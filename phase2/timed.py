"""Run a command; report wall time, CPU time and peak memory of it and its children.

Usage: python timed.py <report.json> <command> [arguments]
"""

import json
import resource
import subprocess
import sys
import time

start = time.perf_counter()
code = subprocess.call(sys.argv[2:])
usage = resource.getrusage(resource.RUSAGE_CHILDREN)
report = {
    "command": sys.argv[2:],
    "returncode": code,
    "wall_s": time.perf_counter() - start,
    "cpu_s": usage.ru_utime + usage.ru_stime,
    "max_rss_mb": usage.ru_maxrss / 1024.0,
}
with open(sys.argv[1], "w", encoding="utf-8") as output:
    json.dump(report, output, indent=1)
sys.exit(code)
