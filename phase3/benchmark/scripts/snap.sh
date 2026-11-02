#!/bin/bash
# usage: snap.sh <tag> <logfile>   (run on the host; records load on host and in container)
{
echo "== $1 $(date -u +%FT%TZ)"
echo "host: $(uptime)"
podman stats --no-stream obdeect-val
podman exec obdeect-val bash -c 'echo "container loadavg: $(cat /proc/loadavg)"; ps -eo pcpu,args --sort=-pcpu | head -8 | cut -c1-160'
} >> "$2" 2>&1
