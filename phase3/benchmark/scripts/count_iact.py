"""Count events, IACT data blocks, photon bunches and photons in a CORSIKA IACT file.

usage: count_iact.py <file.iact or .zst>  (eventio python in the container; prints one JSON line)
Bunch and photon counts come from the Photons sub-objects (n_bunches, n_photons) of each TelescopeData block.
"""

import json
import sys

from eventio import EventIOFile

events = blocks = bunches = photons = 0
with EventIOFile(sys.argv[1]) as f:
    for obj in f:
        if type(obj).__name__ == "EventHeader":
            events += 1
        if type(obj).__name__ != "TelescopeData":
            continue
        blocks += 1
        for sub in obj:
            if type(sub).__name__ == "Photons":
                bunches += int(sub.n_bunches)
                photons += int(sub.n_photons)
print(
    json.dumps(
        {
            "file": sys.argv[1],
            "events": events,
            "iact_data_blocks": blocks,
            "bunches": bunches,
            "photons": photons,
        }
    )
)
