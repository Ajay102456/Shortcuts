"""Figures from exported analysis CSVs only (plus a schematic). No hand-typed results."""
import subprocess, pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
A="/home/s/Documents/XAI-IOTEdge/Shortcut_Paper/05_results/full/analysis"; O="/home/s/Documents/XAI-IOTEdge/Shortcut_Paper/06_manuscript/figures"
plt.rcParams.update({"font.size":9,"axes.spines.top":False,"axes.spines.right":False})
def save(fig,n):
    fig.savefig(f"{O}/{n}.png",dpi=200); fig.savefig(f"{O}/{n}.pdf")
# Fig 1: system diagram
dot='''digraph G{rankdir=LR;node[shape=box,style="rounded,filled",fillcolor="#eef3fb",fontname="Helvetica",fontsize=10];edge[fontname="Helvetica",fontsize=8];
raw[label="Public benchmarks\\nCICIoT2023, Edge-IIoTset,\\nCICIoMT2024"];pool[label="Per-seed stratified\\nsample + split"];
plant[label="Shortcut injection\\n(Family A, Family B,\\nhard decoys, clean)",fillcolor="#fdeedd"];
grp[label="Feature grouping\\n|Pearson r| average linkage,\\ncut 0.10"];
mod[label="Models\\nLightGBM, RF, MLP"];
sig[label="Group-level signals\\nS sufficiency, C SHAP share,\\nA=CxS, R necessity, T transfer",fillcolor="#e6f4ea"];
base[label="Baselines\\ncorrelation ratio,\\nmutual information, RFE",fillcolor="#e6f4ea"];
thr[label="Frozen threshold\\n95th pct of clean\\ncalibration groups"];
ev[label="Detection AUC, TPR at 5% FA,\\nclean false alarms, decoys"];
st[label="Paired bootstrap + Holm\\n(9 benchmark x model\\ncomparisons)"];
raw->pool->plant->grp->mod->sig;grp->base;sig->thr;base->thr;thr->ev->st;
{rank=same;sig;base}}'''
open(f"{O}/fig1_system.dot","w").write(dot)
subprocess.run(["dot","-Tpng","-Gdpi=200",f"{O}/fig1_system.dot","-o",f"{O}/fig1_system.png"],check=True); subprocess.run(["dot","-Tpdf",f"{O}/fig1_system.dot","-o",f"{O}/fig1_system.pdf"],check=True)
# Fig 3: Family B AUC heatmap
fb=pd.read_csv("/home/s/Documents/XAI-IOTEdge/Shortcut_Paper/06_manuscript/tables/auc_familyB.csv")
sc=["S","C","A","T","eta","mi","rfe"]; fb["row"]=fb.bench+" / "+fb.model
M=fb.set_index("row")[sc]
fig,ax=plt.subplots(figsize=(6.2,3.6)); im=ax.imshow(M.values.astype(float),vmin=0.6,vmax=1,cmap="viridis",aspect="auto")
ax.set_xticks(range(len(sc)));ax.set_xticklabels(sc);ax.set_yticks(range(len(M)));ax.set_yticklabels(M.index)
for i in range(M.shape[0]):
    for j in range(M.shape[1]):
        v=M.values[i,j]; ax.text(j,i,"n/a" if np.isnan(v) else f"{v:.2f}",ha="center",va="center",color="w" if (np.isnan(v) or v<0.85) else "k",fontsize=7)
plt.colorbar(im,label="Mean detection AUC (Family B)"); fig.tight_layout(); save(fig,"fig3_familyB_heatmap"); plt.close()
# Fig 4: S minus best baseline with CI
p=pd.read_csv(f"{A}/primary_comparisons.csv"); p["row"]=p.bench+" / "+p.model
fig,ax=plt.subplots(figsize=(5.6,3.4)); y=np.arange(len(p))
ax.errorbar(p.diff_S_minus_baseline,y,xerr=[p.diff_S_minus_baseline-p.ci_lo,p.ci_hi-p.diff_S_minus_baseline],fmt="o",capsize=2,label="S minus best baseline")
ax.errorbar(p.diff_A_minus_S,y+0.2,xerr=[p.diff_A_minus_S-p.ci2_lo,p.ci2_hi-p.diff_A_minus_S],fmt="s",capsize=2,label="A minus S")
ax.axvline(0.05,ls="--",c="k",lw=0.8);ax.axvline(0,c="grey",lw=0.6);ax.set_yticks(y);ax.set_yticklabels(p.row);ax.invert_yaxis()
ax.set_xlabel("Difference in mean AUC (Family B); dashed = pre-registered 0.05 margin");ax.legend(fontsize=7,loc="lower right");fig.tight_layout();save(fig,"fig4_primary_differences");plt.close()
# Fig 5: Tier 2
t=pd.read_csv("/home/s/Documents/XAI-IOTEdge/Shortcut_Paper/06_manuscript/tables/tier2.csv"); t=t[t.score.isin(["S","C","A","eta","mi","rfe"])]
pv=t.pivot(index="score",columns="model",values="auc").reindex(["S","C","A","eta","mi","rfe"])
fig,ax=plt.subplots(figsize=(5,3));pv.plot.bar(ax=ax,width=0.75);ax.axhline(0.5,c="grey",ls=":");ax.set_ylabel("AUC on documented artifacts");ax.set_xlabel("");ax.legend(title="model",fontsize=7);fig.tight_layout();save(fig,"fig5_tier2");plt.close()
# Fig 6: false alarms
f=pd.read_csv(f"{A}/clean_false_alarms.csv");f["row"]=f.bench+"/"+f.model
fig,ax=plt.subplots(figsize=(6.4,3.2))
for s,m in zip(["S","C","A","T","eta","mi","rfe"],["o","s","^","v","D","P","x"]):
    d=f[f.score==s]; ax.scatter(range(len(d)),d.fa_mean,marker=m,label=s,s=22)
rows=sorted(f.row.unique());ax.set_xticks(range(len(rows)));ax.set_xticklabels(rows,rotation=40,ha="right",fontsize=7)
ax.axhline(0.05,c="k",ls="--",lw=0.8);ax.set_ylabel("Clean-control false-alarm rate");ax.legend(ncol=7,fontsize=6,loc="upper center",bbox_to_anchor=(0.5,1.15));fig.tight_layout();save(fig,"fig6_false_alarms");plt.close()
print("ok")
