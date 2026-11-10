import time; from p2lib import *
t0=time.time(); d=load("2019-11-01",extra=("dept",)); d["dept"]=d.dept.astype(str); out={}
names={"Streets and Sanitation":"Streets and Sanitation","CDOT - Department of Transportation":"Transportation (CDOT)","DWM - Department of Water Management":"Water Management","DOB - Buildings":"Buildings","Animal Care and Control":"Animal Care and Control"}
for k,lab in names.items():
    s=d[d.dept==k]; nal=int(s.alder.sum()); r=reg(s,"lhrs",X1,FE0,"ca"); pooled=pooled_summary(r)
    rec={"label":lab,"n":int(len(s)),"n_alder":nal,"share_alder":float(100*s.alder.mean()),"pooled":pooled}
    if nal>=8000:
        r3=reg(s,"lhrs",X3,FE0+["tract"],"ca"); rec["within"]=pack(r3,["alder","digital","alder_B"])
    out[k]=rec; savej("S11_departments",out)
    print(f"{lab:24s} n={len(s):>9,} ald={nal:>7,} | phone {pooled['phone'][0]:.3f} alder {pooled['alder'][0]:.3f} diff {pooled['diff'][0]:.3f} ({pooled['diff'][1]:.3f})"+(f" | within-tract gap {r3.b['alder']:.3f} ({r3.se('alder'):.3f})" if nal>=8000 else " | within-tract: skipped (few aldermanic requests)"),f"[{time.time()-t0:.0f}s]",flush=True)
