# Implementation provenance record, 2026-11-01

Current version 0.4.0 intentionally reads/adapts the user-authorized MIT 0.2
color stage. The following 0.3/0.3.1 records describe their historical scope;
they are not a claim that 0.4 was developed without reading earlier source.

This is an engineering record of the sources actually accessed in this
implementation session. It is not a legal opinion, originality certification,
or a guarantee about every possible similarity to other software.
The access statements below are the implementer's account. The integrator retains
the detailed internal tool-call/path ledger separately; it is excluded from this
distributable package. No independent filesystem audit or raw-rollout log path was
obtained; this was not technically enforced isolation.

The implementer received a functional specification: local RGB sequence/video
input, rational timing, straight RGBA extraction, masks, completion provenance,
preview, original geometry demo and installable 0.3.0 packaging. The code was
written in this new directory from that specification and the general equation
`C = a F + (1-a) B`. Algorithm structure, defaults and tests were chosen here.

## Actual access scope

* Source-writing scope was the new implementation tree, plus temporary generated
  fixtures, build artifacts and isolated install targets. Later authorized image
  validation reads are described separately below.
* Inspected metadata/public imports in
  `site-packages/` in an isolated Python 3.12 environment: Python runtime,
  NumPy, Pillow, cv2, their versions and distribution license metadata, setuptools.
  Did not read dependency implementation files.
* Executed
  an externally supplied macOS arm64 FFmpeg 7.1 executable
  for version/public CLI and generated synthetic video decoding. It was not copied
  into this source tree or wheel.
* Initially opened only newly generated geometric images. After the first defaults
  failed visual assessment, the parent explicitly supplied current original RGB
  decoded frames and this new implementation's own results. Opened those two
  difficult frames and their immediate neighbors (six RGB frames total), plus
  the newly generated calibration outputs. They are private validation inputs,
  excluded from distribution. No game image rights are granted here.
* Did not open other-agent-provided tools, historical keying implementations,
  old tool archives or old tool source. Did not inspect the local root AGENTS
  file; applicable boundaries were supplied in the parent task. No old thresholds,
  implementation, source layout or source snippets were used as a target.
* Did not stage, commit, push, publish, change global configuration, access paid
  generation, or download a model.

## Public API references

The browser successfully returned these official public API documentation pages:

* OpenCV 4.13 distance transform / labels semantics:
  https://docs.opencv.org/4.x/d7/d1b/group__imgproc__misc.html
* Pillow Image module / open / save / resize:
  https://pillow.readthedocs.io/en/stable/reference/Image.html
* NumPy `lstsq` public documentation:
  https://numpy.org/doc/stable/reference/generated/numpy.linalg.lstsq.html
  (Consulted initially; the final implementation uses direct dot products rather
  than this solver.)

Attempts to access FFmpeg's `ffmpeg-doc.html` and `ffmpeg-filters.html#showinfo`
timed out. CLI behavior was checked by executing the external FFmpeg 7.1 on
synthetic inputs and parsing its own showinfo records. An attempted OpenCV
connected-components example URL was inaccessible; no contents were used.
For the initial 0.3 work, no public implementation source or sample code was copied. Public API names,
mathematical formulas, package metadata and separately attributed license texts
are not represented as newly invented by SpriteKey.

## Initial authored file inventory and maintained paths

The following files originated in the 0.3 implementation and are maintained in
later versions, with MIT terms for SpriteKey-owned content. The authorized 0.4
adaptation is detailed below. API provenance by group is listed in `SOURCES.md`.

