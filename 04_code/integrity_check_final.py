"""Stage 4.5: asserts every numeric claim in the manuscript against exported result files. Writes a report."""
import pandas as pd, numpy as np, glob, re
R="/home/s/Documents/XAI-IOTEdge/Shortcut_Paper/05_results/full"; A=f"{R}/analysis"; T="/home/s/Documents/XAI-IOTEdge/Shortcut_Paper/06_manuscript/tables"
out=[]; fails=0
def chk(name,cond,detail=""):
    global fails
    out.append(f"- {'PASS' if cond else 'FAIL'}: {name} {detail}")
    if not cond: fails+=1
p=pd.read_csv(f"{A}/primary_comparisons.csv").set_index(["bench","model"])
chk("H1: S beats baseline in 0 of 9",(~p.S_beats_baseline).all() and len(p)==9)
chk("H2: A adds in 0 of 9",(~p.shap_concentration_adds).all())
chk("best baseline is MI in 9 of 9",(p.best_baseline=="mi").all())
chk("largest S-MI diff 0.045 (ciciomt mlp)",abs(p.diff_S_minus_baseline.max()-0.045)<5e-4 and p.diff_S_minus_baseline.idxmax()==("ciciomt","mlp"),f"{p.diff_S_minus_baseline.max():.4f}")
chk("S-MI ciciomt lgbm .016, rf .019",abs(p.loc[("ciciomt","lgbm")].diff_S_minus_baseline-0.016)<6e-4 and abs(p.loc[("ciciomt","rf")].diff_S_minus_baseline-0.019)<6e-4)
chk("S-MI ciciot lgbm and rf -0.013",all(abs(p.loc[("ciciot",m)].diff_S_minus_baseline+0.013)<6e-4 for m in ("lgbm","rf")))
chk("largest A-S 0.048 (ciciot rf)",abs(p.diff_A_minus_S.max()-0.048)<6e-4 and p.diff_A_minus_S.idxmax()==("ciciot","rf"))
chk("A<S for all three ciciomt",all(p.loc[("ciciomt",m)].diff_A_minus_S<0 for m in ("lgbm","mlp","rf")))
chk("A<S for edge lgbm and mlp",all(p.loc[("edge",m)].diff_A_minus_S<0 for m in ("lgbm","mlp")))
chk("seeds 30/15/30",list(p.n_seeds)==[30,15,30,30,15,30,30,15,30])
fa=pd.read_csv(f"{T}/auc_familyA.csv"); fb=pd.read_csv(f"{T}/auc_familyB.csv")
chk("Family A S range .960-1.000",abs(fa.S.min()-0.960)<1e-3 and abs(fa.S.max()-1.0)<1e-3)
mi=fb.groupby("bench").mi.mean()
chk("Family B MI: ciciot .911, ciciomt .954, edge>=.999",abs(mi["ciciot"]-.911)<2e-3 and abs(mi["ciciomt"]-.954)<2e-3 and fb[fb.bench=="edge"].mi.min()>=0.999)
lower=(fb.C<fb.S).sum(); chk("C<S in 8 of 9 B cells; exception ciciot rf",lower==8 and (fb[~(fb.C<fb.S)][["bench","model"]].values.tolist()==[["ciciot","rf"]]))
pc=pd.read_csv(f"{T}/auc_per_condition.csv").set_index(["bench","condition"])
w=pc.loc[("ciciot","plant_weak")]; chk("weak plant ciciot S .994 MI .799 eta .794",abs(w.S-.994)<1e-3 and abs(w.mi-.799)<1e-3 and abs(w.eta-.794)<1e-3)
t=pc.loc[("ciciot","transplanted")]; chk("transplanted S .507 MI .553 A .672 eta .954",abs(t.S-.507)<1e-3 and abs(t.mi-.553)<1e-3 and abs(t.A-.672)<1e-3 and abs(t.eta-.954)<1e-3)
for m in ("ciciomt","ciciot"):
    r=pc.loc[(m,"redundant_ungrouped")]; chk(f"redundant_ungrouped A<S ({m})",r.A<r.S)
