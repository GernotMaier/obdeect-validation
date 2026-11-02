"""
Telescope inputs of the sim_telarray transmission lookup (model 7.0.0), read from the model files.

- ztel: telescope height above the observatory [m]. The z of array_element_position_ground
  (version 2.0.0, production 7.0.0), which simtools writes as the CORSIKA TELESCOPE z (origin at
  the observation level). sim_telarray uses it as array.ztel (sim_telarray.c:1859).
- pathlen: pathlen_tel [m]. For a single-mirror telescope (mirror_class 0, sim_config.c:4670-4672)
  pathlen_tel = focal_length of the design model. Dual-mirror (mirror_class 2) would use the
  primary/secondary/focal-surface path (sim_config.c:4665); not needed here, asserted below.
"""

import json
from pathlib import Path

MODELS = Path("/workdir/external/simulation-models/simulation-models/model_parameters")
PRODUCTIONS = MODELS.parent / "productions" / "7.0.0"
TELESCOPES = ["LSTS-01", "MSTS-04", "LSTN-01", "MSTN-07"]


def _value(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))["value"]


def telescope_parameters(name):
    """Return dict(name, site, design, ztel_m, pathlen_m) for a telescope of model 7.0.0."""
    production = json.loads((PRODUCTIONS / f"{name}.json").read_text(encoding="utf-8"))
    design = production["design_model"][name]
    site = "South" if "S-" in name else "North"  # LSTS/MSTS south, LSTN/MSTN north
    position = _value(MODELS / name / "array_element_position_ground" /
                      "array_element_position_ground-2.0.0.json")
    focal_cm = _value(MODELS / design / "focal_length" / "focal_length-1.0.0.json")
    mirror_class = _value(MODELS / design / "mirror_class" / "mirror_class-1.0.0.json")
    if mirror_class != 0:
        raise NotImplementedError(f"{design}: mirror_class {mirror_class} (dual mirror path)")
    return {
        "name": name,
        "site": site,
        "design": design,
        "ztel_m": float(position[2]),
        "pathlen_m": float(focal_cm) / 100.0,
    }
