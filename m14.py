# November 2019 break diagnostics (S17)
import pandas as pd, json
r=pd.read_parquet("work/core_request_file.parquet",columns=["created","chan","origin","ward"]); r=r[r.chan!="city"].copy(); r["ym"]=r.created.dt.to_period("M")
a=r[r.origin=="Alderman's Office"]; pre=a[(a.ym>="2019-09")&(a.ym<="2019-10")].groupby("ward").size(); post=a[(a.ym>="2019-11")&(a.ym<="2019-12")].groupby("ward").size()
d=pd.DataFrame({"pre":pre,"post":post}).fillna(0); d["jump"]=d.post-d.pre; d=d[d.index>0]; w=r[r.ym=="2019-10"]; w2=r[r.ym=="2019-11"]
out={"wards_with_increase":int((d.jump>0).sum()),"wards":int(len(d)),"top_wards":[int(x) for x in d.jump.nlargest(5).index],"phone_share_oct":float(100*(w.origin=="Phone Call").mean()),"phone_share_nov":float(100*(w2.origin=="Phone Call").mean())}
json.dump(out,open("results/S17_break_check.json","w"),indent=1); print(out)
