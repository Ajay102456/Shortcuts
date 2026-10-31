| Step | Action | Evidence in this study |
|---|---|---|
| 1 | Compute class-dependence statistics per feature group (correlation ratio and mutual information) on the training split and flag groups above a threshold set on clean groups | The correlation ratio flagged all four documented Edge-IIoTset artifact groups, and mutual information was the strongest baseline on planted shortcuts |
| 2 | Inspect each flagged group: does the field identify the capture process, the tool or the protocol implementation rather than attack behaviour? | The four documented fields are protocol-identity columns |
| 3 | Run a hard-decoy control: add informative columns that are not shortcuts and check that they are not flagged at the same threshold | Sufficiency flagged the 90th-percentile decoy in 3 of 27 cells, and the transfer gap flagged decoys in 9 of 18 cells |
| 4 | Optionally add a model-based score (sufficiency) as a second view, and treat its flags as unconfirmed | Sufficiency flags natural features on clean data (for example Tot sum) and missed the documented artifacts |
| 5 | Do not use the transfer gap as confirmation, and report ceiling effects where scores saturate | Edge-IIoTset scores reached 0.998 to 1.000 for several signals |
| 6 | Set thresholds on separate seeds, report the clean false-alarm rate, and fix the protocol before the evaluation runs | The 5% budget was met only approximately (28 of 60 cells above 0.05) |
