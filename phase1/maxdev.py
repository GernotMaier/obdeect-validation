"""Largest |obdeect/sim_telarray - 1| per telescope over the offsets (validate-optics)."""
import sys
from pathlib import Path
import numpy as np
from astropy.table import QTable

root = Path(sys.argv[1])
for tel in sys.argv[2:]:
    s, o = (QTable.read(next((root / tel / b / "results").glob("*.ecsv"))) for b in ("sim_telarray", "obdeect"))
    dev = {}
    for key in ("psf_cm", "eff_area", "eff_flen"):
        a, b = np.asarray(s[key].value, float), np.asarray(o[key].value, float)
        ok = np.isfinite(a) & np.isfinite(b)
        dev[key] = 100 * np.max(np.abs(b[ok] / a[ok] - 1))
    print(f"{tel}: D80 {dev['psf_cm']:.2f}%  area {dev['eff_area']:.2f}%  f_eff {dev['eff_flen']:.2f}%")
