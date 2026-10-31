"""POST-HOC, exploratory (not pre-registered): inspect Tier 2 artifact groups in existing evaluation output. No reruns."""
import pandas as pd, glob
R="/home/s/Documents/XAI-IOTEdge/Shortcut_Paper/05_results/full"
ev=pd.concat([pd.read_csv(f) for f in glob.glob(f"{R}/group_scores_edge_*_evaluation.csv")])
t=ev[ev.condition=="tier2_real"]
print("planted-group count per seed (min,max):",t.groupby(["model","seed"]).planted.sum().agg(["min","max"]).tolist())
print("groups per run (min,max):",t.groupby(["model","seed"]).size().agg(["min","max"]).tolist())
p=t[t.planted]
print(p.groupby("model")[["S","C","A","eta","mi","rfe"]].mean().round(3).to_string())
print("example planted members:",p.members.value_counts().head(8).to_string())
tau=pd.read_csv(f"{R}/analysis/clean_false_alarms.csv").query("bench=='edge'").pivot(index="model",columns="score",values="tau").round(3)
print(tau.to_string())
