"""Run one command and print one JSON line with wall, user/sys CPU and peak RSS of the child.

usage: timed.py <label> <log-prefix|-> <command...>
The child's stdout and stderr go to <log-prefix>.out and <log-prefix>.err ('-': discarded). Peak RSS is ru_maxrss
of the child process (Linux: kB). Exit code of the child is recorded; the wrapper exits 0.
"""

import json
import os
import subprocess
import sys
import time

label, out, cmd = sys.argv[1], sys.argv[2], sys.argv[3:]
if out == "-":
    stdout = subprocess.DEVNULL
    stderr = subprocess.DEVNULL
else:
    stdout = open(out + ".out", "w")
    stderr = open(out + ".err", "w")
start = time.perf_counter()
proc = subprocess.Popen(cmd, stdout=stdout, stderr=stderr)
_, status, usage = os.wait4(proc.pid, 0)
wall = time.perf_counter() - start
rc = os.waitstatus_to_exitcode(status)
print(
    json.dumps(
        {
            "label": label,
            "rc": rc,
            "wall_s": round(wall, 3),
            "user_s": round(usage.ru_utime, 3),
            "sys_s": round(usage.ru_stime, 3),
            "cpu_s": round(usage.ru_utime + usage.ru_stime, 3),
            "maxrss_mb": round(usage.ru_maxrss / 1024, 1),
        }
    ),
    flush=True,
)
