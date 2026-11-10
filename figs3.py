import json, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams.update({"font.family":"serif","font.size":9,"axes.spines.top":False,"axes.spines.right":False,"axes.titlesize":9.5,"axes.labelsize":9})
RC="#c0392b"; BL="#1f77b4"; GR="#444444"
G=json.load(open("results/S15_dept_comparable.json")); pts=G["pts"]
col={"Streets and Sanitation":"#c0392b","CDOT - Department of Transportation":"#7f3fbf","DWM - Department of Water Management":"#1f77b4","DOB - Buildings":"#2e8b57"}
fig,axs=plt.subplots(1,2,figsize=(6.5,3.0),gridspec_kw={"width_ratios":[1,1.15]})
for k,ax in (("CDOT - Department of Transportation",axs[0]),):
    o=G[k]; e=np.array([o["alder"][str(p)][0] for p in pts]); s=np.array([o["alder"][str(p)][1] for p in pts]); ax.plot(pts,e,color=col[k],marker="o",ms=4); ax.fill_between(pts,e-1.96*s,e+1.96*s,color=col[k],alpha=.15); ax.set_title("Transportation (CDOT)")
ax=axs[1]
for k in ("Streets and Sanitation","DWM - Department of Water Management","DOB - Buildings"):
    o=G[k]; e=np.array([o["alder"][str(p)][0] for p in pts]); s=np.array([o["alder"][str(p)][1] for p in pts]); ax.plot(pts,e,color=col[k],marker="o",ms=4,label=o["label"]); ax.fill_between(pts,e-1.96*s,e+1.96*s,color=col[k],alpha=.13)
ax.axhline(0,color="#999999",lw=.8); ax.set_title("Other departments"); ax.legend(frameon=False,fontsize=7.5,loc="lower left")
for a in axs: a.set_xlabel("Tract Black share (%)"); a.set_xticks(pts); a.set_xticklabels(["0","33","67","100"])
axs[0].set_ylabel("Aldermanic − phone completion-time gap\n(log points, same tract)")
fig.tight_layout(); fig.savefig("figs/fig4_gap.png",dpi=220); plt.close()
S=json.load(open("results/S11_departments.json")); keys=["Streets and Sanitation","CDOT - Department of Transportation","DWM - Department of Water Management","DOB - Buildings","Animal Care and Control"]
fig,ax=plt.subplots(figsize=(6.2,3.2)); off={"phone":-0.22,"digital":0,"alder":0.22}; cc={"phone":GR,"digital":BL,"alder":RC}; lab={"phone":"Phone","digital":"Web / app","alder":"Aldermanic office"}
for i,k in enumerate(keys):
    p=S[k]["pooled"]
    for ch in ("phone","digital","alder"):
        ax.errorbar(p[ch][0],i+off[ch],xerr=1.96*p[ch][1],fmt="o",color=cc[ch],capsize=2.5,ms=4,label=lab[ch] if i==0 else None)
ax.axvline(0,color="#999999",lw=.8); ax.set_yticks(range(len(keys))); ax.set_yticklabels([S[k]["label"] for k in keys]); ax.invert_yaxis(); ax.set_xlabel("Black-share gradient in completion time (log points per +1 SD)"); ax.legend(frameon=False,fontsize=8,loc="lower right")
fig.tight_layout(); fig.savefig("figs/fig5_depts.png",dpi=220); plt.close(); print("fig4, fig5 written")
