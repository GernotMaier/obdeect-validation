"""Parameter versions chosen by obdeect's reader vs simtools' production-table merge."""
from pathlib import Path
import os

from obdeect.repository import read_telescope
from simtools.model_repository.files import read_production_tables

root = Path(os.environ.get("MODELS_DIR", "/workdir/external/simulation-models")) / "simulation-models"
for version in ("6.0.1", "6.0.2", "6.1.1", "6.2.1"):
    tables = read_production_tables(root / "productions" / version)["telescopes"]
    for tel in ("LSTN-01", "LSTS-01", "MSTN-01", "MSTS-01", "SSTS-01", "SCTS-01"):
        if tel not in tables["parameters"]:
            continue
        mine = {k: v["parameter_version"] for k, v in read_telescope(root, tel, version).records.items()}
        theirs = {}
        chain = [tel]
        while (parent := tables["design_model"].get(chain[-1])) is not None:
            chain.append(parent)
        for instrument in reversed(chain):
            theirs |= tables["parameters"][instrument]
        diff = {k for k in mine.keys() | theirs.keys() if mine.get(k) != theirs.get(k)}
        print(version, tel, len(mine), "parameters", "identical" if not diff else f"DIFFER {sorted(diff)}")
