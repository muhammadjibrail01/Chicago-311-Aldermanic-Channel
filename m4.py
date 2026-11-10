import time; from p2lib import *
t0=time.time(); d=load("2019-11-01",extra=("ward_new",)); out={}
F=["ty","ym","dow","hod"]; X=["z_pct_black","z_hardship","z_pct_hisp","lwl"]
for ch in ("phone","digital","alderman"):
    r=reg(d[d.chan==ch],"lhrs",X,F,"ca"); out[f"chan_{ch}"]=pack(r,X); print(ch,{k:(round(r.b[k],3),round(r.se(k),3)) for k in X[:3]},f"n={r.n:,}",flush=True)
X1=["z_pct_black","z_hardship","z_pct_hisp","alder","digital","alder_B","digital_B","alder_H","digital_H","alder_L","digital_L","lwl"]
r=reg(d,"lhrs",X1,F,"ca"); out["M1"]=pack(r); out["M1_grad"]={"digital_B":r.lin({"z_pct_black":1,"digital_B":1}),"alder_B":r.lin({"z_pct_black":1,"alder_B":1}),"digital_H":r.lin({"z_hardship":1,"digital_H":1}),"alder_H":r.lin({"z_hardship":1,"alder_H":1})}
out["M1_wald"]=r.wald(["alder_B","alder_H","alder_L"]); print("M1 done",f"[{time.time()-t0:.0f}s]",flush=True)
X3=["alder","digital","alder_B","digital_B","alder_H","digital_H","alder_L","digital_L","lwl"]
r=reg(d,"lhrs",X3,F+["tract"],"ca"); out["M3"]=pack(r)
grid=[-1,0,1,2,3]; out["M3_gap_by_black"]={str(z):r.lin({"alder":1,"alder_B":z}) for z in grid}; out["M3_dig_by_black"]={str(z):r.lin({"digital":1,"digital_B":z}) for z in grid}
print("M3 done",f"[{time.time()-t0:.0f}s]",flush=True); savej("S6_main",out)
# M3 with ward-new FE not feasible; M3 clustered at ward level for robustness
r=reg(d,"lhrs",X3,F+["tract"],"ward_new"); out["M3_wardcl"]=pack(r); savej("S6_main",out); print("M3 ward-clustered done",f"[{time.time()-t0:.0f}s]",flush=True)
