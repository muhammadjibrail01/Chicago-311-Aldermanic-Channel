# Transportation checks (S13): median completion hours by channel for selected types; Transportation within-tract gap without the pothole types
import pandas as pd, numpy as np
from p2lib import *
d=load("2019-11-01",extra=("dept",)); d["dept"]=d.dept.astype(str); d["hours"]=np.expm1(d.lhrs); out={}
types=["Pothole in Street Complaint","Alley Pothole Complaint","Street Light Out Complaint","Traffic Signal Out Complaint","Sign Repair Request - All Other Signs","Graffiti Removal Request","Rodent Baiting/Rat Complaint","Garbage Cart Maintenance","Fly Dumping Complaint"]
sel=d[d.type.astype(str).isin(types)]; t=sel.groupby([sel.type.astype(str),"chan"]).hours.median().unstack(); t["n_phone"]=sel[sel.chan=="phone"].groupby(sel.type.astype(str)).size(); t["n_type"]=d.groupby(d.type.astype(str)).size().reindex(t.index)
cd=d[d.dept=="CDOT - Department of Transportation"]; shares=(cd.groupby(cd.type.astype(str)).size()/len(cd)*100).sort_values(ascending=False).head(4)
out["median_hours"]=t.round(1).fillna(0).to_dict(orient="index"); out["cdot_share_of_sample"]=float(len(cd)/len(d)*100); out["cdot_top_types"]=shares.round(1).to_dict(); out["ss_share_of_sample"]=float((d.dept=="Streets and Sanitation").mean()*100)
m=cd[~cd.type.astype(str).isin(["Pothole in Street Complaint","Alley Pothole Complaint"])]; r=reg(m,"lhrs",X3,FE0+["tract"],"ca")
out["cdot_excl_potholes"]={"n":int(r.n),"gap":[float(r.b["alder"]),r.se("alder"),r.p("alder")]}; savej("S13_cdot_check",out); print(out["median_hours"]["Pothole in Street Complaint"],out["cdot_excl_potholes"])
