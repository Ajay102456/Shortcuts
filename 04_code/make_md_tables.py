"""Pipe-table exports for the manuscript, from analysis CSVs only."""
import pandas as pd, numpy as np
A="/home/s/Documents/XAI-IOTEdge/Shortcut_Paper/05_results/full/analysis"; O="/home/s/Documents/XAI-IOTEdge/Shortcut_Paper/06_manuscript/tables"
def md(df,fmt="{:.3f}",name=None,idx=False):
    d=df.reset_index() if idx else df.copy()
    cols=list(d.columns); L=["| "+" | ".join(map(str,cols))+" |","|"+"|".join(["---"]*len(cols))+"|"]
    for _,r in d.iterrows():
        L.append("| "+" | ".join("n/a" if (isinstance(v,float) and np.isnan(v)) else (fmt.format(v) if isinstance(v,(float,np.floating)) else str(v)) for v in r)+" |")
    open(f"{O}/{name}.pipe.md","w").write("\n".join(L)+"\n")
sc=["S","C","A","T","eta","mi","rfe"]
p=pd.read_csv(f"{A}/primary_comparisons.csv")
q=p[["bench","model","n_seeds","auc_S","auc_best_baseline","diff_S_minus_baseline","ci_lo","ci_hi","p_holm","auc_A","diff_A_minus_S","ci2_lo","ci2_hi","p2_holm"]].copy()
q.columns=["Benchmark","Model","Seeds","AUC S","AUC best baseline (MI)","S − MI","CI low","CI high","Holm p","AUC A","A − S","CI low ","CI high ","Holm p "]
q1=q.iloc[:,:9]; md(q1,name="t_primary")
q2=q[["Benchmark","Model","AUC A","A − S","CI low ","CI high ","Holm p "]].copy(); q2.columns=["Benchmark","Model","AUC A","A − S","CI low","CI high","Holm p"]; md(q2,name="t_primary2")
for fam in ["familyA","familyB"]:
    d=pd.read_csv(f"{O}/auc_{fam}.csv")[["bench","model"]+sc]; d.columns=["Benchmark","Model"]+sc; md(d,name=f"t_{fam}")
pc=pd.read_csv(f"{O}/auc_per_condition.csv")[["bench","condition","S","A","C","eta","mi","rfe"]]; pc.columns=["Benchmark","Condition","S","A","C","eta","MI","RFE"]; md(pc,name="t_percond")
tp=pd.read_csv(f"{O}/tpr_all_plants.csv")[["bench","model"]+sc]; tp.columns=["Benchmark","Model"]+sc; md(tp,name="t_tpr")
t2=pd.read_csv(f"{O}/tier2.csv"); t2=t2[t2.score.isin(["S","C","A","eta","mi","rfe"])]
a=t2.pivot(index="model",columns="score",values="auc")[["S","C","A","eta","mi","rfe"]].rename(columns={"mi":"MI","rfe":"RFE"}); md(a,name="t_tier2_auc",idx=True)
b=t2.pivot(index="model",columns="score",values="tpr_at_fa5")[["S","C","A","eta","mi","rfe"]].rename(columns={"mi":"MI","rfe":"RFE"}); md(b,name="t_tier2_tpr",idx=True)
f=pd.read_csv(f"{A}/clean_false_alarms.csv"); f["over"]=f.fa_mean>0.05
g=f.groupby("score").agg(min_fa=("fa_mean","min"),max_fa=("fa_mean","max"),cells=("fa_mean","size"),over_0_05=("over","sum")).reset_index(); g.columns=["Signal","Min FA","Max FA","Cells","Cells above 0.05"]; md(g,name="t_fa_summary")
fp=f.pivot_table(index=["bench","model"],columns="score",values="fa_mean")[sc].reset_index(); fp.columns=["Benchmark","Model"]+sc; md(fp,name="t_fa_full")
d=pd.read_csv(f"{A}/decoys.csv"); d["cell"]=d.seeds_flagged.astype(str)+"/"+d.n_seeds.astype(str)
dd=d.pivot_table(index=["bench","model","decoy"],columns="score",values="cell",aggfunc="first").reset_index(); dd.columns=["Benchmark","Model","Decoy"]+list(dd.columns[3:]); md(dd,name="t_decoys")
tr=pd.read_csv(f"{A}/clean_flagged_groups_tier3.csv")[["bench","model","members","n_seeds","mean_S","mean_C"]]; tr.columns=["Benchmark","Model","Group members","Seeds flagged","Mean S","Mean C"]; tr["Group members"]=tr["Group members"].str.replace("|"," + ",regex=False); md(tr,name="t_tier3")
print("ok")
