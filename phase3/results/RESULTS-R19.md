# R19 atmospheric correction: obdeect route vs native sim_telarray, zenith rerun

- All 9 points pass the gate (total p.e. route/native within 1 % and within 3 sigma). Ratios 0.999-1.005; largest deviation 1.47 sigma.
- The 40 and 60 deg excess from RESULTS.md (old ratios 1.07-1.39) is gone with the R19 correction.
- Regression: LSTS-01 at 20 deg gives 0.9992 (old 1.0026), within 0.4 % of native.

| telescope | zenith [deg] | native mean [p.e.] | route [p.e.] | route/native | old ratio | pass/fail |
|---|---|---|---|---|---|---|
| LSTS-01 | 20 | 1678606 | 1677207 | 0.9992 | 1.0026 | pass (regression) |
| LSTN-01 | 40 | 1061542 | 1062029 | 1.0005 | 1.0705 | pass |
| MSTN-07 | 40 | 264967 | 265766 | 1.0030 | 1.0763 | pass |
| LSTS-01 | 40 | 1196284 | 1197360 | 1.0009 | n/a (not run before) | pass |
| MSTS-04 | 40 | 406894 | 406417 | 0.9988 | n/a (not run before) | pass |
| LSTS-01 | 60 | 390242 | 390761 | 1.0013 | 1.3823 | pass |
| MSTS-04 | 60 | 134511 | 135149 | 1.0047 | 1.3946 | pass |
| LSTN-01 | 60 | 325837 | 325495 | 0.9990 | 1.3327 | pass |
| MSTN-07 | 60 | 95095 | 95157 | 1.0007 | 1.3445 | pass |

Dropped bunches (zero bypass transmission, from the route INFO log): LSTS-01 20 deg 194122; LSTN-01 40 deg 204640; MSTN-07 40 deg 35719; LSTS-01 40 deg 278485; MSTS-04 40 deg 82041; LSTS-01 60 deg 376059; MSTS-04 60 deg 121954; LSTN-01 60 deg 243391; MSTN-07 60 deg 56473.

## How it was run

- Unit tests (worktree, container): `SETUPTOOLS_SCM_PRETEND_VERSION=0.0.0 PYTHONPATH=src python -m pytest -n 2 -q --no-cov tests/unit_tests`: 4976 passed, 1 skipped.
- Lint (worktree, container): `ruff check` and `ruff format --check` on the changed files; see the caveat below.
- Route, per point: `PYTHONPATH=/workdir/external/wt/simtools-p3/src scripts/run_route.sh <TEL> <ZA> 11 r19` (SITE=North for North telescopes; no `ROUTE_HEIGHT_OVERRIDE`).
- Native and IACT inputs: reused from `work/<TEL>_za<ZA>/` (South 40 deg: CORSIKA run and native seeds 4242-4244 created for this rerun).
- Comparison: `scripts/compare.py work/<TEL>_za<ZA> r19 4242 4243 4244 > work/<TEL>_za<ZA>/compare_r19.json`.
- Dropped count: shower_route rerun with root logger at INFO (same seeds), bunch output deleted.
- Route plane heights from the worktree (m): LSTS-01 20 deg 29.9; LSTN-01 40 deg 36.7; MSTN-07 40 deg 26.6 (old 24.6); LSTS-01 40 deg 36.7; MSTS-04 40 deg 27.7; LSTS-01 60 deg 56.2; LSTN-01 60 deg 56.2; MSTS-04 60 deg 42.0 (old override 40.0, now rejected by the guard); MSTN-07 60 deg 40.4 (old override 41.0).
- Caveat: South 40 deg model export ran with `PYTHONPATH` on the worktree (the main checkout import of `simtools.settings` failed). CORSIKA and native used the main checkout.
- Caveat: the worktree had no generated `src/simtools/_version.py`; it was copied from the main checkout (gitignored, no tracked change). Without it the route rejects the model with version 0.0.0.
- Lint: ruff format is clean; ruff check still reports 2 items in `shower_route.py` and `_shower_transmission.py` (float equality `bypass == 0.0`, private-name import), not changed.
