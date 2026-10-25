import os
from simtools.application.model_reader import create_model_reader
from simtools.model.telescope_model import TelescopeModel
reader = create_model_reader(simulation_models_path=os.environ.get("MODELS_DIR", "/workdir/external/simulation-models"))
for site, tel in (("South", "SSTS-01"), ("South", "SCTS-01"), ("North", "LSTN-01"), ("North", "MSTN-01")):
    m = TelescopeModel(model_reader=reader, site=site, telescope_name=tel, model_version="6.0.2", label="t")
    print(tel, {k: m.parameters[k]["value"] for k in ("mirror_offset", "focal_length") if k in m.parameters}, m.parameters.get("secondary_mirror_parameters", {}).get("value", [None])[0], m.parameters.get("focal_surface_parameters", {}).get("value", [None])[0])
