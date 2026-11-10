import time; from p2lib import *
t0=time.time(); d=load("2019-11-01",extra=("dept",)); d["dept"]=d.dept.astype(str)
SIGN=["Sign Repair Request - All Other Signs","Sign Repair Request - Stop Sign","Sign Repair Request - One Way Sign"]
d=d[(d.lhrs>=0.0166)&~d.type.astype(str).isin(SIGN)]      # comparable-closure sample: no sub-minute closures, no sign-repair types
t=pd.read_csv("../paper1_replication/work/tract.csv",dtype={"GEOID":str}); t=t[t.analytic]; mu,sd=t.pct_black.mean(),t.pct_black.std(); pts=[0,33.3,66.7,100]; out={"pts":pts,"n_total":int(len(d))}
names={"Streets and Sanitation":"Streets and Sanitation","CDOT - Department of Transportation":"Transportation (CDOT)","DWM - Department of Water Management":"Water Management","DOB - Buildings":"Buildings","Animal Care and Control":"Animal Care and Control"}
for k,lab in names.items():
    s=d[d.dept==k]; r=reg(s,"lhrs",X1,FE0,"ca"); rec={"label":lab,"n":int(len(s)),"n_alder":int(s.alder.sum()),"share_alder":float(100*s.alder.mean()),"pooled":pooled_summary(r)}
    if int(s.alder.sum())>=8000:
        r3=reg(s,"lhrs",X3,FE0+["tract"],"ca"); rec["alder"]={str(p):r3.lin({"alder":1,"alder_B":(p-mu)/sd}) for p in pts}; rec["alder_mean"]=[float(r3.b["alder"]),r3.se("alder"),r3.p("alder")]
    out[k]=rec; savej("S15_dept_comparable",out); p=rec["pooled"]
    print(f"{lab:24s} n={len(s):>9,} diff {p['diff'][0]:.3f} ({p['diff'][1]:.3f}) | gaps "+(", ".join(f"{q}%: {rec['alder'][str(q)][0]:.3f} ({rec['alder'][str(q)][1]:.3f})" for q in pts) if "alder" in rec else "skipped"),f"[{time.time()-t0:.0f}s]",flush=True)
