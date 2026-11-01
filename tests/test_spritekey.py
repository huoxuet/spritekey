"""Independent generated fixtures: no game assets or older implementation."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import numpy as np
from PIL import Image,ImageDraw
from spritekey.config import read_config, DEFAULTS
from spritekey.demo import generate
from spritekey.keyer import extract
from spritekey.media import png_timing, load_png
from spritekey.pipeline import run

def crossing_fixture(noise=False):
    """Original known-alpha white strands crossed by two dark thin structures."""
    width,height,scale=128,96,8
    hair=Image.new('RGBA',(width*scale,height*scale))
    draw=ImageDraw.Draw(hair)
    for x in (60,67,75,84,94):
        draw.line([(x*scale,8*scale),((x+4)*scale,88*scale)],fill=(224,218,211,255),width=2*scale)
    lines=Image.new('RGBA',hair.size)
    draw=ImageDraw.Draw(lines)
    draw.line([(23*scale,18*scale),(116*scale,77*scale)],fill=(87,43,26,255),width=scale)
    draw.line([(23*scale,36*scale),(116*scale,36*scale)],fill=(105,54,29,255),width=scale)
    draw.ellipse((20*scale,15*scale,27*scale,22*scale),fill=(87,43,26,255))
    truth=Image.alpha_composite(hair,lines).resize((width,height),Image.Resampling.LANCZOS)
    line_alpha=np.array(lines.resize((width,height),Image.Resampling.LANCZOS))[:,:,3]
    rgba=np.array(truth);a=rgba[:,:,3:4].astype(np.float32)/255
    background=np.array([24,46,249],np.float32)
    source=np.rint(rgba[:,:,:3]*a+background*(1-a)).astype(np.uint8)
    if noise:
        perturb=np.random.default_rng(813).integers(-2,3,source.shape,dtype=np.int16)
        source=np.clip(source.astype(np.int16)+perturb,0,255).astype(np.uint8)
    return source,rgba,line_alpha

def textured_green_fixture():
    """Known-alpha warm texture with no locally smooth opaque color reference."""
    y,x=np.indices((40,48))
    tone=np.where((x+y)%2==0,1,-1)
    foreground=np.full((40,48,3),[150,80,50],np.float32)
    foreground+=tone[:,:,None]*np.array([20,15,5])
    alpha=np.zeros((40,48),np.float32)
    alpha[8:30,10:25]=1
    alpha[8:30,25:29]=[.25,.4,.55,.65]
    background=np.array([28,255,15],np.float32)
    source=np.rint(foreground*alpha[:,:,None]+background*(1-alpha[:,:,None])).astype(np.uint8)
    return source,foreground,alpha

class SpriteKeyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.config = generate(self.root/"demo")

    def tearDown(self):
        self.tmp.cleanup()

    def rewrite(self, **changes):
        data=json.loads(self.config.read_text())
        data.update(changes)
        self.config.write_text(json.dumps(data))

    def test_demo_sequence_and_provenance(self):
        m=run(self.config)
        self.assertEqual(m["frame_count"],3)
        self.assertEqual([Path(f["source"]["path"]).name for f in m["frames"]],
                         ["frame1.png","frame2.png","frame10.png"])
        self.assertEqual(m["total_duration_seconds"],"1/4")
        self.assertEqual(m["width"],192)
        out=self.config.parent/"output"
        self.assertFalse((out/"INCOMPLETE").exists())
        self.assertTrue((out/"manifest.json").exists())
        self.assertIn("data:image/png;base64,",(out/"preview.html").read_text())
        for row in m["frames"]:
            actual=load_png(out/row["result"]["path"],"RGBA")
            src=load_png(row["source"]["path"],"RGB")
            core=load_png(row["masks"]["core_masks"]["path"],"L")>=240
            self.assertTrue(np.array_equal(actual[core,:3],src[core]))
            self.assertTrue(np.all(actual[core,3]==255))
            self.assertTrue(np.all(actual[actual[:,:,3]==0,:3]==0))
        with self.assertRaisesRegex(ValueError,"new directory"):
            run(self.config)

    def test_unknown_settings_and_duplicates_rejected(self):
        self.rewrite(settings={"mystery":1})
        with self.assertRaisesRegex(ValueError,"settings"):
            read_config(self.config)
        self.config.write_text('{"screen":"green","screen":"blue"}')
        with self.assertRaisesRegex(ValueError,"duplicate"):
            read_config(self.config)

    def test_unknown_timing_and_exact_vfr(self):
        status,p,d=png_timing({},3)
        self.assertEqual(status,"UNKNOWN")
        self.assertEqual(p,[None]*3)
        status,p,d=png_timing({"pts_seconds":["7/3","5/2","3"],"last_duration_seconds":"1/7"},3)
        self.assertEqual([str(x) for x in d],["1/6","1/2","1/7"])
        for config in ({"fps":"0"},{"pts_seconds":["0","0"],"last_duration_seconds":"1"}):
            with self.assertRaises(ValueError):
                png_timing(config,2)

    def test_overlap_and_video_override(self):
        self.rewrite(output="input/subdir")
        with self.assertRaisesRegex(ValueError,"overlapping"):
            read_config(self.config)
        data=json.loads(self.config.read_text())
        data.pop("input_dir")
        data["input_video"]="some.mp4"
        self.config.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError,"overrides"):
            read_config(self.config)

    def test_failure_leaves_marker_no_manifest(self):
        frame=self.config.parent/"input"/"frame2.png"
        Image.new("RGB",(32,32),(0,255,0)).save(frame)
        with self.assertRaisesRegex(ValueError,"dimensions"):
            run(self.config)
        out=self.config.parent/"output"
        self.assertTrue((out/"INCOMPLETE").exists())
        self.assertFalse((out/"manifest.json").exists())

    def test_equation_soft_edge_and_tiny_line(self):
        b=np.array([0,255,0],np.float32)
        c=np.tile(b.astype(np.uint8),(20,40,1))
        c[8:12,10:15]=[240,80,40]
        c[8:12,15]=[120,168,20] # approximately half alpha
        c[15,30:36]=[230,230,240] # isolated thin line must remain
        rgba,_=extract(c,"green",[0,0,3,3],DEFAULTS)
        self.assertTrue(np.all(rgba[15,30:36,3]==255))
        self.assertTrue(np.all(np.abs(rgba[8:12,15,3].astype(int)-128)<3))
        self.assertTrue(np.all(np.abs(rgba[8:12,15,:3].astype(int)-[240,80,40])<4))

    def test_preserve_exact_and_core_guard(self):
        rgb=np.full((10,10,3),[0,255,0],np.uint8)
        rgb[5,5]=[255,0,0]
        core=np.full((10,10),255,np.uint8)
        preserve=np.zeros((10,10,4),np.uint8)
        preserve[2,3]=[17,201,36,71]
        rgba,stats=extract(rgb,"green",[0,0,2,2],DEFAULTS,core,preserve)
        self.assertEqual(stats["core_rejected_background_pixels"],99)
        self.assertEqual(rgba[5,5].tolist(),[255,0,0,255])
        self.assertEqual(rgba[2,3].tolist(),[17,201,36,71])
        self.assertEqual(rgba[0,0].tolist(),[0,0,0,0])

    def test_codec_screen_variation_not_opaque_seed(self):
        for screen,b,noise in [('green',[30,255,16],[0,252,15]),('blue',[24,46,249],[26,55,255])]:
            rgb=np.full((12,12,3),b,np.uint8)
            rgb[6,5]=[85,60,45]
            rgb[6,6]=noise
            rgba,_=extract(rgb,screen,[0,0,2,2],DEFAULTS)
            self.assertLess(int(rgba[6,6,3]),32)

    def test_true_screen_color_core_and_partial_thin_line(self):
        rgb=np.full((15,30,3),[0,255,0],np.uint8)
        rgb[7,15:20]=[128,255,128]
        rgba,_=extract(rgb,'green',[0,0,2,2],DEFAULTS)
        self.assertTrue(np.all(np.abs(rgba[7,15:20,3].astype(int)-128)<=1))
        self.assertTrue(np.all(rgba[7,15:20,:3]>=250))
        rgb[10,15]=[20,160,40]
        core=np.zeros((15,30),np.uint8);core[10,15]=255
        rgba,_=extract(rgb,'green',[0,0,2,2],DEFAULTS,core)
        self.assertEqual(rgba[10,15].tolist(),[20,160,40,255])

    def test_white_strands_crossed_by_dark_thin_structures(self):
        for noisy in (False,True):
            with self.subTest(noisy=noisy):
                source,truth,line_alpha=crossing_fixture(noisy)
                result,_=extract(source,'blue',[0,0,12,12],DEFAULTS)
                dark_line=(line_alpha>100)&(truth[:,:,:3].mean(axis=2)<140)
                # Known dark structure must stay present and dark, including
                # its mixed pixels on white strands, not be whitened or erased.
                self.assertTrue(np.all(result[:,:,3][dark_line]>=truth[:,:,3][dark_line]*0.85))
                error=np.abs(result[:,:,:3].astype(float)-truth[:,:,:3])[dark_line]
                self.assertLess(float(error.mean()),22)
                self.assertFalse(np.any((result[:,:,:3].mean(axis=2)>170)&dark_line))
                self.assertTrue(np.all(result[result[:,:,3]==0,:3]==0))

    def test_multicolor_soft_boundaries_with_sample_noise(self):
        colors=np.array([[230,220,210],[190,50,40],[220,180,50],[50,170,70],[190,70,150]],np.float32)
        foreground=np.zeros((50,96,3),np.float32)
        truth_alpha=np.zeros((50,96),np.float32)
        for row,color in enumerate(colors):
            y=8+row*8
            foreground[y:y+5,45:90]=color
            truth_alpha[y:y+5,45:65]=np.linspace(.15,1,20)
            truth_alpha[y:y+5,65:90]=1
        background=np.array([24,46,249],np.float32)
        c=foreground*truth_alpha[:,:,None]+background*(1-truth_alpha[:,:,None])
        noise=np.random.default_rng(901).integers(-2,3,c.shape)
        source=np.clip(np.rint(c)+noise,0,255).astype(np.uint8)
        result,_=extract(source,'blue',[0,0,12,6],DEFAULTS)
        # Check moderate soft coverage with opaque references in search range.
        # Nearly opaque key-opposed colors are intrinsically ambiguous from one
        # RGB observation and are separately covered by core/preserve contracts.
        supported=(truth_alpha>.2)&(truth_alpha<.6)&(np.indices(truth_alpha.shape)[1]>=51)
        self.assertLess(float(np.abs(result[:,:,3].astype(float)/255-truth_alpha)[supported].mean()),.09)
        self.assertLess(float(np.abs(result[:,:,:3].astype(float)-foreground)[supported].mean()),20)

    def test_true_green_purple_material_and_authoritative_overrides(self):
        for screen,b in [('green',[0,255,0]),('blue',[24,46,249])]:
            source=np.full((20,24,3),b,np.uint8)
            source[8:11,9:12]=[35,170,65]
            source[12:15,9:12]=[160,40,150]
            core=np.zeros((20,24),np.uint8);core[8:15,9:12]=255
            preserve=np.zeros((20,24,4),np.uint8);preserve[10,10]=[28,230,187,47]
            result,_=extract(source,screen,[0,0,4,4],DEFAULTS,core,preserve)
            self.assertEqual(result[8,9].tolist(),[35,170,65,255])
            self.assertEqual(result[12,9].tolist(),[160,40,150,255])
            self.assertEqual(result[10,10].tolist(),[28,230,187,47])

    def test_textured_green_soft_boundary_alpha_color_and_composites(self):
        source,foreground,truth_alpha=textured_green_fixture()
        result,_=extract(source,'green',[0,0,6,6],DEFAULTS)
        soft=(truth_alpha>0)&(truth_alpha<1)
        alpha=result[:,:,3].astype(float)/255
        delta=(alpha-truth_alpha)[soft]
        # Both over-coverage and under-coverage fail. Nonzero support alone
        # would miss the olive fringe regression caused by inflated alpha.
        self.assertGreaterEqual(float(delta.min()),-.025)
        self.assertLessEqual(float(delta.max()),.025)
        self.assertLess(float(np.abs(result[:,:,:3].astype(float)-foreground)[soft].mean()),4)
        for background in (28,240):
            expected=foreground*truth_alpha[:,:,None]+background*(1-truth_alpha[:,:,None])
            actual=result[:,:,:3]*alpha[:,:,None]+background*(1-alpha[:,:,None])
            error=(actual-expected)[soft]
            self.assertLess(float(np.abs(error).mean()),1.5)
            self.assertGreaterEqual(float(error.min()),-3)
            self.assertLessEqual(float(error.max()),3)

    def test_candidate_setting_ranges_rejected(self):
        for changes in ({'edge_fit_tolerance':0},{'edge_fit_tolerance':1.1},{'edge_spatial_weight':-0.1},{'seed_color_variation':-0.1}):
            self.rewrite(settings=changes)
            with self.assertRaises(ValueError):read_config(self.config)

    def test_despill_strength_changes_rgb_only(self):
        source=np.full((32,48,3),[24,46,249],np.uint8)
        source[14:17,8:40]=[140,80,125]
        outputs=[extract(source,'blue',[0,0,5,5],{**DEFAULTS,'edge_despill_strength':s})[0]
                 for s in (0,.25,.85,1)]
        for out in outputs:self.assertTrue(np.array_equal(out[:,:,3],outputs[0][:,:,3]))
        self.assertGreater(int(outputs[0][15,22,2]),int(outputs[2][15,22,2]))
        self.assertGreaterEqual(int(outputs[1][15,22,2]),int(outputs[2][15,22,2]))
        self.assertGreaterEqual(int(outputs[2][15,22,2]),int(outputs[3][15,22,2]))
        self.assertTrue(np.array_equal(outputs[0][:,:,:2],outputs[3][:,:,:2]))

    def test_purple_material_interior_match_is_not_blanket_purple_skip(self):
        source=np.full((36,48,3),[24,46,249],np.uint8)
        source[5:23,7:25]=[160,40,150] # known authentic broad purple material
        source[28:30,7:40]=[140,80,125] # narrow contaminated structure, different RGB
        result,_=extract(source,'blue',[0,0,4,4],DEFAULTS)
        self.assertTrue(np.all(result[5:23,7:25,:3]==[160,40,150]))
        self.assertLess(int(result[28,15,2]),125)
        self.assertEqual(int(result[28,15,3]),255)

    def test_green_material_color_preserved_by_matching_interior(self):
        source=np.full((32,40,3),[24,46,249],np.uint8)
        source[6:26,8:30]=[35,170,65]
        result,_=extract(source,'blue',[0,0,4,4],DEFAULTS)
        self.assertTrue(np.all(result[6:26,8:30,:3]==[35,170,65]))
        self.assertTrue(np.all(result[6:26,8:30,3]==255))

    def test_strength_sweep_keeps_authoritative_layers_and_source(self):
        source=np.full((20,24,3),[0,255,0],np.uint8)
        source[8:12,9:15]=[35,170,65]
        before=source.copy()
        core=np.zeros((20,24),np.uint8);core[8:12,9:15]=255
        preserve=np.zeros((20,24,4),np.uint8);preserve[10,10]=[71,190,230,47]
        for strength in (0,.25,.85,1):
            result,_=extract(source,'green',[0,0,4,4],{**DEFAULTS,'edge_despill_strength':strength},core,preserve)
            self.assertEqual(result[8,9].tolist(),[35,170,65,255])
            self.assertEqual(result[10,10].tolist(),[71,190,230,47])
            self.assertTrue(np.array_equal(source,before))

    def test_despill_screen_defaults_and_invalid_settings(self):
        self.rewrite(screen='blue',settings={})
        settings=read_config(self.config)[0]['settings']
        self.assertEqual(settings['edge_despill_balance'],0)
        self.rewrite(screen='green',settings={})
        self.assertEqual(read_config(self.config)[0]['settings']['edge_despill_balance'],.5)
        for changes in ({'edge_despill_strength':-1},{'edge_despill_width':-1},
                        {'edge_despill_balance':'blue'},{'spill_allowance':2},
                        {'material_protection_radius':-1},{'material_protection_tolerance':None}):
            self.rewrite(settings=changes)
            with self.assertRaises(ValueError):read_config(self.config)

    def test_bounded_query_is_invariant_under_empty_canvas_padding(self):
        source,_,_=textured_green_fixture()
        settings={**DEFAULTS,'edge_despill_strength':0}
        expected,_=extract(source,'green',[0,0,6,6],settings)
        expanded=np.full((110,135,3),[28,255,15],np.uint8)
        expanded[33:73,41:89]=source
        actual,_=extract(expanded,'green',[0,0,6,6],settings)
        self.assertTrue(np.array_equal(expected,actual[33:73,41:89]))

    def test_blue_demo(self):
        config=generate(self.root/"blue","blue")
        self.assertEqual(run(config)["frame_count"],3)

    def test_wrong_mask_mode_and_names(self):
        Image.new("RGB",(192,128)).save(self.config.parent/"core"/"frame1.png")
        with self.assertRaisesRegex(ValueError,"L 8-bit"):
            run(self.config)

    def test_hardlink_mask_overlap_rejected(self):
        target=self.config.parent/"core"/"frame1.png"
        target.unlink()
        os.link(self.config.parent/"input"/"frame1.png",target)
        with self.assertRaisesRegex(ValueError,"hard links"):
            run(self.config)

    def test_input_rgba_not_silently_converted(self):
        target=self.config.parent/"input"/"frame1.png"
        Image.new("RGBA",(192,128),(0,255,0,255)).save(target)
        with self.assertRaisesRegex(ValueError,"RGB 8-bit"):
            run(self.config)

    def test_rgb_transparent_color_refused_by_cli(self):
        target=self.config.parent/"input"/"frame1.png"
        im=Image.new("RGB",(192,128),(0,255,0))
        im.putpixel((60,60),(255,0,0))
        im.save(target,transparency=(255,0,0))
        with Image.open(target) as check:
            self.assertEqual(check.mode,"RGB")
            self.assertEqual(check.convert("RGBA").getpixel((60,60)),(255,0,0,0))
        result=subprocess.run([sys.executable,"-m","spritekey.cli","--config",str(self.config)],
                              capture_output=True,text=True)
        self.assertEqual(result.returncode,1)
        self.assertIn("transparency metadata",result.stderr)
        self.assertNotIn("COMPLETE:",result.stdout)
        out=self.config.parent/"output"
        self.assertTrue((out/"INCOMPLETE").exists())
        self.assertFalse((out/"manifest.json").exists())

    def test_mask_missing_frame_rejected(self):
        (self.config.parent/"core"/"frame2.png").unlink()
        with self.assertRaisesRegex(ValueError,"exactly"):
            run(self.config)

    @unittest.skipUnless(os.environ.get("SPRITEKEY_TEST_FFMPEG"),"set SPRITEKEY_TEST_FFMPEG for external FFmpeg integration")
    def test_video_pts_and_final_duration(self):
        exe=os.environ["SPRITEKEY_TEST_FFMPEG"]
        video=self.root/"sample.mkv"
        subprocess.run([exe,"-hide_banner","-loglevel","error","-f","lavfi","-i",
                        "color=c=0x18dc26:s=32x32:r=3:d=1","-output_ts_offset","5",
                        "-c:v","ffv1",str(video)],check=True)
        config=self.root/"video.json"
        config.write_text(json.dumps({"input_video":str(video),"output":str(self.root/"video-out"),
                          "screen":"green","background_roi":[0,0,8,8]}))
        m=run(config,exe)
        self.assertEqual(m["frame_count"],3)
        self.assertEqual([f["pts_integer"] for f in m["frames"]],[5000,5333,5667])
        self.assertEqual([f["duration_seconds"] for f in m["frames"]],["333/1000","167/500","333/1000"])
        self.assertEqual(m["frames"][-1]["duration_seconds"],"333/1000")
        self.assertEqual(m["ffmpeg"]["time_base"],"1/1000")

    @unittest.skipUnless(os.environ.get("SPRITEKEY_TEST_FFMPEG"),"set SPRITEKEY_TEST_FFMPEG for external FFmpeg integration")
    def test_video_missing_last_duration_refused(self):
        exe=os.environ["SPRITEKEY_TEST_FFMPEG"]
        video=self.root/"no-last-duration.mkv"
        subprocess.run([exe,"-hide_banner","-loglevel","error","-f","lavfi","-i",
                        "color=c=0x18dc26:s=32x32:r=3:d=1","-vf","setpts=N*N/(3*TB)+5/TB",
                        "-fps_mode","passthrough","-c:v","ffv1",str(video)],check=True)
        config=self.root/"missing-duration.json"
        config.write_text(json.dumps({"input_video":str(video),"output":str(self.root/"refused"),
                          "screen":"green","background_roi":[0,0,8,8]}))
        with self.assertRaisesRegex(ValueError,"duration"):
            run(config,exe)
        self.assertFalse((self.root/"refused"/"manifest.json").exists())
        self.assertTrue((self.root/"refused"/"INCOMPLETE").exists())

if __name__ == "__main__":
    unittest.main()
