import pandas as pd, numpy as np
raw=pd.read_parquet("work/core_raw.parquet",columns=["SR_NUMBER","SR_TYPE","STREET_ADDRESS","CREATED_DATE"])
p=pd.read_parquet("work/p2_data.parquet",columns=["sr","chan","speed_s","created","tract","z_pct_black","alder"])
raw=raw.merge(p[["sr"]].assign(res=True),left_on="SR_NUMBER",right_on="sr",how="inner")   # resident requests in analytic tracts
raw["addr"]=raw.STREET_ADDRESS.astype(str).str.upper().str.strip()
k=raw.groupby(["SR_TYPE","addr"],observed=True).ngroup()
cnt=k.map(k.value_counts()); thr=cnt.quantile(0.9995); raw=raw[cnt<=thr].copy(); raw["k"]=k[raw.index]   # drop placeholder-address groups
raw=raw.sort_values(["k","CREATED_DATE"]); prev=raw.groupby("k").CREATED_DATE.shift(1)
gap=(raw.CREATED_DATE-prev).dt.total_seconds()/86400
raw["rep30"]=gap.le(30); raw["rep90"]=gap.le(90)
m=raw[["sr","rep30","rep90"]].merge(p[["sr","chan","speed_s","created","z_pct_black"]],on="sr")
m=m[m.speed_s&(m.created>="2019-11-01")]
print("Share of speed-sample requests that repeat an earlier same-type, same-address request within 30 / 90 days (%):")
print((m.groupby("chan")[["rep30","rep90"]].mean()*100).round(1).to_string())
m["bq"]=pd.qcut(m.z_pct_black,3,labels=["low Black","mid","high Black"])
print("\nBy tract Black-share tercile (rep90 %):"); print((m.groupby(["bq","chan"],observed=True).rep90.mean().unstack()*100).round(1).to_string())
m[["sr","rep30","rep90"]].to_parquet("work/repeat_flags.parquet",index=False)
