"""Compile the optical models used by the performance benchmarks.

Usage: python make_models.py [telescope ...]  (default: all five)
Needs obdeect importable and the simulation-models checkout on the branch
``simulation-model-masts`` (MSTS-04 structure).
"""

import subprocess
import sys
import os
from pathlib import Path

from obdeect import OpticalModel

HERE = Path(__file__).resolve().parent
MODELS = Path(os.environ.get("MODELS_DIR", "/workdir/external/simulation-models")) / "simulation-models"
TELESCOPES = ("LSTN-01", "MSTN-07", "MSTS-04", "SSTS-17", "SCTS-design")
VERSION = "7.0.0"
FALLBACK_VERSION = "6.0.2"


def main() -> None:
    branch = subprocess.run(
        ["git", "branch", "--show-current"], cwd=MODELS, capture_output=True, text=True, check=True
    ).stdout.strip()
    if branch != "simulation-model-masts":
        sys.exit(f"simulation-models is on '{branch}', expected 'simulation-model-masts'")
    (HERE / "models").mkdir(exist_ok=True)
    for tel in sys.argv[1:] or TELESCOPES:
        for version in (VERSION, FALLBACK_VERSION):
            try:
                model = OpticalModel.from_simulation_models(
                    MODELS, tel, version, configuration_seed=11, zenith_deg=20.0
                )
            except Exception as error:  # noqa: BLE001 - report and try the fallback version
                print(f"{tel} {version}: {error}", file=sys.stderr)
                continue
            model.save(HERE / "models" / f"{tel}.json")
            print(f"{tel}: version {version}, sha256 {model.sha256}")
            break
        else:
            sys.exit(f"{tel}: no model could be compiled")


if __name__ == "__main__":
    main()
