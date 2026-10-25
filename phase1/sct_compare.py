import sys
from astropy.table import QTable
from simtools.ray_tracing.psf_analysis import PSFImage
from pathlib import Path
results = Path(sys.argv[1])
photon_dir = Path(sys.argv[2])
o = QTable.read(next(results.glob("*.ecsv")))
T = {0: 0.971}
print(" off_x off_y | d80 cm simtel obdeect ratio | area simtel obdeect ratio(T applied same) | centroid r simtel")
from simtools.model.model_utils import compute_telescope_transmission
pars = [0.971, 1.0, 0.158, 5.376, 1.069, 0.0]
import math
for row in o:
    ox, oy = float(row["off_x"].value), float(row["off_y"].value)
    img = PSFImage(focal_length=558.6, containment_fraction=0.8)
    img.read_photon_list_from_simtel_file(photon_dir / f"photons_{ox:g}_{oy:g}.lis")
    t = compute_telescope_transmission(pars, math.hypot(ox, oy))
    ps, po = img.get_psf(0.8, "cm"), float(row["psf_cm"].value)
    es, eo = img.get_effective_area(t), float(row["eff_area"].value)
    r = math.hypot(img.centroid_x, img.centroid_y)
    fe = r / math.tan(math.radians(math.hypot(ox, oy))) if ox or oy else float("nan")
    print(f" {ox:5.1f} {oy:5.1f} | {ps:6.3f} {po:6.3f} {po/ps:7.4f} | {es:7.3f} {eo:7.3f} {eo/es:7.4f} | f_eff {fe:8.2f} {float(row['eff_flen']):8.2f}")
