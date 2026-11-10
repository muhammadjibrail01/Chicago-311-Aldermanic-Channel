import numpy as np, pandas as pd
from scipy import stats
from fe import demean, _codes
class Res:
    def __init__(s,b,V,names,n,G): s.b=pd.Series(b,index=names); s.V=pd.DataFrame(V,index=names,columns=names); s.n=n; s.G=G
    def se(s,k): return float(np.sqrt(s.V.loc[k,k]))
    def p(s,k): return float(2*stats.t.sf(abs(s.b[k]/s.se(k)),s.G-1))
    def lin(s,w):                       # linear combination {name: weight}
        v=pd.Series(w); est=float((s.b[v.index]*v).sum()); se=float(np.sqrt(v.values@s.V.loc[v.index,v.index].values@v.values))
        return est,se,float(2*stats.t.sf(abs(est/se),s.G-1))
    def wald(s,names):                  # joint test all = 0
        b=s.b[names].values; Vi=np.linalg.inv(s.V.loc[names,names].values); W=float(b@Vi@b); k=len(names)
        F=W/k; return F,float(stats.f.sf(F,k,s.G-1))
def reg(df,y,X,fes,cluster):
    d=df[list(dict.fromkeys([y]+X+fes+[cluster]))].dropna()
    M=demean(d[[y]+X].to_numpy(np.float64),[d[f].to_numpy() for f in fes],tol=1e-7,maxit=120); yt,Xt=M[:,0],M[:,1:]
    A=Xt.T@Xt; A_inv=np.linalg.inv(A); b=A_inv@(Xt.T@yt); e=yt-Xt@b
    g=_codes(d[cluster].to_numpy()); G=g.max()+1; n,k=Xt.shape
    S=np.column_stack([np.bincount(g,weights=Xt[:,j]*e,minlength=G) for j in range(k)])
    V=A_inv@(S.T@S)@A_inv*(G/(G-1))*((n-1)/(n-k)); return Res(b,V,X,n,G)
def load(start="2019-11-01",extra=()):
    cols=["sr","type","chan","year","ym","dow","hod","ca","lwl","lhrs","speed_s","created","tract","z_hardship","z_pct_black","z_pct_hisp","alder","digital","period","aw"]+list(extra)
    d=pd.read_parquet("work/p2_data.parquet",columns=list(dict.fromkeys(cols)))
    d=d[d.speed_s&(d.created>=pd.Timestamp(start))].copy()
    d["ty"]=(d.type.astype("category").cat.codes.astype(np.int32)*10+(d.year-2019)).astype(np.int32)
    for c in ("z_hardship","z_pct_black","z_pct_hisp"): d[c]=d[c].astype("float32")
    for ch in ("alder","digital"):
        for z,nm in (("z_pct_black","B"),("z_hardship","H"),("z_pct_hisp","L")): d[f"{ch}_{nm}"]=(d[ch]*d[z]).astype("float32")
    d["wp"]=(d.period.astype(int)*100+d.aw.fillna(0).astype(int)).astype(np.int32)
    return d

import json, os
def pack(r,keys=None):
    keys=keys or list(r.b.index)
    return {"n":int(r.n),"G":int(r.G),"coef":{k:[float(r.b[k]),r.se(k),r.p(k)] for k in keys}}
def savej(name,obj):
    json.dump(obj,open(f"results/{name}.json","w"),indent=1,default=float)

def add_inter(d):
    for ch in ("alder","digital"):
        for z,nm in (("z_pct_black","B"),("z_hardship","H"),("z_pct_hisp","L")):
            d[f"{ch}_{nm}"]=(d[ch]*d[z]).astype("float32")
    d["ty"]=(d.type.astype("category").cat.codes.astype(np.int32)*10+(d.year-2019)).astype(np.int32)
    for c in ("z_hardship","z_pct_black","z_pct_hisp"): d[c]=d[c].astype("float32")
    return d
X1=["z_pct_black","z_hardship","z_pct_hisp","alder","digital","alder_B","digital_B","alder_H","digital_H","alder_L","digital_L","lwl"]
X3=["alder","digital","alder_B","digital_B","alder_H","digital_H","alder_L","digital_L","lwl"]
FE0=["ty","ym","dow","hod"]
def pooled_summary(r):
    pg=r.lin({"z_pct_black":1}); ag=r.lin({"z_pct_black":1,"alder_B":1}); dg=r.lin({"z_pct_black":1,"digital_B":1})
    return {"phone":[pg[0],pg[1]],"digital":[dg[0],dg[1]],"alder":[ag[0],ag[1]],"diff":[float(r.b["alder_B"]),r.se("alder_B"),r.p("alder_B")],"n":int(r.n)}
