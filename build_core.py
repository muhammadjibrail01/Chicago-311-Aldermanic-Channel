import pandas as pd, numpy as np
r=pd.read_parquet("work/core_raw.parquet")
o=r.ORIGIN.astype(str)
city={"Mass Entry","Generated In House","DWM","City Department","WOFromTerraGo","Salesforce Mobile App","SPOTCSR","CSCC","XTERFACE","Chicago Police Department","Chicago Fire Department","IMMTOWQA","RMS","CreateWorkOrder","Radio","HealthProfessionals"}
phone={"Phone Call","Phone","Walk-in","Mail","Fax"}; ald={"Alderman's Office","ALDERMAN","Budget Town Hall Meeting","FY25 Budget Engagement","Mayor's Office"}
r["chan"]=np.select([o.isin(city),o.isin(phone),o.isin(ald)],["city","phone","alderman"],default="digital")
c=r.CREATED_DATE; r["year"]=c.dt.year.astype("int16"); r["ym"]=((c.dt.year-2019)*12+c.dt.month-1).astype("int16")
r["dow"]=c.dt.dayofweek.astype("int8"); r["hod"]=c.dt.hour.astype("int8"); r["week"]=((c-pd.Timestamp("2019-01-01")).dt.days//7).astype("int16")
res=r.chan!="city"; nd=res&(r.DUPLICATE.astype(str)=="false")
ok=r.CLOSED_DATE.notna()&(r.CLOSED_DATE>=r.CREATED_DATE)&c.notna()
r["speed_s"]=nd&(r.STATUS=="Completed")&ok
hrs=(r.CLOSED_DATE-r.CREATED_DATE).dt.total_seconds()/3600
r["hours"]=hrs.where(r.speed_s)
cap=r[r.speed_s].groupby("SR_TYPE",observed=True).hours.quantile(0.99)
r["hours_w"]=np.minimum(r.hours,r.SR_TYPE.map(cap).astype(float))
r["lhrs"]=np.log1p(r.hours_w).astype("float32")
# workload: resident non-duplicate requests of same type, community area, week (incl. itself)
key=r.loc[nd,["SR_TYPE","COMMUNITY_AREA","week"]]
cnt=key.groupby(["SR_TYPE","COMMUNITY_AREA","week"],observed=True).size().rename("wl")
r=r.join(cnt,on=["SR_TYPE","COMMUNITY_AREA","week"])
r["lwl"]=np.log(r.wl.where(nd)).astype("float32")
out=pd.DataFrame({"sr":r.SR_NUMBER.values,"type":r.SR_TYPE.astype(str).values,"chan":r.chan.values,"year":r.year.values,"ym":r.ym.values,"dow":r.dow.values,"hod":r.hod.values,
  "ca":r.COMMUNITY_AREA.values,"ward":r.WARD.values,"lwl":r.lwl.values,"dept":r.OWNER_DEPARTMENT.astype(str).values,"speed_s":r.speed_s.values,"lhrs":r.lhrs.values,
  "lat":r.LATITUDE.values,"lon":r.LONGITUDE.values,"created":r.CREATED_DATE.values,"nd":nd.values,"status":r.STATUS.astype(str).values,"origin":o.values,"hours":r.hours.values})
out.to_parquet("work/core_request_file.parquet",index=False)
s=out[out.speed_s]
print("speed sample:",f"{len(s):,}","(paper 3,540,652) | mean lhrs: %.3f (paper 4.708)"%s.lhrs.mean())
print("channels in speed sample:",s.chan.value_counts().to_dict(),"(paper 1,871,774 / 1,367,395 / 301,483)")
print("median hours: %.1f (paper 117.4)"%s.hours.median())
