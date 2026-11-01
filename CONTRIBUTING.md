# Contributing

Use Python 3.10+ and a virtual environment. Install from source with
`python -m pip install .`, then run `python -m unittest discover -s tests -v`.
The standard invocation reports two skipped external-video tests. To execute all
28 tests with a separately obtained/licensed FFmpeg **7.x**:

```sh
SPRITEKEY_TEST_FFMPEG=/absolute/path/to/ffmpeg python -m unittest discover -s tests -v
```

PowerShell: set `$env:SPRITEKEY_TEST_FFMPEG` to the executable path, then run the
same Python unittest command. No FFmpeg executable is bundled or downloaded by CI.

Please report OS, Python/dependency versions, screen type, configuration, expected
behavior and the exact error. Prefer original geometric reproducers. Before
sharing a manifest or log, inspect source/mask/output paths, filenames and any
FFmpeg command for private information; include only media you have permission
to share. Do not upload account tokens or confidential clips.

For an algorithm change, add a meaningful known-alpha/known-color fixture and
compare real alpha composites on dark/light backgrounds. Distinguish matte,
foreground RGB, explicit preservation and timing changes. Do not weaken existing
assertions to make a regression pass. Maintain straight RGBA8 and zero RGB at
alpha zero, except that only nonzero-alpha preservation pixels override output.

After intentional source edits, regenerate `SOURCE-SHA256.json` with the same
sorted file whitelist and SHA256 schema; do not change the inventory to hide an
unexplained mismatch. Build products, virtual environments, demo runs and caches
are excluded. `python scripts/verify_source.py` checks the published inventory.
The wheel-installed resources retain documentation and license notices.
