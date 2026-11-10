import time; from p2lib import *
t0=time.time(); SIGN=["Sign Repair Request - All Other Signs","Sign Repair Request - Stop Sign","Sign Repair Request - One Way Sign"]
d=load("2019-11-01"); d=d[(d.lhrs>=0.0166)&~d.type.astype(str).isin(SIGN)].copy()
t=pd.read_csv("../paper1_replication/work/tract.csv",dtype={"GEOID":str}); t=t[t.analytic]; mu,sd=t.pct_black.mean(),t.pct_black.std(); pts=[0,33.3,66.7,100]; out={"pts":pts}
r3=reg(d,"lhrs",X3,FE0+["tract"],"ca"); out["pooled_within"]={"n":int(r3.n),"coef":{c:[float(r3.b[c]),r3.se(c),r3.p(c)] for c in ("alder","digital","alder_B","digital_B")},"alder":{str(p):r3.lin({"alder":1,"alder_B":(p-mu)/sd}) for p in pts},"digital":{str(p):r3.lin({"digital":1,"digital_B":(p-mu)/sd}) for p in pts}}
print("pooled comparable-closure within-tract gaps (aldermanic):",{p:tuple(round(x,3) for x in out["pooled_within"]["alder"][str(p)][:2]) for p in pts},f"[{time.time()-t0:.0f}s]",flush=True); savej("S16_comparable_pooled",out)
q=pd.read_parquet("work/quality_flags.parquet"); d=d.merge(q,on="sr",how="left"); del q
for y in ("rr30","rr90"):
    s=d[d[y].notna()].copy(); s["y"]=(100*s[y]).astype("float32"); r=reg(s,"y",X3,FE0+["tract"],"ca")
    out[y]={"n":int(r.n),"means":{ch:float(s[s.chan==ch].y.mean()) for ch in ("phone","digital","alderman")},"coef":{c:[float(r.b[c]),r.se(c),r.p(c)] for c in ("alder","digital","alder_B")}}
    print(y,"means",{k:round(v,2) for k,v in out[y]["means"].items()},"| alder gap %.3f (%.3f), web %.3f"%(r.b["alder"],r.se("alder"),r.b["digital"]),f"[{time.time()-t0:.0f}s]",flush=True); savej("S16_comparable_pooled",out)
