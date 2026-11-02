"""Export the sim_telarray model (CTAO-South-<TEL>.cfg and model files) for one telescope, 7.0.0.

usage (container): export_model.py <TEL> <output_dir>
The files go to <output_dir>/run000001/7.0.0/ (same layout as the simtools full chain).
Native sim_telarray and the route use this directory, so both see the same model files.
"""
import sys
from pathlib import Path

from simtools.application.model_reader import create_model_reader
from simtools.io import io_handler
from simtools import settings
from simtools.model.array_model import ArrayModel

tel, out = sys.argv[1], Path(sys.argv[2])
# the config header names the CORSIKA executable; it is only resolved when set explicitly
settings.config._corsika_path = "/workdir/simulation_software/corsika7"
settings.config._corsika_exe = "corsika_qgs3_urqmd_flat"
out.mkdir(parents=True, exist_ok=True)
io_handler.IOHandler().set_paths(output_path=str(out))
reader = create_model_reader(simulation_models_path="/workdir/external/simulation-models")
import os
array = ArrayModel(model_version="7.0.0", site=os.environ.get("SITE", "South"), layout_name=tel, label="obdv_export",
                   model_reader=reader)
array.export_all_simtel_config_files()
print("exported", tel, "to", out, flush=True)
