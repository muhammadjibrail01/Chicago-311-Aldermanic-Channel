import time; from p2lib import *
t0=time.time()
u=pd.read_parquet("work/p2_data.parquet",columns=["created","period","aw","alder"]); u=u[(u.created>=pd.Timestamp("2019-11-01"))&(u.period>0)]
u["wp"]=(u.period.astype(int)*100+u.aw.fillna(0).astype(int)).astype(np.int32); sh=u.groupby("wp").alder.mean().sort_index(); del u
sh=sh[sh.index%100>0]; terc=pd.qcut(sh.rank(method="first"),3,labels=[1,2,3]).astype(int); order=sh.sort_values(ascending=False)
print("highest-use ward-periods:",[(int(i//100),int(i%100),round(100*v,1)) for i,v in order.head(10).items()],flush=True)
d=load("2019-11-01"); d=d[d.period>0].copy(); d["terc"]=d.wp.map(terc)
out={"top_wardperiods":[[int(i//100),int(i%100),float(100*v)] for i,v in order.head(10).items()]}
def run(tag,s):
    r=reg(s,"lhrs",X1,FE0,"ca"); out[tag]=pooled_summary(r); o=out[tag]
    print(f"{tag:34s} n={o['n']:>9,} phone {o['phone'][0]:.3f} alder {o['alder'][0]:.3f} diff {o['diff'][0]:.3f} ({o['diff'][1]:.3f})  [{time.time()-t0:.0f}s]",flush=True); savej("S12_concentration",out)
for k,lab in ((1,"Lowest-use third of ward-periods"),(2,"Middle third of ward-periods"),(3,"Highest-use third of ward-periods")): run(lab,d[d.terc==k])
for k in (3,5,10): run(f"Excluding the {k} highest-use ward-periods",d[~d.wp.isin(order.head(k).index)])
