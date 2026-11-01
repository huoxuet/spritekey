"""Frame loading, hashes, rational timestamps and external FFmpeg decoding."""
from fractions import Fraction
from pathlib import Path
import hashlib
import re
import subprocess
import struct
import numpy as np
from PIL import Image
from .config import rational

def digest(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            result.update(chunk)
    return result.hexdigest()

def pngs(directory):
    directory = Path(directory)
    files = [p for p in directory.iterdir() if p.suffix.lower() == ".png"]
    if not files:
        raise ValueError(f"no PNG frames: {directory}")
    for p in files:
        if not p.is_file() or p.is_symlink() or p.resolve().parent != directory.resolve():
            raise ValueError(f"PNG must be a regular local file: {p}")
    def key(p):
        return [(1, int(x)) if x.isdigit() else (0, x.casefold()) for x in re.split(r"(\d+)", p.name)]
    return sorted(files, key=lambda p: (key(p), p.name))

def load_png(path, mode):
    with Path(path).open("rb") as f:
        header = f.read(33)
    if len(header) != 33 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError(f"invalid PNG: {path}")
    if header[24] != 8 or header[25] != {"RGB":2, "RGBA":6, "L":0}[mode]:
        raise ValueError(f"PNG must be {mode} 8-bit: {path}")
    with Image.open(path) as im:
        if im.mode != mode or getattr(im, "n_frames", 1) != 1:
            raise ValueError(f"expected static {mode} PNG: {path}")
        if mode == "RGB" and "transparency" in im.info:
            raise ValueError(f"RGB source PNG must not contain transparency metadata: {path}")
        return np.array(im)

def png_timing(config, count):
    if "fps" in config:
        fps = rational(config["fps"], "fps", True)
        return "KNOWN", [Fraction(i, 1)/fps for i in range(count)], [1/fps]*count
    if "pts_seconds" in config:
        values = config["pts_seconds"]
        if not isinstance(values, list) or len(values) != count:
            raise ValueError("pts_seconds length must equal frame count")
        pts = [rational(x, "pts_seconds") for x in values]
        durations = [b-a for a,b in zip(pts, pts[1:])]
        if any(x <= 0 for x in durations):
            raise ValueError("timestamps must be strictly increasing")
        durations.append(rational(config["last_duration_seconds"], "last_duration_seconds", True))
        return "KNOWN", pts, durations
    return "UNKNOWN", [None]*count, [None]*count

def decode_video(source, directory, executable):
    if executable is None:
        raise ValueError("video requires --ffmpeg with an external FFmpeg 7 executable")
    executable = str(Path(executable).resolve(strict=True))
    version = subprocess.run([executable, "-version"], capture_output=True, text=True, check=True).stdout.splitlines()[0]
    if not re.search(r"ffmpeg version (?:n)?7\.", version):
        raise ValueError("this release requires FFmpeg 7.x")
    directory.mkdir()
    command = [executable, "-hide_banner", "-nostdin", "-nostats", "-n", "-copyts",
               "-noautorotate", "-i", str(source), "-map", "0:v:0", "-an", "-sn", "-dn",
               "-vf", "showinfo", "-fps_mode", "passthrough", "-pix_fmt", "rgb24",
               "-start_number", "1", str(directory / "%08d.png")]
    completed = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    (directory.parent / "ffmpeg-decode.log").write_text(completed.stderr, encoding="utf-8")
    if completed.returncode:
        raise ValueError("FFmpeg failed; inspect ffmpeg-decode.log")
    bases = re.findall(r"config in time_base:\s*(\d+/\d+)", completed.stderr)
    if not bases or len(set(bases)) != 1:
        raise ValueError("missing or changing video time base")
    base = rational(bases[0], "time base", True)
    rows = re.findall(r"\bn:\s*(\d+)\s+pts:\s*(-?\d+)\s+pts_time:\S+\s+duration:\s*(\d+)\s+duration_time:\S+.*?\bs:(\d+)x(\d+)", completed.stderr)
    frames = pngs(directory)
    if len(rows) != len(frames) or not rows:
        raise ValueError("incomplete integer PTS/duration evidence")
    pts, reported, dimensions = [], [], set()
    for expected, row in enumerate(rows):
        n, p, d, w, h = map(int, row)
        if n != expected or d <= 0:
            raise ValueError("unreliable video frame sequence/duration")
        pts.append(p*base)
        reported.append(d*base)
        dimensions.add((w,h))
    if len(dimensions) != 1 or any(b <= a for a,b in zip(pts, pts[1:])):
        raise ValueError("variable dimensions or non-increasing PTS")
    if re.search(r"non[- ]monoton|corrupt|invalid|error while decoding", completed.stderr, re.I):
        raise ValueError("FFmpeg reported unreliable decoding/timing")
    durations = [b-a for a,b in zip(pts, pts[1:])] + [reported[-1]]
    return frames, pts, durations, {"version": version, "command": command,
        "time_base": str(base), "pts_integer": [int(row[1]) for row in rows],
        "reported_duration_integer": [int(row[2]) for row in rows]}
