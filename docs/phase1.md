# Phase 1: optics

These routines compare simtools applications backed by obdeect and sim_telarray
on the same optical models, source directions, and seeds. Core observables are
D80 (point spread), effective area, effective focal length, incident angles,
per-mirror photon fractions, and off-axis image centroids. The source validation
matrix in `obdeect/docs/VALIDATION.md` gives the measured maximum deviations:
across the 0–4 degree, nine-offset runs, D80 differs by at most 1.1%, effective
area by at most 0.45%, and effective focal length by at most 0.1% (the latter
includes mirror-error realization spread). These are empirical reference
levels, not universal hard gates; statistical comparisons should be repeated
with independent seeds.

`run_psf.sh` is the general two-backend optics comparison. The remaining
scripts cover the more specialized observables and applications described in
the source validation matrix.
