import pandas as pd, numpy as np
c=pd.read_parquet("work/core_request_file.parquet",columns=["sr","type","chan","year","ym","dow","hod","ca","ward","lwl","dept","speed_s","lhrs","created","nd"])
for k in ("type","chan","dept"): c[k]=c[k].astype("category")
loc=pd.read_parquet("../paper1_replication/work/core_locations.parquet",columns=["GEOID"])
wa=pd.read_parquet("work/ward_assign.parquet")
assert (c.sr.values==wa.SR_NUMBER.values).all() and len(c)==len(loc)
c["GEOID"]=pd.Categorical(loc.GEOID.values); del loc; c["ward_old"]=wa.ward_old.values; c["ward_new"]=wa.ward_new.values; del wa
t=pd.read_csv("../paper1_replication/work/tract.csv",dtype={"GEOID":str}).set_index("GEOID"); t=t[t.analytic]
ix=pd.Index(t.index); pos=ix.get_indexer(c.GEOID.astype(object).values)    # -1 if not an analytic tract
c["tract"]=pos.astype("int32"); del c["GEOID"]
for v in ["hardship","pct_black","pct_hisp","poverty","pct_white"]:
    z=((t[v]-t[v].mean())/t[v].std()).values.astype("float32"); c["z_"+v]=np.where(pos>=0,z[np.maximum(pos,0)],np.nan).astype("float32")
c=c[(c.chan!="city")&(c.tract>=0)].copy()                       # resident requests in the 789 analytic tracts
t1=pd.Timestamp("2019-05-20"); t2=pd.Timestamp("2023-05-15")
c["period"]=np.select([c.created<t1,c.created<t2],[0,1],default=2).astype("int8")
c["aw"]=np.where(c.period==1,c.ward_old,np.where(c.period==2,c.ward_new,np.nan))    # ward whose alderman held this location on the request date
c["alder"]=(c.chan=="alderman").astype("int8"); c["digital"]=(c.chan=="digital").astype("int8")
c.to_parquet("work/p2_data.parquet",index=False)
s=c[c.speed_s]
print(f"resident requests in analytic tracts: {len(c):,} | speed sample: {len(s):,}")
print("period counts (all resident):",c.period.value_counts().sort_index().to_dict())
print("aldermanic share of resident requests by period:",(c.groupby('period').alder.mean()*100).round(2).to_dict())
