#!/bin/bash
PY="/home/s/Documents/XAI-IOTEdge/Journal MDPI sensors/.venv/bin/python"
cd /home/s/Documents/XAI-IOTEdge/Shortcut_Paper/04_code
OUT=../05_results/full
for b in ciciot edge ciciomt; do "$PY" full_study.py --mode prep --bench $b; done > $OUT/stdout_prep.txt 2>&1
for bm in "ciciot lgbm" "ciciot rf" "ciciot mlp" "edge lgbm" "ciciomt lgbm"; do set -- $bm; "$PY" full_study.py --mode timing --bench $1 --model $2; done > $OUT/stdout_timing.txt 2>&1
echo finished >> $OUT/stdout_timing.txt
