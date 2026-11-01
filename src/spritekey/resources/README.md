# SpriteKey 0.4.0 — detailed usage

Local green/blue screen extraction: original RGB8 frames become straight RGBA8
PNG frames at their original dimensions. No network, model, frame interpolation,
geometric transform or small-component removal is used. The matte/IO base was
implemented in 0.3/0.3.1 from a functional specification. Version 0.4 explicitly
adapts the user-authorized MIT 0.2 RGB-only opponent-channel cleanup, retains the
0.3.1 R2 matte and optimizes candidate computation. See `AUTHORSHIP.md` for actual
historical/new source-access scopes, rather than a legal guarantee or a claim
that 0.4 never read earlier source. Detailed private validation
media and internal access ledgers are excluded from this distributable source.

## Install (Python 3.10+)

Run from the repository root (the directory containing pyproject.toml).
Use a fresh virtual environment. The following commands use a macOS/Linux shell;
for Windows PowerShell use the public README quick start. Default PyPI:

```sh
python3 -m venv .venv
. .venv/bin/activate
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install .
```

Alternative when the default index is slow, using the Tsinghua mirror:

```sh
.venv/bin/python -m pip install --index-url https://pypi.tuna.tsinghua.edu.cn/simple .
```

Build a pure Python wheel without bundling dependencies:

```sh
.venv/bin/python -m pip wheel --no-deps --wheel-dir dist .
```

The wheel has no dependency binaries, models, FFmpeg, or game images. NumPy,
Pillow and OpenCV are separately installed dependencies with their own notices.
For video, obtain and license an external FFmpeg 7.x executable separately.

## Original generated demo

```sh
python -m spritekey.demo demo-040
spritekey --config demo-040/config.json
```

Open `demo-040/output/preview.html` locally. It embeds every image,
uses no external resource or network request, supports light/dark/checker backdrops,
playback with known durations, a frame slider, and previous/next. Playback is
disabled when timing is UNKNOWN. The generator draws geometric shapes at fourfold
resolution then reduces them to produce genuine alpha and composited test inputs.
It reads no pictures. Demo images and demo source are covered by this package's MIT
license; they are test geometry rather than production art.

## Configure

Paths are relative to the JSON file. Output must not exist, even as an empty
directory. Unknown options, duplicate keys, wrong PNG modes/dimensions, overlapping
input/mask/output trees and hardlinked frame aliases are errors.

```json
{
  "input_dir": "input",
  "output": "output-new",
  "screen": "green",
  "background_roi": [0, 0, 12, 12],
  "fps": "24000/1001",
  "settings": {
    "background_tolerance": 0.025,
    "roi_max_deviation": 0.10,
    "edge_search_radius": 16,
    "core_threshold": 240,
    "core_background_guard": 0.08,
    "alpha_floor": 0.004,
    "edge_fit_tolerance": 0.06,
    "edge_spatial_weight": 0.001,
    "seed_color_variation": 0.02,
    "edge_despill_strength": 0.85,
    "edge_despill_width": 2.5,
    "edge_despill_balance": null,
    "spill_allowance": 0.011764705882352941,
    "material_protection_radius": 16,
    "material_protection_tolerance": 0.08
  }
}
```

`input_video` replaces `input_dir` for video, without `fps` or explicit timing:

```sh
spritekey --config video.json --ffmpeg /absolute/path/to/ffmpeg
```

PNG sequences are static 8-bit RGB PNGs in natural filename order. Output names
are `frames/00000001.png` onwards; original names remain in the manifest.
`background_roi` is `[left, top, right, bottom]`, right/bottom exclusive, and must
contain uniform bare screen in **every** frame. Median screen sampling is per
frame. No single-color method can recover a foreground identical to the screen.

Timing choices for PNGs are:

* `fps`: a positive integer or rational/decimal string; constant durations.
* `pts_seconds`: an array of strictly increasing integer/rational/decimal strings,
  together with positive `last_duration_seconds`. Negative starting PTS are valid.
