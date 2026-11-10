import time; from p2lib import *
t0=time.time(); d=load("2019-11-01",extra=("dept",)); d["dept"]=d.dept.astype(str)
t=pd.read_csv("../paper1_replication/work/tract.csv",dtype={"GEOID":str}); t=t[t.analytic]; mu,sd=t.pct_black.mean(),t.pct_black.std(); pts=[0,33.3,66.7,100]
names={"Streets and Sanitation":"Streets and Sanitation","CDOT - Department of Transportation":"Transportation (CDOT)","DWM - Department of Water Management":"Water Management","DOB - Buildings":"Buildings"}
out={"pts":pts}
for k,lab in names.items():
    s=d[d.dept==k]; r=reg(s,"lhrs",X3,FE0+["tract"],"ca")
    out[k]={"label":lab,"n":int(r.n),"alder":{str(p):r.lin({"alder":1,"alder_B":(p-mu)/sd}) for p in pts},"digital":{str(p):r.lin({"digital":1,"digital_B":(p-mu)/sd}) for p in pts},
            "coef":{c:[float(r.b[c]),r.se(c),r.p(c)] for c in ("alder","digital","alder_B","digital_B")}}
    print(lab,{p:tuple(round(x,3) for x in out[k]["alder"][str(p)][:2]) for p in pts},f"[{time.time()-t0:.0f}s]",flush=True); savej("S11b_dept_gaps",out)
