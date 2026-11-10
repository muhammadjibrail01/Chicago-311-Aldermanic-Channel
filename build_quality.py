# Quality outcomes per the main paper's definitions (Section 4.2 and Appendix B.3), validated against its Table 5 means.
import pandas as pd, numpy as np
raw=pd.read_parquet("work/core_raw.parquet",columns=["SR_NUMBER","SR_TYPE","STREET_ADDRESS","CREATED_DATE","CLOSED_DATE","STATUS"])
core=pd.read_parquet("work/core_request_file.parquet",columns=["sr","chan","speed_s","nd"])
assert (raw.SR_NUMBER.values==core.sr.values).all()
res=(core.chan!="city").values; nd=core.nd.values; sp=core.speed_s.values
t0=pd.Timestamp("2019-01-01"); cs=((raw.CREATED_DATE-t0).dt.total_seconds()).values; ce=((raw.CLOSED_DATE-t0).dt.total_seconds()).values
addr=raw.STREET_ADDRESS.astype(str).str.upper().str.strip()
gid=pd.Series(list(zip(raw.SR_TYPE.astype(str).values,addr.values))).where(res).map(lambda x: x).factorize(use_na_sentinel=True)[0] if False else None
addr=addr.where(raw.STREET_ADDRESS.notna(),"<<MISSING>>")
key=(raw.SR_TYPE.astype(str)+"|"+addr)
codes,uni=pd.factorize(key); codes=codes.astype(np.int64)
gcount_all=np.bincount(codes); thr=np.quantile(gcount_all,0.9995); ph=gcount_all>thr       # placeholder groups: defined over all core requests, as the main paper's counts imply
print("placeholder groups:",int(ph.sum()),"| requests in them:",int(gcount_all[ph].sum()),"(main paper: 1,267 groups, 112,674 requests)")
gid=np.where(res,codes,-1)
BIG=np.int64(10**10)
import sys
UNI=sys.argv[1] if len(sys.argv)>1 else 'res'; VARIANTS=False
ok=(res&nd if UNI=='nd' else res)&(gid>=0); skeys=np.sort(gid[ok]*BIG+cs[ok].astype(np.int64))
def rereport(days,cut_inclusive):
    focal=res&nd&sp&~np.isnan(ce)&(gid>=0)
    focal&=~np.isin(gid,np.where(ph)[0])
    end=(pd.Timestamp("2024-12-31")-t0).total_seconds()
    lim=end-days*86400
    focal&=(ce<=lim) if cut_inclusive else (ce<lim)
    q=gid[focal]*BIG+ce[focal].astype(np.int64); i=np.searchsorted(skeys,q,side="right"); i2=np.minimum(i,len(skeys)-1)
    cand=skeys[i2]; same=(i<len(skeys))&(cand//BIG==gid[focal]); delta=cand-gid[focal]*BIG-ce[focal].astype(np.int64)
    if days==30 and VARIANTS:
        for nm,cond in (('<=30d',delta<=30*86400),('<30d',delta<30*86400),('whole days <=30 (floor)',delta//86400<=30),('whole days <30',delta//86400<30),('<=31d',delta<=31*86400)):
            print(f'   variant {nm:26s}: mean {100*np.mean(same&cond):.3f}%',flush=True)
    out=np.full(len(raw),np.nan); out[np.where(focal)[0]]=(same&(delta<=days*86400)).astype(float); return out
r30=rereport(30,True); r90=rereport(90,True)
print(f"re-report 30 d: N={int(np.sum(~np.isnan(r30))):,} mean={100*np.nanmean(r30):.2f}% (paper 3,377,469; 9.55%) | 90 d: N={int(np.sum(~np.isnan(r90))):,} mean={100*np.nanmean(r90):.2f}% (paper 3,279,497; 15.14%)")
st=pd.read_parquet("work/core_request_file.parquet",columns=["status"]).status.values
q=res&nd; print(f"quality sample N={int(q.sum()):,} (paper 3,677,012) | canceled {100*np.mean(st[q]=='Canceled'):.2f}% (paper 2.95) | unresolved {100*np.mean(st[q]=='Open'):.2f}% (paper 0.76)")
pd.DataFrame({"sr":core.sr.values,"rr30":r30,"rr90":r90}).to_parquet("work/quality_flags.parquet",index=False); print("saved quality_flags.parquet")
import json
json.dump({"placeholder_groups":int(ph.sum()),"placeholder_requests":int(gcount_all[ph].sum()),"rr30_n":int(np.sum(~np.isnan(r30))),"rr30_mean":float(100*np.nanmean(r30)),"rr90_n":int(np.sum(~np.isnan(r90))),"rr90_mean":float(100*np.nanmean(r90)),
  "quality_n":int(q.sum()),"canceled_pct":float(100*np.mean(st[q]=="Canceled")),"unresolved_pct":float(100*np.mean(st[q]=="Open")),
  "main_paper":{"placeholder_groups":1267,"placeholder_requests":112674,"rr30_n":3377469,"rr30_mean":9.55,"rr90_n":3279497,"rr90_mean":15.14,"quality_n":3677012,"canceled_pct":2.95,"unresolved_pct":0.76}},open("results/S18_quality_validation.json","w"),indent=1)