* Neither: manifest timing is `UNKNOWN`, with null PTS and durations. No rate is
  guessed. JSON floating numbers are rejected for timing; use decimal strings.

Video uses the first video stream, `-copyts`, `showinfo`, `-fps_mode passthrough`,
and no autorotation. Original PTS integers and time base are retained as rational
seconds. Adjacent PTS differences determine presentation intervals; the last
frame requires an explicit positive `showinfo` duration. Reported source duration
integers are also retained. Missing/non-increasing timing, frame mismatch,
changing dimensions or decoder corruption is rejected. FFmpeg 7.x is required;
there is no FPS override or silent fallback. This validates decoder-reported
timing; it cannot independently prove metadata in an input container is truthful.

Optional `core_masks` is a directory containing exactly one 8-bit grayscale L PNG
per frame, with the **original input filename** (video: `00000001.png` onwards).
Values >= `core_threshold` request full opacity and exact source RGB, unless
their distance from the sampled screen is <= `core_background_guard`. Rejected
background requests are counted in the manifest. Paint only high-confidence
opaque interiors; low grayscale values do not create partial alpha.

Optional `preserve_rgba` follows the same names and dimensions, as 8-bit RGBA PNGs.
Every pixel whose alpha is greater than zero replaces the final RGBA **byte for
byte**, after every other operation. Alpha-zero preservation pixels do nothing.
Use it for authenticated fine detail or screen-colored foreground. Source frames,
core masks, preservation layers and output must be disjoint.

| Setting | Meaning / allowed range |
|---|---|
| `background_tolerance` | Maximum RGB-channel distance from sampled screen set transparent; `[0,1)` |
| `roi_max_deviation` | Maximum RGB-channel deviation permitted inside sample ROI; `[0,1)` |
| `edge_search_radius` | Nearest opaque foreground search radius in pixels; `0..256`; zero disables local refinement |
| `core_threshold` | Inclusive grayscale confidence threshold; integer `1..255` |
| `core_background_guard` | Screen-like core requests at or below this distance are ignored; `[0,1)` |
| `alpha_floor` | Alpha at or below this value becomes transparent; `[0,1)` |
| `edge_fit_tolerance` | Maximum normalized RGB RMS residual for a local foreground candidate; `(0,1]`; smaller values trust fewer local priors |
| `edge_spatial_weight` | Normalized RGB residual cost per pixel of candidate distance; `[0,1]`; distance breaks color-fit ties |
| `seed_color_variation` | Maximum RGB-channel standard deviation in a 3x3 neighborhood for a preferred estimated opaque color seed; `[0,1]`; accepted core seeds bypass this check; compatible textured references are tried when stable ones cannot fit |
| `edge_despill_strength` | New RGB-only opponent cleanup amount; `[0,1]`; `0` disables this added stage and retains the 0.3.1 R2 RGB result |
| `edge_despill_width` | Near-opaque contour width in pixels; `[0,256]`; fractional-alpha pixels remain eligible when width is zero |
| `edge_despill_balance` | Other-channel ceiling blend; `[0,1]` or `null`; null resolves to `0` on blue, `.5` on green |
| `spill_allowance` | Normalized RGB allowance over the ceiling; `[0,1]`; default `3/255` |
| `material_protection_radius` | Search radius for a compatible stable material interior; `[0,256]`; zero disables this automatic guard |
| `material_protection_tolerance` | Maximum RGB-channel difference from that reference; `[0,1]`; explicit core/RGBA remains authoritative |

