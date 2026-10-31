#!/bin/bash
PY="/home/s/Documents/XAI-IOTEdge/Journal MDPI sensors/.venv/bin/python"
cd /home/s/Documents/XAI-IOTEdge/Shortcut_Paper/04_code
OUT=../05_results/full
COMBOS="ciciot:lgbm ciciot:rf ciciot:mlp edge:lgbm edge:rf edge:mlp ciciomt:lgbm ciciomt:rf ciciomt:mlp"
for mode in calibrate evaluate; do
  for c in $COMBOS; do b=${c%%:*}; m=${c##*:}
    "$PY" full_study.py --mode $mode --bench $b --model $m > $OUT/stdout_${mode}_${b}_${m}.txt 2>&1
  done
done
"$PY" analyze_full.py --dir $OUT > $OUT/stdout_analysis.txt 2>&1
echo finished > $OUT/DONE
