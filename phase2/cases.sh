#!/bin/bash
# Phase 2 validation cases (simulation models 7.0.0), in three streams.
HERE=$(cd "$(dirname "$0")" && pwd)
r="$HERE/run_case.sh"
illuminator=(--number_of_events 10 --flasher_photons 1000000000)
flashers() {
  $r flasher-msts04-flashcam flasher --light_source MSFx-FlashCam --site South \
    --telescopes MSTS-04 --number_of_events 100 --flasher_photons 1000000
  $r flasher-mstn07-nectarcam flasher --light_source MSFx-NectarCam --site North \
    --telescopes MSTN-07 --number_of_events 100 --flasher_photons 1000000
  $r flasher-lstn01 flasher --light_source LSFN-design --site North --telescopes LSTN-01 \
    --number_of_events 100 --flasher_photons 3000000
  $r flasher-lsts01 flasher --light_source LSFS-design --site South --telescopes LSTS-01 \
    --number_of_events 100 --flasher_photons 3000000
}
illuminators_north() {
  $r illuminator-illn01-mstn07 illuminator --light_source ILLN-01 --site North \
    --telescope MSTN-07 "${illuminator[@]}"
  $r illuminator-illn02-lstn01 illuminator --light_source ILLN-02 --site North \
    --telescope LSTN-01 "${illuminator[@]}"
  $r illuminator-ills03-msts07 illuminator --light_source ILLS-03 --site South \
    --telescope MSTS-07 "${illuminator[@]}"
}
illuminators_south() {
  $r illuminator-ills03-ssts17 illuminator --light_source ILLS-03 --site South \
    --telescope SSTS-17 "${illuminator[@]}"
  $r illuminator-ills03-ssts17-400nm illuminator --light_source ILLS-03 --site South \
    --telescope SSTS-17 --overwrite_model_parameters "$HERE/wavelength_400.yml" \
    "${illuminator[@]}"
  $r illuminator-ills03-lsts04 illuminator --light_source ILLS-03 --site South \
    --telescope LSTS-04 "${illuminator[@]}"
}
off_axis() {
  # Vertical telescopes, the source 600 m (400 m) above them, off axis; positions are relative
  # to the array centre (LSTN-01 at -70.91, -52.35, 45.0 m; SSTS-17 at 212.45, -799.49, 56.25 m).
  # 2.0 deg (LSTN-01 camera rotated).
  $r illuminator-lstn01-offaxis illuminator --light_source ILLN-02 --site North \
    --telescope LSTN-01 --light_source_position -55.91 -37.35 645.0 "${illuminator[@]}"
  # 1.7 deg, dual-mirror camera frame.
  $r illuminator-ssts17-offaxis illuminator --light_source ILLS-03 --site South \
    --telescope SSTS-17 --light_source_position 222.45 -805.49 456.25 "${illuminator[@]}"
}
case ${1:-all} in
  off_axis) off_axis ;;
  flashers) flashers ;;
  north) illuminators_north ;;
  south) illuminators_south ;;
  *) flashers & illuminators_north & illuminators_south & wait ;;
esac
