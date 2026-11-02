# obdeect shower route vs native sim_telarray (phase 3, P9 / R6)

Compares the obdeect route (`python -m simtools.simtel.shower_route`, then sim_telarray `Bypass_Optics=1`)
with native sim_telarray (`Bypass_Optics=0`) on the same CORSIKA file. LSTS-01, MSTS-04, LSTN-01, MSTN-07;
model 7.0.0; 1 TeV gamma; zenith 20/40/60 deg. Result: 20 deg passes, 40/60 deg fail (cause known, fix in progress).
See `results/RESULTS.md`.

## Run

In the container `obdeect-val` (`/workdir/external` = repository root):

```sh
docker exec obdeect-val bash -c '/workdir/external/obdeect-validation/phase3/scripts/run_point.sh LSTS-01 20 50'
# North telescopes: prefix SITE=North
```

`run_point.sh` runs CORSIKA, native sim_telarray (seeds 4242-4244), the route (seed 11) twice for determinism,
and `compare.py`, which writes `results/<TEL>_za<ZA>.json`. `scripts/summarize.py` prints the table.
Set `ROUTE_HEIGHT_OVERRIDE=<m>` where the route rejects the input-plane height (MSTS-04 60 deg: 40.0; MSTN-07 60 deg: 41.0).
Large files stay in `work/` (not versioned).

Requires simtools, CORSIKA 7, sim_telarray and `simulation-models` in the container; Python: eventio, numpy, scipy.
