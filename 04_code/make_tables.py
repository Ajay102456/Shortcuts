"""Exports manuscript tables from analysis CSVs. No hand-typed numbers."""
import pandas as pd, numpy as np
A="/home/s/Documents/XAI-IOTEdge/Shortcut_Paper/05_results/full/analysis"
O="/home/s/Documents/XAI-IOTEdge/Shortcut_Paper/06_manuscript/tables"
auc=pd.read_csv(f"{A}/auc_per_seed.csv")
FA=["exact_copy","plant_weak","plant_medium","plant_strong"]
FB=["redundant_grouped","redundant_ungrouped","entangled_0.5","entangled_1.0","transplanted"]
sc=["S","C","A","T","R","eta","mi","rfe"]
def fam(conds,name):
    x=auc[auc.condition.isin(conds)].groupby(["bench","model","seed","score"]).auc.mean().reset_index()
    t=x.groupby(["bench","model","score"]).auc.mean().unstack().reindex(columns=sc).round(3)
    t.to_csv(f"{O}/auc_{name}.csv"); open(f"{O}/auc_{name}.md","w").write(t.to_string())
fam(FA,"familyA"); fam(FB,"familyB")
fam([c for c in FB if c!="transplanted"],"familyB_excl_transplant")
# per condition, S vs mi vs A, mean over models
pc=auc[auc.score.isin(["S","A","C","mi","eta","rfe"])].groupby(["bench","condition","score"]).auc.mean().unstack().round(3)
pc.to_csv(f"{O}/auc_per_condition.csv"); open(f"{O}/auc_per_condition.md","w").write(pc.to_string())
# tpr at 5% FA, per family
tp=auc[auc.condition.isin(FA+FB)].groupby(["bench","model","score"]).tpr_at_fa5.mean().unstack().reindex(columns=["S","C","A","T","eta","mi","rfe"]).round(3)
tp.to_csv(f"{O}/tpr_all_plants.csv"); open(f"{O}/tpr_all_plants.md","w").write(tp.to_string())
t2=auc[auc.condition=="tier2_real"].groupby(["bench","model","score"])[["auc","tpr_at_fa5"]].mean().round(3)
t2.to_csv(f"{O}/tier2.csv"); open(f"{O}/tier2.md","w").write(t2.to_string())
print(open(f"{O}/auc_familyA.md").read());print();print(open(f"{O}/auc_familyB.md").read());print();print(open(f"{O}/auc_per_condition.md").read())
print(open(f"{O}/tpr_all_plants.md").read())
