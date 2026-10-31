"""POST-HOC sensitivity analysis (not pre-registered): primary comparisons with the three Edge-IIoTset
(ceiling) combinations dropped from the Holm family. Same procedure as analyze_full.py, from auc_per_seed.csv."""
import numpy as np, pandas as pd
A="/home/s/Documents/XAI-IOTEdge/Shortcut_Paper/05_results/full/analysis"; T="/home/s/Documents/XAI-IOTEdge/Shortcut_Paper/06_manuscript/tables"
FB=["redundant_grouped","redundant_ungrouped","entangled_0.5","entangled_1.0","transplanted"]; BASE=["eta","mi","rfe"]; N=10000
rng=np.random.default_rng(12345)
auc=pd.read_csv(f"{A}/auc_per_seed.csv"); auc=auc[auc.condition.isin(FB)&(auc.bench!="edge")]
fb=auc.groupby(["bench","model","seed","score"]).auc.mean().reset_index()
def boot(d):
    d=np.asarray(d,float); d=d[~np.isnan(d)]; bs=rng.choice(d,size=(N,len(d)),replace=True).mean(1)
    return d.mean(),np.percentile(bs,2.5),np.percentile(bs,97.5),min(1.0,2*min((bs<=0).mean(),(bs>=0).mean())+1.0/N)
def holm(ps):
    ps=np.array(ps); o=np.argsort(ps); adj=np.empty_like(ps); run=0.0
    for r,i in enumerate(o): run=max(run,(len(ps)-r)*ps[i]); adj[i]=min(1.0,run)
    return adj
rows=[]
for (b,m),g in fb.groupby(["bench","model"]):
    x=g.pivot(index="seed",columns="score",values="auc"); best=x[BASE].mean().idxmax()
    d1=boot(x["S"]-x[best]); d2=boot(x["A"]-x["S"])
    rows.append(dict(Benchmark=b,Model=m,Best=best,**{"S minus best":d1[0],"CI lo":d1[1],"CI hi":d1[2],"p1":d1[3],"A minus S":d2[0],"CI lo ":d2[1],"CI hi ":d2[2],"p2":d2[3]}))
r=pd.DataFrame(rows); r["Holm p (S)"]=holm(r.p1); r["Holm p (A)"]=holm(r.p2)
r["H1 met"]=(r["S minus best"]>=0.05)&(r["Holm p (S)"]<0.05); r["H2 met"]=(r["A minus S"]>=0.05)&(r["Holm p (A)"]<0.05)
r.drop(columns=["p1","p2"]).round(4).to_csv(f"{A}/sensitivity_no_ceiling.csv",index=False)
out=r[["Benchmark","Model","Best","S minus best","CI lo","CI hi","Holm p (S)","A minus S","CI lo ","CI hi ","Holm p (A)","H1 met","H2 met"]].round(3)
print(out.to_string(index=False)); print("H1 met:",int(r["H1 met"].sum()),"of",len(r),"; H2 met:",int(r["H2 met"].sum()),"of",len(r))
# pipe table for the appendix (two compact tables in one)
cols=["Benchmark","Model","S − best","CI low","CI high","Holm p","A − S","CI low ","CI high ","Holm p "]
t=pd.DataFrame({"Benchmark":r.Benchmark,"Model":r.Model,"S − best":r["S minus best"].round(3),"CI low":r["CI lo"].round(3),"CI high":r["CI hi"].round(3),"Holm p":r["Holm p (S)"].round(3),"A − S":r["A minus S"].round(3),"CI low ":r["CI lo "].round(3),"CI high ":r["CI hi "].round(3),"Holm p ":r["Holm p (A)"].round(3)})
L=["| "+" | ".join(t.columns)+" |","|"+"|".join(["---"]*len(t.columns))+"|"]+["| "+" | ".join(str(v) for v in row)+" |" for row in t.values]
open(f"{T}/t_sensitivity.pipe.md","w").write("\n".join(L)+"\n")