* `pyproject.toml`: project metadata / pure Python build / console entry point.
* `.gitignore`: own generated build/install/cache exclusions.
* `MANIFEST.in`: source distribution inclusion rules.
* `LICENSE`: standard MIT grant, copyright 2026 SpriteKey contributors.
* `README.md`: install, usage, configuration, limits and validation instructions.
* `AUTHORSHIP.md`: this factual provenance record.
* `SOURCES.md`: file-by-file source map.
* `THIRD_PARTY_NOTICES.md`: dependency identities / own licenses; no relicense.
* `tests/test_spritekey.py`: generated-fixture behavioral tests.
* `src/spritekey/__init__.py`: package version.
* `src/spritekey/config.py`: strict JSON / path / option validation.
* `src/spritekey/media.py`: PNG modes, natural order, hashes, timestamps, FFmpeg.
* `src/spritekey/keyer.py`: independently derived matte / candidate color fit / mask logic.
* `src/spritekey/pipeline.py`: output lifecycle, provenance and completion.
* `src/spritekey/preview.py`: self-contained HTML/JS viewer template.
* `src/spritekey/cli.py`: argparse CLI.
* `src/spritekey/demo.py`: original geometric image generator.
* `src/spritekey/resources/ALGORITHM.md`: algorithm explanation and limitations.
* `src/spritekey/resources/example-png.json`: original configuration example.
* `src/spritekey/resources/example-video.json`: original configuration example.

The original resource copies reproduced root documentation and licenses for
installed users. In the public release, the installed README retains the detailed
docs/USAGE.md guide; AUTHORSHIP.md, SOURCES.md, LICENSE and THIRD_PARTY_NOTICES.md
continue to reproduce the corresponding public root documents. Build-generated `.egg-info`, caches, wheel or
source distribution files are generated metadata/artifacts, not additional
third-party source. No game asset is included or licensed by this record.
`SOURCE-SHA256.json` is a generated file-integrity inventory and excludes itself.

## Verification and corrections

The initial defaults passed ten synthetic behavioral tests but produced obvious
screen-colored fringes on supplied real RGB footage. That failure is retained in
the integrator's private validation evidence. Corrected the overstrict gamut
bound and ill-conditioned inverse-color behavior based solely on these newly
authorized RGB inputs and this implementation's own results. Six neighboring
frames were checked as actual alpha composites on light/dark backgrounds; no
whole-video visual acceptance is claimed by this author check. Generated
tests cover mode/path/timing/failure behavior, codec screen deviations, tiny and
partial thin lines, screen-colored core protection and exact RGBA preservation.

An independent reviewer subsequently reported that RGB8 PNG tRNS transparent-color
metadata was accepted while its transparency semantics were discarded. After the
integrator relocated this same source to the canonical directory, the implementer
first checked all 25 source-file hashes against the frozen inventory, then
reproduced the counterexample with an original generated RGB image. Added explicit
RGB transparency-metadata rejection and a CLI regression requiring failure,
INCOMPLETE and no completion manifest. Only media loading, tests, this provenance
note and the source map/resource copies/inventory changed; the keying algorithm
remained byte-identical. No historical implementation was accessed for this fix.

## 0.3.1 detail correction

The parent supplied two user screenshots and authorized using this author's own
0.3 source/final outputs, original RGB decodes and source videos for a new detail
quality correction. The screenshots do not identify unique source frames; feature
matching only identifies candidates in a similar held-pose group. Comparisons use
the same source frame and original canvas, including dark/light actual alpha
composites of white-strand/dark-line crossings and adjacent horizontal structure.
Private image evidence stays with the integrator and is excluded from this source.

Designed multi-family local color candidates selected by compositing-equation
residual, fit confidence gating and a stable-color-reference test. No old tool
implementation, old dedicated thresholds or external production script was read.
No person coordinates or authored image masks were inserted into the algorithm.
OpenCV public RGB-to-HSV and box-filter APIs were used with NumPy math; no public
implementation source was copied. Additional official API documentation consulted:
https://docs.opencv.org/4.x/d8/d01/group__imgproc__color__conversions.html .

Generated tests cover the existing contracts and new crossing/color
cases. Known-alpha fixtures verify structure/color preservation; a purple input
sample or a near-one estimated alpha alone is not proof of authentic material.
This correction conservatively retains near-opaque colors and does not claim
all source spill or low-alpha nonuniform-screen residue has been removed. Full
real-footage evidence and independent review status belong to the integrator's
private batch record, rather than being inferred from these generated tests.

