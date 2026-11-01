"""Transactional output completion and per-frame provenance."""
from pathlib import Path
import importlib.metadata
import json
import platform
import numpy as np
from PIL import Image
from . import __version__
from .config import read_config
from .keyer import extract
from .media import digest, pngs, load_png, png_timing, decode_video
from .preview import write_preview

def code_fingerprint():
    root = Path(__file__).parent
    files = sorted(p for p in root.rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    return {str(p.relative_to(root)): digest(p) for p in files}

def run(config_path, ffmpeg=None):
    config_path = Path(config_path).resolve(strict=True)
    config_hash = digest(config_path)
    config, config_path = read_config(config_path)
    if digest(config_path) != config_hash:
        raise ValueError("config changed during reading")
    out = Path(config["output"])
    out.mkdir(parents=True, exist_ok=False)
    marker = out / "INCOMPLETE"
    marker.write_text("Processing has not completed. No final manifest is available.\n", encoding="utf-8")
    try:
        return _process(config, config_path, config_hash, ffmpeg, out, marker)
    except Exception as exc:
        marker.write_text(f"INCOMPLETE: {type(exc).__name__}: {exc}\n", encoding="utf-8")
        raise

def _process(config, config_path, config_hash, ffmpeg, out, marker):
    evidence = None
    source_video = None
    if "input_video" in config:
        source_video = {"path": config["input_video"], "sha256": digest(config["input_video"])}
        frames, pts, durations, evidence = decode_video(Path(config["input_video"]), out / "decoded", ffmpeg)
        timing = "KNOWN"
    else:
        frames = pngs(config["input_dir"])
        timing, pts, durations = png_timing(config, len(frames))
    masks = {}
    all_inputs = list(frames)
    for key in ("core_masks", "preserve_rgba"):
        if key in config:
            candidates = pngs(config[key])
            if {p.name for p in candidates} != {p.name for p in frames}:
                raise ValueError(f"{key} must have exactly the source frame PNG names")
            masks[key] = {p.name:p for p in candidates}
            all_inputs += candidates
    inodes = [(p.stat().st_dev,p.stat().st_ino) for p in all_inputs]
    if len(inodes) != len(set(inodes)):
        raise ValueError("input and mask files overlap through hard links")
    hashes = {str(p):digest(p) for p in all_inputs}
    frame_out = out / "frames"
    frame_out.mkdir()
    entries, rendered = [], []
    dimensions = None
    for index, frame in enumerate(frames):
        rgb = load_png(frame, "RGB")
        if dimensions is None:
            dimensions = rgb.shape[:2]
        if rgb.shape[:2] != dimensions:
            raise ValueError("source dimensions change")
        inputs = {}
        mask_arrays = {}
        for key, mode in (("core_masks", "L"), ("preserve_rgba", "RGBA")):
            if key in masks:
                p = masks[key][frame.name]
                arr = load_png(p, mode)
                if arr.shape[:2] != dimensions:
                    raise ValueError(f"{key} dimensions differ from source")
                mask_arrays[key] = arr
                inputs[key] = {"path":str(p), "sha256":hashes[str(p)]}
        rgba, stats = extract(rgb, config["screen"], config["background_roi"], config["settings"],
                              mask_arrays.get("core_masks"), mask_arrays.get("preserve_rgba"))
        destination = frame_out / f"{index+1:08d}.png"
        Image.fromarray(rgba).save(destination)
        entry = {"index":index, "source":{"path":str(frame), "sha256":hashes[str(frame)]},
            "result":{"path":str(destination.relative_to(out)), "sha256":digest(destination)},
            "pts_seconds":str(pts[index]) if pts[index] is not None else None,
            "duration_seconds":str(durations[index]) if durations[index] is not None else None,
            "masks":inputs, "analysis":stats}
        if evidence:
            entry["pts_integer"] = evidence["pts_integer"][index]
            entry["time_base"] = evidence["time_base"]
            entry["reported_duration_integer"] = evidence["reported_duration_integer"][index]
        entries.append(entry)
        rendered.append(destination)
    write_preview(out / "preview.html", rendered, durations)
    for p in all_inputs:
        if digest(p) != hashes[str(p)]:
            raise ValueError("input changed during processing")
    if source_video and digest(source_video["path"]) != source_video["sha256"]:
        raise ValueError("source video changed during processing")
    if digest(config_path) != config_hash:
        raise ValueError("config changed during processing")
    dependencies = {}
    for name in ("numpy", "Pillow", "opencv-python-headless", "opencv-python"):
        try:
            dependencies[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            pass
    manifest = {"schema":"spritekey-manifest-1", "version":__version__, "status":"COMPLETE",
        "pixel_format":"straight RGBA8; transparent RGB zero except nonzero-alpha preservation",
        "width":dimensions[1], "height":dimensions[0], "frame_count":len(entries),
        "config_path":str(config_path), "config_sha256":config_hash, "config":config,
        "timing_status":timing, "source_video":source_video, "ffmpeg":evidence,
        "dependencies":dependencies, "python":platform.python_version(),
        "code_sha256":code_fingerprint(), "frames":entries,
        "total_duration_seconds":str(sum(durations)) if timing == "KNOWN" else None,
        "preview_sha256":digest(out / "preview.html")}
    temporary = out / "manifest.json.partial"
    temporary.write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    marker.unlink()
    temporary.rename(out / "manifest.json")
    return manifest
