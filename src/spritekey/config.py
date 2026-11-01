"""Strict configuration validation; no implicit timing assumptions."""
from fractions import Fraction
from pathlib import Path
import json
import math

TOP = {"input_video", "input_dir", "output", "screen", "background_roi", "fps",
       "pts_seconds", "last_duration_seconds", "core_masks", "preserve_rgba", "settings"}
DEFAULTS = {"background_tolerance": 0.025, "roi_max_deviation": 0.10,
            "edge_search_radius": 16.0, "core_threshold": 240,
            "core_background_guard": 0.08, "alpha_floor": 0.004,
            "edge_fit_tolerance": 0.06, "edge_spatial_weight": 0.001,
            "seed_color_variation": 0.02,
            "edge_despill_strength": 0.85, "edge_despill_width": 2.5,
            "edge_despill_balance": None, "spill_allowance": 3/255,
            "material_protection_radius": 16.0, "material_protection_tolerance": 0.08}

def rational(value, label, positive=False):
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise ValueError(f"{label} must be an integer or rational/decimal string")
    try:
        result = Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError(f"invalid {label}") from exc
    if positive and result <= 0:
        raise ValueError(f"{label} must be positive")
    return result

def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result

def read_config(path):
    path = Path(path).resolve(strict=True)
    with path.open(encoding="utf-8") as f:
        data = json.load(f, object_pairs_hook=no_duplicates)
    if not isinstance(data, dict):
        raise ValueError("config must be an object")
    unknown = set(data) - TOP
    if unknown:
        raise ValueError(f"unknown options: {sorted(unknown)}")
    if ("input_video" in data) == ("input_dir" in data):
        raise ValueError("supply exactly one of input_video/input_dir")
    for required in ("output", "screen", "background_roi"):
        if required not in data:
            raise ValueError(f"missing {required}")
    if data["screen"] not in ("green", "blue"):
        raise ValueError("screen must be green or blue")
    roi = data["background_roi"]
    if not isinstance(roi, list) or len(roi) != 4 or any(type(x) is not int for x in roi):
        raise ValueError("background_roi must contain four integer pixel boundaries")
    if not (0 <= roi[0] < roi[2] and 0 <= roi[1] < roi[3]):
        raise ValueError("invalid background_roi")
    settings = data.get("settings", {})
    if not isinstance(settings, dict) or set(settings) - set(DEFAULTS):
        raise ValueError("unknown or invalid settings")
    settings = {**DEFAULTS, **settings}
    for key, value in settings.items():
        if key=="edge_despill_balance" and value is None:
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(f"invalid setting {key}")
    for key in ("background_tolerance", "roi_max_deviation", "core_background_guard", "alpha_floor"):
        if not 0 <= settings[key] < 1:
            raise ValueError(f"{key} outside [0,1)")
    if not 0 <= settings["edge_search_radius"] <= 256:
        raise ValueError("edge_search_radius outside [0,256]")
    if not 0 < settings["edge_fit_tolerance"] <= 1:
        raise ValueError("edge_fit_tolerance outside (0,1]")
    if not 0 <= settings["edge_spatial_weight"] <= 1:
        raise ValueError("edge_spatial_weight outside [0,1]")
    if not 0 <= settings["seed_color_variation"] <= 1:
        raise ValueError("seed_color_variation outside [0,1]")
    for key in ("edge_despill_strength","spill_allowance","material_protection_tolerance"):
        if not 0<=settings[key]<=1:raise ValueError(f"{key} outside [0,1]")
    for key in ("edge_despill_width","material_protection_radius"):
        if not 0<=settings[key]<=256:raise ValueError(f"{key} outside [0,256]")
    if settings["edge_despill_balance"] is None:
        settings["edge_despill_balance"]=0.0 if data["screen"]=="blue" else 0.5
    elif not 0<=settings["edge_despill_balance"]<=1:
        raise ValueError("edge_despill_balance outside [0,1]")
    if type(settings["core_threshold"]) is not int or not 1 <= settings["core_threshold"] <= 255:
        raise ValueError("core_threshold must be integer in [1,255]")
    data["settings"] = settings
    if "input_video" in data and any(k in data for k in ("fps", "pts_seconds", "last_duration_seconds")):
        raise ValueError("video timing overrides are prohibited")
    if "fps" in data and any(k in data for k in ("pts_seconds", "last_duration_seconds")):
        raise ValueError("fps and explicit timestamps are mutually exclusive")
    if ("pts_seconds" in data) != ("last_duration_seconds" in data):
        raise ValueError("explicit timing needs pts_seconds and last_duration_seconds")
    for key in ("input_video", "input_dir", "output", "core_masks", "preserve_rgba"):
        if key in data:
            if not isinstance(data[key], str) or not data[key]:
                raise ValueError(f"{key} must be a nonempty path")
            data[key] = str((path.parent / data[key]).resolve())
    paths = [(k, Path(data[k])) for k in ("input_video", "input_dir", "output", "core_masks", "preserve_rgba") if k in data]
    for i, (ka, a) in enumerate(paths):
        for kb, b in paths[i+1:]:
            if a == b or a in b.parents or b in a.parents:
                raise ValueError(f"overlapping paths: {ka}, {kb}")
    out = Path(data["output"])
    if out.exists():
        raise ValueError("output must be a new directory")
    for key, p in paths:
        if key == "output":
            continue
        if not p.exists() or (key == "input_video" and not p.is_file()) or (key != "input_video" and not p.is_dir()):
            raise ValueError(f"invalid path for {key}")
    return data, path
