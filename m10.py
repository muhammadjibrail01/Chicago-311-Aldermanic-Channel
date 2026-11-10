import time; from p2lib import *
t0=time.time(); d=load("2019-11-01",extra=("dept",)); d["dept"]=d.dept.astype(str); ty=d.type.astype(str)
SIGN=["Sign Repair Request - All Other Signs","Sign Repair Request - Stop Sign","Sign Repair Request - One Way Sign"]
sub=d.lhrs<0.0166          # completed within about one minute of creation (administrative closure)
out={"share_subminute":{ch:float(100*sub[d.chan==ch].mean()) for ch in ("phone","digital","alderman")},"share_subminute_sign":{ch:float(100*sub[(d.chan==ch)&ty.isin(SIGN)].mean()) for ch in ("phone","digital","alderman")},
     "sign_share_of_cdot":float(100*ty.isin(SIGN)[d.dept=="CDOT - Department of Transportation"].mean())}
print("share closed within ~1 minute by channel (all types):",{k:round(v,1) for k,v in out["share_subminute"].items()},"| sign-repair types:",{k:round(v,1) for k,v in out["share_subminute_sign"].items()},flush=True)
def run(tag,s,within=True):
    r=reg(s,"lhrs",X1,FE0,"ca"); rec={"pooled":pooled_summary(r)}
    if within:
        r3=reg(s,"lhrs",X3,FE0+["tract"],"ca"); t=pd.read_csv("../paper1_replication/work/tract.csv",dtype={"GEOID":str}); t=t[t.analytic]; mu,sd=t.pct_black.mean(),t.pct_black.std()
        rec["within"]={"n":int(r3.n),"alder":[float(r3.b["alder"]),r3.se("alder"),r3.p("alder")],"alder_B":[float(r3.b["alder_B"]),r3.se("alder_B"),r3.p("alder_B")],"gap0":r3.lin({"alder":1,"alder_B":(0-mu)/sd}),"gap100":r3.lin({"alder":1,"alder_B":(100-mu)/sd})}
    out[tag]=rec; savej("S14_artifacts",out)
    w=rec.get("within"); p=rec["pooled"]
    print(f"{tag:46s} n={p['n']:>9,} gradients phone {p['phone'][0]:.3f} alder {p['alder'][0]:.3f} diff {p['diff'][0]:.3f} ({p['diff'][1]:.3f})"+(f" | within-tract gap {w['alder'][0]:.3f} ({w['alder'][1]:.3f}); 0% {w['gap0'][0]:.3f}, 100% {w['gap100'][0]:.3f} ({w['gap100'][1]:.3f})" if w else ""),f"[{time.time()-t0:.0f}s]",flush=True)
run("all departments, excluding sign-repair types",d[~ty.isin(SIGN)])
run("all departments, excluding sub-minute closures",d[~sub])
run("all departments, excluding both",d[~ty.isin(SIGN)&~sub])
cd=d[d.dept=="CDOT - Department of Transportation"]; tc=cd.type.astype(str)
run("Transportation, excluding sign-repair types",cd[~tc.isin(SIGN)])
run("Transportation, excluding both",cd[~tc.isin(SIGN)&~(cd.lhrs<0.0166)])
