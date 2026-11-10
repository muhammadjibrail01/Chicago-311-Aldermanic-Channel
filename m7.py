import time; from p2lib import *
t0=time.time()
cols=["sr","type","chan","year","ym","dow","hod","ca","lwl","speed_s","created","tract","z_hardship","z_pct_black","z_pct_hisp","alder","digital","nd"]
d=pd.read_parquet("work/p2_data.parquet",columns=cols); d=d[(d.created>=pd.Timestamp("2019-11-01"))&d.nd].copy()
st=pd.read_parquet("work/core_request_file.parquet",columns=["sr","status"]); d=d.merge(st,on="sr",how="left"); del st
q=pd.read_parquet("work/quality_flags.parquet"); d=d.merge(q,on="sr",how="left"); del q
d["canceled"]=(100*(d.status=="Canceled")).astype("float32"); d["unresolved"]=(100*(d.status=="Open")).astype("float32")
d["rr30"]=(100*d.rr30).astype("float32"); d["rr90"]=(100*d.rr90).astype("float32")
d=add_inter(d); print(f"quality sample (post-break, resident non-duplicate): {len(d):,} [{time.time()-t0:.0f}s]",flush=True)
out={}
for y,lab in (("canceled","Canceled"),("unresolved","Still unresolved"),("rr30","Re-reported within 30 days"),("rr90","Re-reported within 90 days")):
    s=d[d[y].notna()]
    means={ch:float(s[s.chan==ch][y].mean()) for ch in ("phone","digital","alderman")}
    r=reg(s,y,X1,FE0,"ca"); pooled=pooled_summary(r)
    r3=reg(s,y,X3,FE0+["tract"],"ca")
    out[y]={"label":lab,"means":means,"pooled":pooled,"within":pack(r3,["alder","digital","alder_B","digital_B"]),"n":int(len(s))}
    print(y,"means",{k:round(v,2) for k,v in means.items()},"| within-tract alder gap %.3f (%.3f), digital %.3f (%.3f), alder×Black %.3f (%.3f) | pooled gradients phone %.3f alder %.3f diff %.3f (%.3f)"%(r3.b["alder"],r3.se("alder"),r3.b["digital"],r3.se("digital"),r3.b["alder_B"],r3.se("alder_B"),pooled["phone"][0],pooled["alder"][0],pooled["diff"][0],pooled["diff"][1]),f"[{time.time()-t0:.0f}s]",flush=True)
    savej("S10_quality",out)
