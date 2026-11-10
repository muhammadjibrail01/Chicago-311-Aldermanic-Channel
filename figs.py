import json, numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"font.family":"serif","font.size":9,"axes.spines.top":False,"axes.spines.right":False,"axes.titlesize":10,"axes.labelsize":9})
C={"phone":"#444444","digital":"#1f77b4","alderman":"#c0392b"}
S0=json.load(open("results/S0_descriptives.json")); S6=json.load(open("results/S6_main.json")); S5=json.load(open("results/S5_robust.json"))
# Fig 1 monthly share
m=S0["monthly"]; x=np.array(m["ym"]); fig,ax=plt.subplots(figsize=(6.5,2.9))
ax.plot(x,m["share"],color=C["alderman"],lw=1.6)
mo=lambda y,mn: (y-2019)*12+mn-1+0.5
for pos,lab,dy in ((mo(2019,11),"Recording\nbreak, Nov 2019",5.0),(mo(2019,5),"Council\nsworn in",13.8),(mo(2023,5),"Council\nsworn in",13.8)):
    ax.axvline(pos,color="#777777",ls="--",lw=0.8); ax.text(pos+0.4,dy,lab,fontsize=7.5,va="top",color="#333333")
for pos in (mo(2019,2),mo(2023,2)): ax.axvline(pos,color="#bbbbbb",ls=":",lw=0.8)
ax.set_xlim(0,71); ax.set_ylim(0,14); ax.set_xticks([0,12,24,36,48,60]); ax.set_xticklabels(["Jan 2019","Jan 2020","Jan 2021","Jan 2022","Jan 2023","Jan 2024"]); ax.set_ylabel("Aldermanic share of\nresident requests (%)")
fig.tight_layout(); fig.savefig("figs/fig1_share.png",dpi=220); plt.close()
# Fig 2 ward-period scatter
w=pd.DataFrame(S0["wardperiod"]); fig,axs=plt.subplots(1,2,figsize=(6.5,3.1),sharey=True)
for ax,p,ttl in zip(axs,(1,2),("Nov 2019 – May 2023 (2015 wards)","May 2023 – Dec 2024 (2023 wards)")):
    x=w[w.period==p]; ax.scatter(x.pb,x.share,s=16,color=C["alderman"],alpha=.8,edgecolor="white",lw=.4)
    z=np.polyfit(x.pb,x.share,1); xs=np.linspace(0,100,50); ax.plot(xs,np.polyval(z,xs),color="#555555",lw=1)
    for _,r in x[x.aw.isin([13,15,19,6,27,20])].iterrows(): ax.annotate(int(r.aw),(r.pb,r.share),xytext=(3,3),textcoords="offset points",fontsize=7)
    ax.set_title(ttl,fontsize=8.5); ax.set_xlabel("Ward mean Black share of tract (%)")
axs[0].set_ylabel("Aldermanic share of resident requests (%)"); fig.tight_layout(); fig.savefig("figs/fig2_wards.png",dpi=220); plt.close()
# Fig 3 gradients by channel
fig,axs=plt.subplots(1,2,figsize=(6.5,2.7),sharey=True)
for ax,k,ttl in zip(axs,("z_pct_black","z_hardship"),("Black share (per +1 SD)","Hardship index (per +1 SD)")):
    for i,ch in enumerate(("phone","digital","alderman")):
        b,se,_=S6[f"chan_{ch}"]["coef"][k]; ax.errorbar(b,i,xerr=1.96*se,fmt="o",color=C[ch],capsize=3,ms=5)
    ax.axvline(0,color="#999999",lw=.8); ax.set_yticks([0,1,2]); ax.set_yticklabels(["Phone","Web / app","Aldermanic office"]); ax.set_xlabel("Log points of completion time"); ax.set_title(ttl)
ax.invert_yaxis(); fig.tight_layout(); fig.savefig("figs/fig3_gradients.png",dpi=220); plt.close()
# Fig 4 within-tract channel gap by Black share
fig,ax=plt.subplots(figsize=(4.8,3.0)); zs=[-1,0,1,2]; xs=[33.3+37.5*z for z in zs]
for key,lab,col in (("M3_gap_by_black","Aldermanic office vs. phone",C["alderman"]),("M3_dig_by_black","Web / app vs. phone",C["digital"])):
    e=np.array([S6[key][str(z)][0] for z in zs]); s=np.array([S6[key][str(z)][1] for z in zs]); xp=[max(0,min(100,v)) for v in xs]
    xp=np.array([0 if v<0 else v for v in xs]); ax.plot(xs,e,color=col,marker="o",ms=4,label=lab); ax.fill_between(xs,e-1.96*s,e+1.96*s,color=col,alpha=.15)
ax.axhline(0,color="#999999",lw=.8); ax.set_xlabel("Tract Black share, % (evaluated at −1, 0, +1, +2 SD)"); ax.set_ylabel("Completion-time gap vs. phone (log points)"); ax.legend(frameon=False,fontsize=8)
ax.set_xticks(xs); ax.set_xticklabels([f"{v:.0f}" if v>=0 else "<0" for v in xs]); fig.tight_layout(); fig.savefig("figs/fig4_gap.png",dpi=220); plt.close()
# Fig 6 robustness forest
order=[("baseline (post-break)","Baseline (Nov 2019 on)"),("cluster by ward-period","Cluster by ward-period"),("+ ward-period FE","+ ward-period fixed effects"),("excl. mid-term-change wards","Excl. wards 11, 12, 24, 43"),("full window (from Jan 2019)","Full window (from Jan 2019)"),("fixed-scope services","Fixed-scope services"),("variable-scope services","Variable-scope services"),("other services","Other services")]
order=[o for o in order if o[0] in S5]        # rows that are not in the stored robustness results are skipped
fig,ax=plt.subplots(figsize=(5.6,3.1))
for i,(k,lab) in enumerate(order):
    b,se,_=S5[k]["diff"]; ax.errorbar(b,i,xerr=1.96*se,fmt="o",color=C["alderman"],capsize=3,ms=4)
ax.axvline(0,color="#999999",lw=.8); ax.set_yticks(range(len(order))); ax.set_yticklabels([l for _,l in order],fontsize=8); ax.invert_yaxis(); ax.set_xlabel("Aldermanic minus phone difference in Black-share gradient (log points)")
fig.tight_layout(); fig.savefig("figs/fig6_robust.png",dpi=220); plt.close()
print("figures written")
