"""Command line entry point."""
import argparse
import sys
from .pipeline import run

def main():
    parser = argparse.ArgumentParser(description="SpriteKey 0.4.0 local screen extraction")
    parser.add_argument("--config", required=True)
    parser.add_argument("--ffmpeg", help="External FFmpeg 7.x executable, required for video")
    args = parser.parse_args()
    try:
        manifest = run(args.config, args.ffmpeg)
    except Exception as exc:
        print(f"SpriteKey: {exc}", file=sys.stderr)
        return 1
    print(f"COMPLETE: {manifest['frame_count']} frames; timing {manifest['timing_status']}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