tp=pd.read_csv(f"{T}/tpr_all_plants.csv")
chk("TPR S .875-1.000, eta .25-.34",abs(tp.S.min()-.875)<1e-3 and abs(tp.S.max()-1.0)<1e-3 and abs(tp[tp.bench!='x'].eta.min()-.25)<1e-3 and abs(tp.eta.max()-.339)<1e-3)
f=pd.read_csv(f"{A}/clean_false_alarms.csv")
chk("FA range .028-.073, n=60, 28 above .05",abs(f.fa_mean.min()-.028)<1e-3 and abs(f.fa_mean.max()-.0733)<1e-3 and len(f)==60 and (f.fa_mean>.05).sum()==28,f"{(f.fa_mean>.05).sum()}")
g=lambda b,m,s:f[(f.bench==b)&(f.model==m)&(f.score==s)].fa_mean.iloc[0]
chk("FA C edge rf .073, C ciciot rf .063, T ciciot lgbm .069, A ciciomt mlp .059",abs(g("edge","rf","C")-.073)<1e-3 and abs(g("ciciot","rf","C")-.063)<1e-3 and abs(g("ciciot","lgbm","T")-.069)<1e-3 and abs(g("ciciomt","mlp","A")-.059)<1e-3)
chk("RFE FA .028-.030 everywhere",f[f.score=="rfe"].fa_mean.between(.027,.0305).all())
d=pd.read_csv(f"{A}/decoys.csv")
def dd(s): x=d[d.score==s]; return (x.seeds_flagged>0).sum(),len(x),x.seeds_flagged.sum(),x.n_seeds.sum()
chk("decoys S 3/27 cells 64/675",dd("S")==(3,27,64,675),str(dd("S")))
chk("decoys A 1/27 cells 28/675",dd("A")==(1,27,28,675),str(dd("A")))
chk("decoys T 9/18 cells 109/450",dd("T")==(9,18,109,450),str(dd("T")))
sa=d[(d.score.isin(["S","A"]))&(d.seeds_flagged>0)]; chk("S/A decoy flags all decoy_b90",(sa.decoy=="decoy_b90").all())
x=lambda b,m,dec,s:int(d[(d.bench==b)&(d.model==m)&(d.decoy==dec)&(d.score==s)].seeds_flagged.iloc[0])
chk("specific decoy counts (15,25,24,28; T mlp ciciot decoy_a 15)",x("ciciomt","mlp","decoy_b90","S")==15 and x("edge","lgbm","decoy_b90","S")==25 and x("edge","rf","decoy_b90","S")==24 and x("edge","rf","decoy_b90","A")==28 and x("ciciot","mlp","decoy_a","T")==15)
t2=pd.read_csv(f"{T}/tier2.csv").set_index(["model","score"])
chk("Tier2 eta AUC .990-.991, TPR 1.0",all(0.989<=t2.loc[(m,"eta")].auc<=0.9915 and t2.loc[(m,"eta")].tpr_at_fa5==1.0 for m in ("lgbm","mlp","rf")))
chk("Tier2 S/C/A/MI/RFE TPR 0.0",all(t2.loc[(m,s)].tpr_at_fa5==0.0 for m in ("lgbm","mlp","rf") for s in ("S","C","A","mi","rfe")))
chk("Tier2 S AUC .732-.845",abs(min(t2.loc[(m,"S")].auc for m in ("lgbm","mlp","rf"))-.732)<1e-3 and abs(max(t2.loc[(m,"S")].auc for m in ("lgbm","mlp","rf"))-.845)<1e-3)
# run counts and failures
cnt={}
for fl in glob.glob(f"{R}/run_log_*_evaluation.csv"):
    l=pd.read_csv(fl); cnt[fl.split("run_log_")[1][:-15]]=(int((l.status=="ok").sum()),int(l.status.astype(str).str.startswith("FAILED").sum()))
chk("run counts 390/195/390 etc, 0 failures",cnt=={ 'ciciot_lgbm':(390,0),'ciciot_rf':(390,0),'ciciot_mlp':(195,0),'edge_lgbm':(390,0),'edge_rf':(390,0),'edge_mlp':(195,0),'ciciomt_lgbm':(360,0),'ciciomt_rf':(360,0),'ciciomt_mlp':(180,0)},str(cnt))
cal=[pd.read_csv(fl) for fl in glob.glob(f"{R}/run_log_*_calibration.csv")]
chk("calibration 9 logs x 80 ok, 0 failed",len(cal)==9 and all((c.status=="ok").sum()==80 for c in cal))
# groups per run
for b,lo,hi in (("ciciot",32,33),("edge",35,38),("ciciomt",33,34)):
    e=pd.read_csv(f"{R}/group_scores_{b}_lgbm_evaluation.csv",usecols=["condition","n_groups"]); c=e[e.condition=="clean"].n_groups
    chk(f"groups per clean run {b} {lo}-{hi}",c.min()==lo and c.max()==hi,f"{c.min()}-{c.max()}")
e2=pd.concat([pd.read_csv(fl) for fl in glob.glob(f"{R}/group_scores_edge_*_evaluation.csv")]); t2g=e2[e2.condition=="tier2_real"]
chk("Edge tier2: 4 planted groups/run, 39-42 groups",t2g.groupby(["model","seed"]).planted.sum().eq(4).all() and t2g.groupby(["model","seed"]).size().between(39,42).all())
rep="# Stage 4.5 final integrity check (numbers), 2026-10-31\n\n"+"\n".join(out)+f"\n\nResult: {len(out)-fails} PASS, {fails} FAIL\n"
open(f"{R}/integrity_gate_4_5_numbers.md","w").write(rep); print(rep)
