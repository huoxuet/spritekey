# Source map

The 0.3/0.3.1 implementation was independently written under the historical scope
recorded in AUTHORSHIP.md. Version 0.4 intentionally adapts the user-authorized
MIT 0.2 final RGB opponent-channel cleanup; it is not claimed to have avoided
earlier source. Its matting/IO base is this author's 0.3.1 R2 implementation.
The MIT license text is a standard license text, not an original algorithm.

| Files | Public concepts / APIs used |
|---|---|
| `pyproject.toml`, `MANIFEST.in` | Python project/build metadata, setuptools packaging conventions |
| `.gitignore` | Own build/cache exclusions |
| `LICENSE` | Standard MIT permission text; SpriteKey contributors copyright line |
| `README.md`, `AUTHORSHIP.md`, `SOURCES.md` | This task's implementation, access facts and command examples |
| `THIRD_PARTY_NOTICES.md` | Installed distribution metadata; dependency owners' license identifiers and URLs |
| `src/spritekey/__init__.py` | Python package version constant |
| `src/spritekey/config.py` | Python json/pathlib/fractions; original strict validation rules |
| `src/spritekey/media.py` | PNG IHDR structure, Pillow Image API and transparency metadata, NumPy array API, Python hashlib/subprocess/fractions/re; observed FFmpeg showinfo CLI |
| `src/spritekey/keyer.py` | Author-owned 0.3.1 R2 matting; optimized bounded/vector candidate computation; authorized MIT 0.2 RGB opponent ceiling/contour stage adapted to normalized RGB; new bounded material-interior guard; public NumPy/OpenCV APIs |
| `src/spritekey/pipeline.py` | Python pathlib/json/importlib.metadata, Pillow saving; original pipeline/provenance structure |
| `src/spritekey/preview.py` | Browser DOM, setTimeout, data URLs, CSS; original local viewer code |
| `src/spritekey/cli.py` | Python argparse API |
| `src/spritekey/demo.py` | Original geometry; Pillow ImageDraw/resize, NumPy compositing, OpenCV erode for generated confidence masks |
| `tests/test_spritekey.py` | Python unittest/tempfile; original generated geometry, known-alpha crossing/color/textured-green fixtures, strength/alpha and material-guard cases; signed alpha, actual composite error and padding invariance |
| `src/spritekey/resources/ALGORITHM.md` | General compositing equation, newly implemented algorithm and actual limitations |
| `src/spritekey/resources/example-png.json`, `example-video.json` | Newly authored configurations |
| Installed documentation / LICENSE | README.md is the detailed docs/USAGE.md guide; Chinese/source/provenance/license notices reproduce the corresponding root documents |
| `SOURCE-SHA256.json` | Generated integrity hashes for this new tree, excluding itself and generated build/install/cache output |

The successful public API document URLs and unsuccessful access attempts are
recorded in `AUTHORSHIP.md`. Detailed private access ledgers, calibration media
and build/install scratch directories are excluded from the distributable source.
No dependency binary, model, external sample implementation, game picture,
complete historical tool package or FFmpeg executable is included. The authorized
adapted 0.2 color-stage arithmetic is included as documented below.

The inherited source is archived 0.2 `src/spritekey/core.py`, SHA256
`60bb155f3b05329d034332fad905de2c825983c4c01c6413a09be2642e98ecbf`,
in the private 0.2 source archive.
Its ALGORITHM.md/SOURCES.md/LICENSE were read with explicit user authorization.
Only the final opponent-channel RGB cleanup concept/arithmetic was adapted; the
old source file itself, old alpha/haze/CLI machinery and old production scripts
are not bundled. The inherited SpriteKey code uses the same MIT LICENSE and
copyright 2026 SpriteKey contributors. Historical 0.3 creation records remain
historical facts, not a no-old-source claim for 0.4 or a legal guarantee.

Public release additions: English/Chinese README, detailed USAGE, VALIDATION, CONTRIBUTING and CHANGELOG are authored release documentation. scripts/verify_source.py checks this inventory; scripts/check_install.py checks the installed payload and executes the original demo. The pinned official GitHub Actions in .github/workflows/ci.yml are separately executed service dependencies, not vendored implementations. docs/assets/demo.png is composed only from the original generator and this package outputs, under MIT. No production image was used.
