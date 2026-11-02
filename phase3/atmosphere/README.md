# P7: atmospheric transmission, simtools vs sim_telarray

Summary:
- A Python port of sim_telarray's transmission lookup (`atmospheric_transmission2`, sim_absorb.c) matches the C code
  exactly (max diff 0.0) for LSTS-01, MSTS-04, LSTN-01, MSTN-07 (model 7.0.0). The per-telescope tables for option B pass.
- simtools `AtmosphericTransmission.transmission()` misses sim_telarray's instrument path term and is off by up to 0.035.
  A small simtools change (below, not applied) fixes it.
- Open: truncated model rows at 200-290 nm, and the telescope height convention (up to 0.049 in transmission).

## Physics of the port

sim_telarray's optical depth from emission height to the telescope is the vertical depth between the two altitudes
times the airmass, plus an instrument path term: the depth between ztel and ztel + pathlen, without airmass factor
(sim_absorb.c:785, sim_telarray.c:1859-1870). All four telescopes are single-mirror, so pathlen = focal length (sim_config.c:4672).
ztel is the z of `array_element_position_ground`, which simtools writes as the CORSIKA TELESCOPE z.

| Telescope | ztel [m] | pathlen [m] |
| --- | --- | --- |
| LSTS-01 | 34.0 | 28.0 |
| MSTS-04 | 21.0 | 16.0 |
| LSTN-01 | 45.0 | 28.0 |
| MSTN-07 | 65.0 | 16.0 |

## Results (gate: max abs diff < 1e-3)

| Check | Max abs diff | Result |
| --- | --- | --- |
| Port incl. path term vs C harness (4 x 20 000 random cases) | 0.0 | pass |
| Per-telescope table values vs C harness (4 x 92 916 cells) | 0.0 | pass |
| simtools vs port, atmosphere only, South / North | 3.8e-4 / 3.9e-4 | pass |
| Unpatched simtools vs port incl. path term | 0.014-0.035 | fail |
| Patched simtools vs port incl. path term | < 5e-15 | pass |

The path term changes transmission by up to 0.116 (LSTS-01, 200 nm, observation level), so atmosphere-only tables are not enough for option B.

## Proposed simtools change (not applied)

```diff
-    def transmission(self, wavelength_nm, emission_altitude_m, telescope_altitude_m, airmass):
+    def transmission(
+        self, wavelength_nm, emission_altitude_m, telescope_altitude_m, airmass, pathlen_m=0.0
+    ):
         depth = np.abs(
             self.optical_depth(wavelength_nm, emission_altitude_m)
             - self.optical_depth(wavelength_nm, telescope_altitude_m)
-        )
-        transmitted = np.exp(-depth * np.asarray(airmass))
+        ) * np.asarray(airmass)
+        if pathlen_m:
+            depth = depth + (
+                self.optical_depth(wavelength_nm, telescope_altitude_m + pathlen_m)
+                - self.optical_depth(wavelength_nm, telescope_altitude_m)
+            )
+        transmitted = np.exp(-depth)
```

Default `pathlen_m=0` keeps existing callers unchanged. Full diff: `work/simtools_proposal/transmission_path_term.diff`.

## Open issues

1. **Truncated model rows.** For 200-290 nm the ECSV lists only some altitudes (up to 4-40 km). sim_telarray then gives zero
   transmission above the last row; simtools clamps. Effect up to 3.9e-4. Needs complete MODTRAN rows in the model.
2. **Telescope height convention.** The schema says z is above `reference_point_altitude` (2163 m South, 2177 m North),
   but the observation levels are 2147 m and 2156 m. If so, ztel should be z + 16 m (South) or z + 21 m (North), changing
   transmission by up to 0.049. The chain currently uses z. Needs confirmation by the model owners.

## Files

- `simtel_transmission.py`: the port; `check_port_against_c.py`, `check_simtools_patch.py`: the checks.
- `acceptance_telescope_<name>.ecsv`: option-B tables (200-1000 nm, obs level and 3-30 km, zenith 0/20/40/60;
  columns `transmission` with path term and `transmission_atmosphere_only`).
- `work/c_harness/`: C harness linked against unmodified sim_absorb.c and rpolator.c. The full sim_telarray executable was not run.