## 0.3.1 candidate revision 2

The original independent reviewer identified a real regression in revision 1:
warm textured green-screen contours could become more green/olive and more
opaque than this author's 0.3 output. The author read only the explicitly
provided review images/metrics and its own 0.3/R1 source/results and original RGB
to reproduce it. Review evidence and revision 1 source/output artifacts were
retained unchanged. No old 0.1/0.2 implementation or external historical script
was accessed.

The correction keeps stable color references as a preference, adds a fitted
textured-reference fallback, separates color brightness bands and stops blending
a valid projected alpha back toward the initial screen-excess estimate. Added an
original known-alpha textured green foreground fixture with both upper/lower
alpha bounds, foreground-color error and actual dark/light composite error
bounds. Twenty-two generated cases pass, including existing thin-line and
authoritative core/RGBA contracts. Local real-image comparison remains evidence
of appearance, not independent ground truth; final independent review status
belongs to the integrator. No alpha-floor increase, component deletion, image
geometry change, coordinate-specific mask or semantic repaint was added.

## 0.4.0 authorized inheritance and optimization

The user explicitly requested combining the 0.2 purple/green cleanup with the
0.3.1 R2 hair/line detail and improving speed, with self-test/independent review
and no publication. This superseded the old-source no-read boundary for this
specific work. The implementer read the archived 0.2
`src/spritekey/core.py` in the private archived 0.2 source snapshot,
SHA256 `60bb155f3b05329d034332fad905de2c825983c4c01c6413a09be2642e98ecbf`,
and its root ALGORITHM.md, SOURCES.md and MIT LICENSE. Also read the specifically
provided historical-source explanation. No missing original script was recovered
or regenerated; no historical CLI, haze deletion, alpha mutation, mask erosion or
whole old pipeline was imported into this version.

Adapted the 0.2 final RGB opponent low/high ceiling formula and bounded contour
concept into normalized RGB, with the same SpriteKey contributors MIT attribution.
The evaluated settings were explicitly converted from 0..255: strength .85,
width 2.5, blue balance 0 / green balance .5, allowance 3/255. Added a bounded
stable-interior RGB-match guard; it is not a semantic classifier or a guarantee
that every authentic purple/green detail is recognized. Core/RGBA remains the
hard final preservation mechanism.

Saved the byte-identical 25-file 0.3.1 R2 source before edits (inventory SHA256
`1455ccab0597db911cc28c23319f2fce58868c9a9451fec6cf8136c00aa507bb`,
keyer SHA256 `a97d042e19b44586c53bc8bd47df3f30b570c08840e5a73356fe058d9bf00cbc`).
Optimized repeated candidate computation by caching unchanged color families,
finite-radius query pruning, bounded distance-transform regions with halo and
target-only RGB fit vectors. The original 0.3.1 matte equations and output
geometry remain the comparison target. No frame/component deletion or alpha-floor
increase is used as a speed or color-cleanup shortcut.

Added generated cases for strength/alpha invariance, matched purple/green material
interiors versus contaminated thin structures, final core/RGBA preservation,
strict new settings and canvas-padding query invariance. Exact fixed-baseline
real-frame pixel comparisons and comparable warmed, alternating benchmark samples
are private author evidence, not inferred from the earlier one-shot render time.
Detailed actual reads, license/source hashes, all timing samples and visual scope
are retained by the integrator outside the distributable package.

## First public release preparation

The owner subsequently authorized publishing huoxuet/spritekey v0.4.0 as an MIT pre-release. Public preparation retains all runtime Python modules and original regression tests byte for byte from the reviewed candidate. Documentation and package metadata were edited; install/integrity checks, CI, original generated demonstration panels and bilingual public usage were added. Private workstation paths in this record are represented by logical source descriptions above; source hashes and historical read/adaptation facts are retained. The detailed original usage is maintained in docs/USAGE.md and as an installed resource; the installed README is the detailed docs/USAGE.md guide; installed Chinese/source/provenance/license copies match their public root documents.
