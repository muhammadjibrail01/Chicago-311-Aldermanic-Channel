import pandas as pd, numpy as np, json
from p2lib import savej
c=pd.read_parquet("work/p2_data.parquet",columns=["sr","chan","created","speed_s","lhrs","tract","period","aw","type","alder","ym","nd"])
t=pd.read_csv("../paper1_replication/work/tract.csv",dtype={"GEOID":str}); t=t[t.analytic].reset_index(drop=True)
c["pb"]=t.pct_black.values[c.tract.values]; c["hard"]=t.hardship.values[c.tract.values]
out={}
# monthly series (all resident requests)
m=c.groupby("ym").alder.agg(["size","mean"]); out["monthly"]={"ym":m.index.tolist(),"share":(m["mean"]*100).round(3).tolist(),"n":m["size"].tolist()}
# Table 1: post-break resident requests and speed sample by channel
p=c[c.created>=pd.Timestamp("2019-11-01")]; s=p[p.speed_s].copy(); s["hours"]=np.expm1(s.lhrs)
def col(g,sp): return {"n_resident":int(len(g)),"n_speed":int(len(sp)),"share_resident":float(len(g)/len(p)*100),"median_hours":float(sp.hours.median()),"mean_lhrs":float(sp.lhrs.mean()),"mean_pct_black":float(g.pb.mean()),"mean_hardship":float(g.hard.mean()),"pct_in_majBlack_tracts":float((g.pb>60).mean()*100)}
out["table1"]={ch:col(p[p.chan==ch],s[s.chan==ch]) for ch in ("phone","digital","alderman")}; out["table1"]["all"]=col(p,s)
out["break_counts"]={"pre_nov2019_share":float(c[c.created<pd.Timestamp("2019-11-01")].alder.mean()*100),"post_share":float(p.alder.mean()*100)}
# ward-period usage table
pp=p[p.period>0]; g=pp.groupby(["period","aw"]).agg(n=("alder","size"),share=("alder","mean"),pb=("pb","mean"),hard=("hard","mean")).reset_index(); g["share"]*=100
out["wardperiod"]=g.round(3).to_dict(orient="list")
for per in (1,2):
    x=g[g.period==per]; out[f"ward_stats_p{per}"]={"min":float(x.share.min()),"p25":float(x.share.quantile(.25)),"median":float(x.share.median()),"p75":float(x.share.quantile(.75)),"max":float(x.share.max()),"sd":float(x.share.std()),"corr_black":float(x.share.corr(x.pb)),"corr_hard":float(x.share.corr(x.hard)),"top3":x.nlargest(3,"share")[["aw","share"]].values.tolist(),"bot3":x.nsmallest(3,"share")[["aw","share"]].values.tolist()}
pp=pp.assign(bq=pd.qcut(pp.pb,5,labels=False)); out["share_by_blackq"]=(pp.groupby("bq").alder.mean()*100).round(2).tolist()
pp=pp.assign(hq=pd.qcut(pp.hard,5,labels=False)); out["share_by_hardq"]=(pp.groupby("hq").alder.mean()*100).round(2).tolist()
tm=pp.groupby(["type","chan"],observed=True).size().unstack(fill_value=0); sh=tm/tm.sum()*100
x=sh[["alderman","phone"]].assign(diff=lambda z:z.alderman-z.phone).sort_values("diff"); out["type_mix"]={"over":x.tail(5).round(1).reset_index().values.tolist(),"under":x.head(4).round(1).reset_index().values.tolist()}
savej("S0_descriptives",out)
print(json.dumps(out["table1"],indent=1)); print(out["break_counts"]); print(out["ward_stats_p1"]); print(out["share_by_blackq"],out["share_by_hardq"])
