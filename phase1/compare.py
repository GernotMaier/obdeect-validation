"""Compare simtools-validate-optics results of the two backends."""
import sys
from pathlib import Path
from astropy.table import QTable

root = Path(sys.argv[1])
for tel in sorted(p.name for p in root.iterdir() if p.is_dir()):
    files = {b: next((root / tel / b / "results").glob("*.ecsv"), None) for b in ("sim_telarray", "obdeect")}
    if not all(files.values()):
        continue
    s, o = (QTable.read(files[b]) for b in ("sim_telarray", "obdeect"))
    print(f"\n{tel}")
    print(" off_x off_y | d80 cm simtel  obdeect   ratio | area m2 simtel obdeect  ratio | f_eff simtel obdeect ratio")
    for a, b in zip(s, o):
        def v(row, key, unit=None):
            x = row[key]
            return float(x.to_value(unit) if hasattr(x, "unit") and unit else x if not hasattr(x, "value") else x.value)
        ps, po = v(a, "psf_cm", "cm"), v(b, "psf_cm", "cm")
        es, eo = v(a, "eff_area", "m2"), v(b, "eff_area", "m2")
        fs, fo = v(a, "eff_flen"), v(b, "eff_flen")
        print(f" {v(a,'off_x','deg'):5.1f} {v(a,'off_y','deg'):5.1f} | {ps:7.3f} {po:8.3f} {po/ps:7.4f} | {es:8.2f} {eo:8.2f} {eo/es:6.4f} | {fs:8.2f} {fo:8.2f} {fo/fs if fs==fs else float('nan'):6.4f}")
