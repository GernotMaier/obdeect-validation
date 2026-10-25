# Phase 2: calibration light

The phase 2 cases compare complete flasher and illuminator simulations through
the two ray-tracing backends. They measure photoelectrons per event, image
centre and width, photoelectron time spread, and pixel-wise image shape pulls.
Two seed sets per backend estimate run-to-run scatter; decisions should account
for that scatter. Same-seed flasher pixel shapes are expected to agree at the
Poisson level (shape-pull width about 1). In the documented 7.0.0 cases,
flasher yields agree within about 0.5%, and illuminator yields agree within
their seed scatter except where known sim_telarray refraction or 2-D mirror
reflectivity conventions apply. See `obdeect/docs/VALIDATION.md` for the case
table and interpretation of those exceptions.
