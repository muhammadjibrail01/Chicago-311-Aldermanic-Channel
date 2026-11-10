import time; from p2lib import *
t0=time.time(); d=load("2019-11-01"); F=["ty","ym","dow","hod","tract"]
X3=["alder","digital","alder_B","digital_B","alder_H","digital_H","alder_L","digital_L","lwl"]
r=reg(d,"lhrs",X3,F,"ca"); t=pd.read_csv("../paper1_replication/work/tract.csv",dtype={"GEOID":str}); t=t[t.analytic]; mu,sd=t.pct_black.mean(),t.pct_black.std()
pts=[0,33.3,66.7,100]; out={"mu":mu,"sd":sd,"pts":pts,"alder":{},"digital":{}}
for p in pts:
    z=(p-mu)/sd; out["alder"][str(p)]=r.lin({"alder":1,"alder_B":z}); out["digital"][str(p)]=r.lin({"digital":1,"digital_B":z})
print(out); savej("S7_gap_pcts",out); print(f"[{time.time()-t0:.0f}s]")
