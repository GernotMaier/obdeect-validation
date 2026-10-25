#!/bin/bash
# sim_telarray ray tracing of SCTS-01 with a one-pixel camera (the container build allows 2368 pixels).
set -e
VAL_DIR=${VAL_DIR:-/workdir/external/val}
SIM_TELARRAY_DIR=${SIM_TELARRAY_DIR:-/workdir/simulation_software/sim_telarray}
OUT_DIR=${OUT_DIR:-$(cd "$(dirname "$0")" && pwd)/out/sct-simtel}
base=$VAL_DIR/psf-6.0.2/SCTS-01/sim_telarray
model=$base/model/6.0.2
out=$OUT_DIR
mkdir -p $out
printf '%s\n' "# Perfect light collection" "0 1.0" "30 1.0" "60 1.0" "90 1.0" > $out/funnel.dat
printf '%s\n' "# Single pixel camera" "PixType 1 0 0 300 1 300 0.00 \"$out/funnel.dat\"" \
  "Pixel 0 1 0. 0. 0 0 0 0x00 1" "Trigger 1 of 0" > $out/camera.dat
echo "0. 70.0 1.0 10.0" > $out/stars.lis
run() {
  ox=$1; oy=$2
  theta=$(python -c "print(20.0-$ox)"); phi=$(python -c "import math; print($oy/math.sin(math.radians(20)))")
  f=$out/photons_${ox}_${oy}.lis
  "$SIM_TELARRAY_DIR/bin/sim_telarray" -c $model/CTAO-SCTS-01.cfg -I$model \
    -C random_state=none -C IMAGING_LIST=$f -C stars=$out/stars.lis -C altitude=2147.0 \
    -C telescope_theta=$theta -C telescope_phi=$phi -C star_photons=2000000 \
    -C camera_transmission=1.0 -C nightsky_background=all:0. -C trigger_current_limit=1e10 \
    -C telescope_random_angle=0 -C telescope_random_error=0 -C convergent_depth=0 \
    -C maximum_telescopes=1 -C show=all -C camera_filter=none \
    -C camera_config_file=$out/camera.dat -C camera_pixels=1 -C trigger_pixels=1 \
    "$SIM_TELARRAY_DIR/run9991.corsika.gz" > $f.log 2>&1 || echo "FAILED $ox $oy"
}
export -f run; export out model
printf '%s\n' "0 0" "0 1" "1 0" "0 2" "2 0" "0 3" "3 0" "0 4" "4 0" | xargs -P 6 -L 1 bash -c 'run $0 $1'
echo done
