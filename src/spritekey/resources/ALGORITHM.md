# Matting, authorized color cleanup and bounded computation (0.4.0)

Every frame independently samples a uniform screen rectangle. Let C be observed
RGB/255, B the channelwise median of that rectangle, a alpha, F foreground color:

    C = a F + (1-a) B

All operations here are in normalized **stored RGB sample space**, not linear
light. This matches the demo compositor and many generated RGB composites, but
linear-light or strongly compressed sources can violate that assumption.

1. Select G or B as the key channel. Its excess over the maximum other channel
   estimates screen contribution, divided by the corresponding excess in B.
   One minus that contribution gives a first matte estimate.
2. Compute a directional gamut alpha lower bound: loss in the key channel and
   increases in the other channels can supply foreground evidence. Allow the
   configured background tolerance as RGB sample uncertainty. Do not treat key
   channel overshoot or a decrease in other channels as opaque evidence: codec
   ringing can cause those deviations on bare screen. Exact/near sample colors
   are transparent. Take the maximum of the first matte and this relaxed bound.
3. Accept high-confidence core mask requests only outside the configurable strong
   background guard. Accepted core pixels are opaque and retain source RGB.
4. A near-opaque initial estimate is not proof of an unmixed foreground sample.
   A 3x3 RGB standard-deviation check prefers locally stable color references;
   accepted core mask seeds bypass it. These statistics do not blur output
   RGB/alpha or change geometry. Group candidate seeds into six HSV hue sectors
   split across three brightness bands, plus three neutral brightness families,
   using OpenCV's public RGB-to-HSV API. For each family, a labeled distance
   transform finds the nearest candidate
   within the configured radius. Project C-B onto each candidate's F-B, respecting
   the relaxed lower bound, and calculate RGB RMS reprojection residual. Minimize
   residual squared plus squared distance cost. Reject candidates whose residual
   exceeds `edge_fit_tolerance`; otherwise confidence is one minus residual over
   tolerance. Prefer stable references; only where they provide no valid fit,
   try textured estimated-opaque references under the same fit test. A valid
   candidate supplies its projected alpha directly. Confidence controls the
   color prior, not blending back toward a potentially inflated initial alpha.
   Thus a slightly farther dark line color can beat a nearby incompatible white
   strand. Only initially partial pixels are refined; exact background and initial
   near-opaque estimates remain unchanged in alpha by this step.
5. Recover straight RGB as (C-(1-a)B)/a, bounded to RGB gamut. On locally refined
   soft pixels, reduce inverse-alpha amplification of codec errors by blending
   toward the selected compatible foreground seed's RGB. Permit a mean brightness
   adjustment bounded to +/-0.04; prior strength is confidence times (1-a^4).
   An incompatible color prior therefore cannot force whitening/desaturation of
   thin dark structure. Finally, for unprotected soft pixels whose source
   is key-dominant, limit the recovered key channel to the maximum other channel.
   This suppresses residual screen chroma without creating a replacement hue in
   opaque foreground. Tiny alpha below the explicit floor becomes transparent;
   RGB of alpha-zero output becomes zero.
6. Apply the user-authorized 0.2 RGB-only opponent-channel stage. For each eligible
   contour/fractional pixel, let low/high be the other channels' minimum/maximum.
   The screen-channel ceiling is `low + balance*(high-low) + allowance`; subtract
   `strength * max(screen_channel-ceiling,0)`. Defaults reproduce the evaluated
   0.2 color-stage settings in normalized space: strength .85, width 2.5, balance
   0 on blue / .5 on green, allowance 3/255. This catches purple contamination
   whose blue is below red but above green. Eligibility uses alpha>.025 and either
   fractional alpha or a narrow near-opaque contour. The contour uses OpenCV's
   L2 mask-3 chamfer distance approximation, as in 0.2; this changes RGB eligibility
   only, never alpha or geometry.
7. A new bounded material guard requires a stable estimated-opaque interior
   beyond contour width+1 and a matching-color RGB reference within the configured
   radius/tolerance. Neither input hue nor estimated alpha alone authenticates a
   material. A narrow contaminated arrow/string with no compatible interior still
   receives cleanup; broad authentic purple/green fixtures with compatible
   interiors are protected. Small, isolated, heavily textured or ambiguous details
   can lack such evidence; explicit core/RGBA is the authoritative protection.
8. Restore accepted core source RGB/full alpha. Apply every nonzero-alpha RGBA
   preservation pixel as a final byte-exact override.

The 0.3/0.3.1 matting implementation was derived from the equation and public APIs.
The equation and local-sample approach are general techniques, not a claim of
novelty. Its historical no-old-source scope is recorded in AUTHORSHIP.md. Version
0.4 explicitly reads/adapts the authorized MIT 0.2 color stage; it does not claim
to have avoided earlier source. The 0.2 CLI, alpha/haze changes, reference erosion
and whole old pipeline are not inherited. Exact paths/hashes are in SOURCES.md.

