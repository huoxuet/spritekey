# Changelog

## 0.4.0 — first public preview

- Combine the 0.3.1 revision 2 local-color matte with authorized MIT 0.2
  opponent-channel contour cleanup. The added stage changes RGB, never alpha.
- Add bounded stable-interior color matching and retain explicit core/RGBA
  preservation as the final authority for known foreground.
- Cache color families, prune impossible radius queries, bound distance-transform
  work with a full-radius halo and vectorize target-only color fitting.
- Retain native dimensions, rational timing and completion provenance; provide
  offline playback plus original green/blue geometric examples.
- Publish Python source/wheel, MIT and dependency notices, English/Chinese usage,
  installation checks and a PNG CI matrix.

Historical 0.2/0.3/0.3.1 were private iterations. Their full Git history and
production media are not part of this independent public repository. See
AUTHORSHIP.md for scoped provenance, VALIDATION.md for evidence and limits.