RGB distances and alpha are normalized to `0..1`. `background_tolerance` also
supplies the input uncertainty allowance for the directional gamut bound.
Matte defaults retain the 0.3.1 R2 choices; new cleanup defaults convert the
evaluated 0.2 settings. Actual footage still needs visual assessment. See
[`ALGORITHM.md`](https://github.com/huoxuet/spritekey/blob/v0.4.0/src/spritekey/resources/ALGORITHM.md) for the equation, assumptions
and limitations. There is no hardcoded costume, silhouette or weapon model.

0.3.1 compares several local hue/brightness families by their ability to explain
the observed RGB composite. An incompatible nearby white strand can no longer
automatically supply both alpha and color for a dark thin line. Unreliable color
priors are reduced rather than forcing a neighboring material's color. Local
color statistics select references only; no output image/matte blur, dilation,
coordinate-specific mask, component deletion or temporal resampling is applied.

The historical 0.3.1 candidate revision 2 retained that detail correction and repaired a green-edge
regression found in independent review of revision 1. Stable color references are
preferred, with a fit-checked textured-reference fallback where the stable set
cannot explain observed RGB. Hue families are split into brightness bands to
reduce mismatching shaded versions of a material. Once a candidate passes the fit
test, use its projected alpha directly; do not blend it toward the potentially
inflated initial screen-excess estimate. Confidence controls the color prior.
Those two candidates shared version 0.3.1 and remain distinguishable by
`SOURCE-SHA256.json` and each output manifest's code fingerprint. Their evidence
is retained separately from the current 0.4.0 work.

0.4 retains the R2 matte and adds the authorized 0.2 color-only contour operation:
bound the screen channel by a weighted low/high value of the other channels,
then reduce its excess by strength. This catches blue contamination even where
red is higher than blue. No alpha value is changed by this added stage. Explicit
core and RGBA preservation are applied last. A conservative automatic guard also
matches edge RGB to a stable matching-color interior beyond the contour; it does
not treat estimated opacity or purple input hue alone as proof of a real material.
It cannot authenticate every small, isolated or textured matching-color detail;
use authoritative layers where the intended color is known.

Candidate matching caches the same HSV partition once, prunes queries with no
possible reference inside the finite radius, includes a full-radius halo around
the remaining query bounds, and evaluates color fits as vectors of target pixels.
It retains the original resolution, candidate families, fit equations and
distance-transform mode. This is computation pruning, not a deliberately lower
quality matte mode. Validate equivalence with `edge_despill_strength: 0`; compare
default-on timing separately because the RGB cleanup adds real work. Private
benchmark evidence uses a fixed source snapshot, warmed inputs, alternating
execution order and repeated samples under the same interpreter/thread settings.

One RGB observation still cannot prove foreground color and alpha independently.
The tool conservatively preserves colors estimated near opaque, which can also
preserve screen spill already present in those samples. A purple region in the
input or an estimated alpha near one is not proof of authentic purple material.
Known-truth synthetic fixtures and authoritative core/RGBA layers are the basis
for the color-preservation checks. Low-alpha background residue can remain when
the bare screen varies away from the sampled ROI; inspect actual composites on
light/dark backgrounds rather than straight RGB alone. No claim of universal
spill removal or recovery of every translucent fiber is made.

## Outputs and failure semantics

The output contains frames, `preview.html`, and only on success `manifest.json`.
Video also retains decoded RGB PNGs and the FFmpeg log. The manifest records
every input/result SHA256, masks, sample RGB, timing evidence, dependencies and
package file fingerprints. Fully transparent pixels have RGB zero. `preserve_rgba`
only overrides nonzero-alpha pixels, so it does not weaken that invariant.

If processing fails after creating output, `INCOMPLETE` remains and no completed
manifest is written. Inspect the failure and choose another new output directory
for a new run; this command never overwrites an old run. Abrupt process termination
may also leave `.partial` files, which are not completion evidence.

## Test

```sh
PYTHONPATH=src python -m unittest discover -s tests -v
SPRITEKEY_TEST_FFMPEG=/absolute/path/to/ffmpeg PYTHONPATH=src python -m unittest discover -s tests -v
```

Source, example, attribution, algorithm and dependency notices are included as
wheel resources. No game asset license is granted by the tool's source license.

For release-platform evidence and the distinction between PNG CI and video tests, see [VALIDATION.md](https://github.com/huoxuet/spritekey/blob/v0.4.0/VALIDATION.md). Without SPRITEKEY_TEST_FFMPEG, two external-video tests are explicitly skipped.