## Computation equivalence and speed evidence

The 0.3.1 R2 matte remains the fixed reference. Cache the same HSV family map
once for both stable/textured queries. A square seed-count query only excludes
targets with no possible finite-radius reference. For remaining targets, include
ceil(radius)+2 halo around their bounds, run the same labeled mask-5 distance
transform in that region, and evaluate the unchanged color-fit math only at the
target coordinates. A candidate at accepted distance cannot lie outside that
halo; no output pixel, component or frame is removed by the computation bounds.
The mask-5 distance is the same pre-existing chamfer approximation, not a new
low-resolution substitute. Projection/channel math remains float32 in the same
order; hardware/library-specific pixel equivalence is checked against the saved
0.3.1 source, not assumed from this explanation.

At despill strength zero the added RGB stage is skipped. This is the equivalence
test mode; default-on timing includes the real added color/material work and is
reported separately. Comparable benchmarks fix interpreter/dependencies/OpenCV
threads, warm the inputs, alternate old/new order, repeat at least three rounds
and retain every sample. Core in-process time is separate from complete CLI/PNG/
preview/manifest time; CLI process-startup/cache treatment is stated explicitly.
No speed multiplier is derived from earlier one-shot full-video renders.

Limitations: a single observation cannot uniquely determine both alpha and RGB.
True screen-colored foreground, reflecting metals, motion blur, colored
translucency and compression spill remain ambiguous. Nearest foreground color can
be wrong near differently colored details, especially when no stable color seed
exists for a fully partial feature. Strong codec errors can still leave
neutral/warm/purple edge residue; set `edge_search_radius` to zero or
supply an explicit preservation layer if necessary. A core mask is a confidence
hint with a screen guard; it cannot force near-pure screen opaque. A preservation
layer is authoritative. There is no temporal propagation, geometry correction,
optical flow, small-component removal, matting model or replacement frame.

Near-one initial alpha is an algorithm estimate, not an independent ground truth.
Conservative preservation of such RGB samples can retain input spill as well as
authentic material. Background differences outside the pure-screen ROI can leave
low-alpha residue far from foreground. This release does not add a spatial
background model or raise the alpha floor to hide it. True screen-colored and
true purple material preservation is verified only in known-alpha generated
fixtures and with explicit protection layers, not inferred from input hue alone.

Validation record: the first independent defaults passed generated tests but
failed visual assessment on high-saturation green/blue codec fringes. The bound
and soft-color corrections above were developed from the original RGB and this
implementation's own output on six explicitly provided neighboring frames.
Dark/light alpha-composited inspection showed clear improvement while retaining
hair and fine independent weapon lines. This is a bounded author check, not
evidence that every frame of those videos or other footage is accepted.

Public API reference: OpenCV `distanceTransformWithLabels`, `DIST_LABEL_PIXEL`,
`DIST_L2` at https://docs.opencv.org/4.x/d7/d1b/group__imgproc__misc.html . Pillow
`Image.open`, `Image.fromarray`, `Image.save`, `ImageDraw`, and `Image.resize` at
https://pillow.readthedocs.io/en/stable/reference/Image.html . NumPy array math
and channel reductions use public APIs; no dependency implementation source was
copied. The authorized project-owned 0.2 color-stage adaptation is disclosed above.
OpenCV RGB-to-HSV / boxFilter API references:
https://docs.opencv.org/4.x/d8/d01/group__imgproc__color__conversions.html and
https://docs.opencv.org/4.x/d4/d86/group__imgproc__filter.html .

0.3.1 validation adds original known-alpha white-strand/dark-line crossings,
horizontal thin structures, moderate multicolor soft coverage under deterministic
RGB perturbations, and explicit green/purple protection checks. The generated
soft-coverage assertions do not claim to identify every nearly opaque colored
coverage ramp from one observation. Supplied screenshots have no source-frame
metadata; visual/feature matching identifies a short held-pose group, not a unique
frame. All version comparisons use the same actual source frame and canvas.

Independent review of candidate revision 1 found a green/olive fringe regression:
texture filtering could leave no color reference and the alpha confidence blend
could thicken the initial estimate. Revision 2 adds the textured-reference
fallback, finer brightness grouping and direct valid-alpha projection above.
An original known-alpha green-screen textured-foreground regression checks alpha
over- and under-coverage, RGB error, and signed actual composite errors against
both dark and light backgrounds. It fails revision 1 and passes revision 2;
existing known-truth thin-line/core/preservation cases remain required. Gray/warm
grain, near-opaque spill ambiguity and nonuniform-background residue are still
limitations; the repair is not a claim that all foreground alpha is exact.
