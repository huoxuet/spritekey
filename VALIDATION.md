# v0.4.0 validation scope

The public release retains byte-identical Python runtime modules and the original
28 regression tests from the locally reviewed 0.4.0 candidate 1. Release preparation
changes documentation, package metadata and adds public install/integrity/CI checks.
`SOURCE-SHA256.json` inventories this public tree; it is not a signature.

## Local macOS evidence

Python 3.12.14 on macOS arm64, NumPy 2.3.5, Pillow 12.3.0,
opencv-python-headless 4.13.0.92; separately provided FFmpeg 7.1.
The reviewed installed candidate passed all 28 tests including the two external
video tests. Two private clips (194 frames total) retained the 0.3.1 revision 2
alpha bytes exactly while the added cleanup only reduced the screen RGB channel.
Neighboring difficult frames were inspected on light and dark backgrounds.
The clips, their images, private logs and internal review are not distributed.
These checks do not establish universal foreground-color truth or every-frame
human visual acceptance, and they do not validate game integration.

## Fresh public-package installation

A new macOS arm64 Python 3.12.14 virtual environment installed the public wheel
and freshly resolved NumPy 2.5.4, Pillow 13.0.0 and opencv-python-headless
5.0.0.93 from the documented HTTPS Tsinghua PyPI mirror. Default PyPI could not
resolve all required distributions on this network. All 28 installed-package
tests passed, including external FFmpeg 7.1 integration; pip check passed.
This is additional package/regression evidence, not a repeat of manual private-clip
quality/performance checks with those newer dependencies.

## Public CI

The workflow builds and installs the wheel with freshly resolved dependencies,
runs the unchanged regression suite and green/blue original CLI demos, checks
installed module/resource hashes and validates the source inventory. Matrix:
`ubuntu-latest`, `macos-latest`, `windows-latest`, Python 3.10 and 3.12.
The workflow deliberately does not obtain FFmpeg: of 28 discovered regression
tests, 26 execute and two external-video tests are explicitly skipped. CI success
covers PNG/package behavior on the actual runners, not cross-platform video,
manual visual quality, every dependency release, or all supported Python versions.
See the commit-specific Actions results, rather than treating a workflow file as
an executed pass. Python 3.10 is the declared minimum; newer unlisted Python
versions have no matrix evidence in this first release.

## Performance

Computation pruning/vectorization reduces repeated candidate work without changing
the reviewed matte on the checked inputs. Private same-machine single-PNG command
benchmarks (including startup and PNG/preview/manifest IO, excluding video decode)
showed roughly 4.7–5.3x speed ratios versus 0.3.1 revision 2, corroborated by an
independent repeat. Those samples are not a whole-video speed ratio, cross-machine
guarantee or publicly reproducible benchmark dataset. No competitive platform
ranking is claimed. Public regression fixtures are reproducible; private footage
is not provided as benchmark material.
