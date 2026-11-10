import time; from p2lib import *
t0=time.time(); out={}
# --- usage models (all resident requests, post-break) ---
u=pd.read_parquet("work/p2_data.parquet",columns=["type","year","ym","dow","hod","ca","created","tract","z_hardship","z_pct_black","z_pct_hisp","alder","period","aw"])
u=u[u.created>=pd.Timestamp("2019-11-01")].copy(); u["ty"]=(u.type.astype("category").cat.codes.astype(np.int32)*10+(u.year-2019)).astype(np.int32)
u["y"]=(u.alder*100).astype("float32"); u["wp"]=(u.period.astype(int)*100+u.aw.fillna(0).astype(int)).astype(np.int32)
Z=["z_pct_black","z_hardship","z_pct_hisp"]
r=reg(u,"y",Z,["ty","ym"],"ca"); out["U1"]=pack(r); print("U1 usage (pp):",{k:round(r.b[k],2) for k in Z},f"[{time.time()-t0:.0f}s]",flush=True)
u2=u[u.period>0]; r=reg(u2,"y",Z,["ty","ym","wp"],"ca"); out["U2"]=pack(r); print("U2 within ward-period (pp):",{k:round(r.b[k],2) for k in Z},f"[{time.time()-t0:.0f}s]",flush=True)
out["usage_mean"]=float(u.y.mean()); savej("S4_usage",out); del u,u2
# --- robustness of the channel-gradient difference ---
FIXED={"Street Light Out Complaint","Alley Light Out Complaint","Traffic Signal Out Complaint","Sign Repair Request - All Other Signs","Sign Repair Request - Stop Sign","Sign Repair Request - One Way Sign","Street Light Pole Damage Complaint","Garbage Cart Maintenance","Blue Recycling Cart"}
VARIABLE={"Graffiti Removal Request","Weed Removal Request","Tree Debris Clean-Up Request","Sanitation Code Violation","Fly Dumping Complaint","Clean Vacant Lot Request","Street Cleaning Request","Yard Waste Pick-Up Request","Pothole in Street Complaint","Alley Pothole Complaint"}
X1=["z_pct_black","z_hardship","z_pct_hisp","alder","digital","alder_B","digital_B","alder_H","digital_H","alder_L","digital_L","lwl"]
F=["ty","ym","dow","hod"]; rob={}
def run(tag,d,fes=F,cl="ca"):
    r=reg(d,"lhrs",X1,fes,cl); ga=r.lin({"z_pct_black":1,"alder_B":1}); rob[tag]={"n":int(r.n),"phone":[float(r.b["z_pct_black"]),r.se("z_pct_black")],"alder":[ga[0],ga[1]],"diff":[float(r.b["alder_B"]),r.se("alder_B"),r.p("alder_B")],"pack":pack(r)}
    print(f"{tag:28s} n={r.n:>9,} phone {r.b['z_pct_black']:.3f} | alder {ga[0]:.3f} | diff {r.b['alder_B']:.3f} ({r.se('alder_B'):.3f}) [{time.time()-t0:.0f}s]",flush=True); savej("S5_robust",rob)
d=load("2019-11-01")
run("baseline (post-break)",d)
run("cluster by ward-period",d,cl="wp")
dd=d[d.period>0]; run("+ ward-period FE",dd,F+["wp"])
ty=d.type.astype(str); run("fixed-scope services",d[ty.isin(FIXED)]); run("variable-scope services",d[ty.isin(VARIABLE)])
run("other services",d[~ty.isin(FIXED|VARIABLE)])
del d,dd
d=load("2019-01-01"); run("full window (from Jan 2019)",d)
savej("S5_robust",rob)
