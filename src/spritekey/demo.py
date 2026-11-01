"""Generate original geometry and known alpha without reading any image."""
import argparse
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw
import cv2

def generate(destination, screen="green"):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    for name in ("input", "truth", "core"):
        (destination/name).mkdir()
    scale, width, height = 4, 192, 128
    background = np.array([24,220,38] if screen == "green" else [25,38,225], dtype=np.float32)
    for step, name in enumerate(("frame1.png", "frame2.png", "frame10.png")):
        im = Image.new("RGBA", (width*scale,height*scale))
        draw = ImageDraw.Draw(im)
        x = 60+step*3
        def box(values):
            return tuple(round(v*scale) for v in values)
        draw.ellipse(box((x-22,26,x+22,72)), fill=(200,85,40,255))
        draw.polygon([box((x-20,65)),box((x+22,65)),box((x+31,113)),box((x-31,113))], fill=(34,45,110,255))
        draw.rectangle(box((x+17,65,x+68,68)), fill=(220,225,235,255))
        draw.line([box((x+65,68)),box((x+94,38))],fill=(250,230,150,255),width=scale)
        draw.line([box((x-22,74)),box((x-43,86))],fill=(40,160,185,255),width=scale)
        draw.ellipse(box((139,92,143,96)),fill=(170,90,200,255))
        draw.ellipse(box((121,15,132,26)),fill=(210,50,150,128))
        im = im.resize((width,height), Image.Resampling.LANCZOS)
        truth = np.array(im)
        alpha = truth[:,:,3:4].astype(np.float32)/255
        composite = np.rint(truth[:,:,:3]*alpha + background*(1-alpha)).astype(np.uint8)
        Image.fromarray(composite).save(destination/"input"/name)
        im.save(destination/"truth"/name)
        core = cv2.erode((truth[:,:,3]>=254).astype(np.uint8)*255, np.ones((3,3),np.uint8))
        Image.fromarray(core).save(destination/"core"/name)
    config = {"input_dir":"input", "output":"output", "screen":screen,
              "background_roi":[0,0,12,12], "fps":"12/1", "core_masks":"core"}
    (destination/"config.json").write_text(json.dumps(config,indent=2)+"\n",encoding="utf-8")
    return destination/"config.json"

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination")
    parser.add_argument("--screen",choices=("green","blue"),default="green")
    args = parser.parse_args()
    print(generate(args.destination,args.screen))

if __name__ == "__main__":
    main()
