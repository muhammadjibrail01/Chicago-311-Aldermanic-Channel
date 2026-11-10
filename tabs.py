import json, numpy as np
R="results/"
L=lambda n: json.load(open(R+n+".json"))
def st(p): return "***" if p<.01 else "**" if p<.05 else "*" if p<.1 else ""
def cs(v,d=3): return f"{v[0]:.{d}f}{st(v[2])}"        # coef with stars, v=[b,se,p]
def se(v,d=3): return f"({v[1]:.{d}f})"
def n_(x): return f"{int(round(x)):,}"
def coefrows(label,vals,d=3):                            # two rows: coef and se
    return [[label]+[cs(v,d) if v else "" for v in vals],[""]+[se(v,d) if v else "" for v in vals]]
S0=L("S0_descriptives"); S4=L("S4_usage"); S5=L("S5_robust"); S6=L("S6_main")

def table1():
    t=S0["table1"]; ch=["phone","digital","alderman","all"]
    rows=[["Resident requests (n)"]+[n_(t[c]["n_resident"]) for c in ch],
          ["Share of resident requests (%)"]+[f"{t[c]['share_resident']:.1f}" for c in ch],
          ["Speed sample (n)"]+[n_(t[c]["n_speed"]) for c in ch],
          ["Median completion time (hours)"]+[f"{t[c]['median_hours']:.0f}" for c in ch],
          ["Mean log(1 + hours)"]+[f"{t[c]['mean_lhrs']:.2f}" for c in ch],
          ["Mean tract Black share (%)"]+[f"{t[c]['mean_pct_black']:.1f}" for c in ch],
          ["Mean tract hardship index"]+[f"{t[c]['mean_hardship']:.1f}" for c in ch],
          ["Requests in majority-Black tracts (%)"]+[f"{t[c]['pct_in_majBlack_tracts']:.1f}" for c in ch]]
    return dict(t="table",title="Table 1. Resident requests by reporting channel, November 2019 – December 2024",cols=[3400,1490,1490,1490,1490],header=["","Phone","Web / app","Aldermanic office","All"],rows=rows,align=["l","c","c","c","c"],
        note="Resident-initiated requests in the 789 analytic census tracts, created on or after 1 November 2019 (after the recording break discussed in Section 3.2). The speed sample contains completed, non-duplicate requests. Tract measures are ACS 2019–2023 estimates; the hardship index is the tract index described in the companion paper on race and class. Source: City of Chicago Data Portal; author's calculations.")
def table2():
    bq=S0["share_by_blackq"]; hq=S0["share_by_hardq"]; u1=S4["U1"]["coef"]; u2=S4["U2"]["coef"]
    rows=[["Panel A. Aldermanic share of resident requests (%), by tract quintile"],
          ["Black share of tract"]+[f"{x:.1f}" for x in bq],["Hardship index of tract"]+[f"{x:.1f}" for x in hq],
          ["Panel B. Linear probability model: aldermanic channel (percentage points per +1 SD of tract measure)"],
          ["","(1) Baseline","(2) Ward-period FE","","",""]]
    for k,lab in (("z_pct_black","Black share"),("z_hardship","Hardship index"),("z_pct_hisp","Hispanic share")):
        rows+=coefrows(lab,[u1[k],u2[k],None,None,None],2)
    rows+=[["Request type × year and month fixed effects","Yes","Yes","","",""],["Ward-period fixed effects","No","Yes","","",""],["Observations",n_(S4["U1"]["n"]),n_(S4["U2"]["n"]),"","",""]]
    return dict(t="table",title="Table 2. Who uses the aldermanic channel",cols=[3300,1212,1212,1212,1212,1212],header=["","Q1 (lowest)","Q2","Q3","Q4","Q5 (highest)"],rows=rows,align=["l","c","c","c","c","c"],
        note="Resident requests in the 789 analytic tracts created on or after 1 November 2019. Panel B: dependent variable is 100 × an indicator for the aldermanic channel (sample mean %.1f); column (2) compares tracts within the same alderman's ward and term, with wards assigned from request coordinates (2015 map before 15 May 2023, 2023 map afterward). Standard errors clustered by community area (77) in parentheses. *** p<0.01, ** p<0.05, * p<0.1."%S4["usage_mean"])
def table3():
    ph,dg,al=[S6[f"chan_{c}"] for c in ("phone","digital","alderman")]; M=S6["M1"]["coef"]
    rows=[["Panel A. Channel-specific models (log points of completion time per +1 SD)"]]
    for k,lab in (("z_pct_black","Black share"),("z_hardship","Hardship index"),("z_pct_hisp","Hispanic share")):
        rows+=coefrows(lab,[ph["coef"][k],dg["coef"][k],al["coef"][k]])
    rows+=[["Observations",n_(ph["n"]),n_(dg["n"]),n_(al["n"])],
           ["Panel B. Pooled model: difference from phone gradient"],["","","Web / app − phone","Aldermanic − phone"]]
    for k,lab in (("B","Black share"),("H","Hardship index"),("L","Hispanic share")):
        rows+=coefrows(lab,[None,M[f"digital_{k}"],M[f"alder_{k}"]])
    F,p=S6["M1_wald"]; rows+=[["Joint test, aldermanic × (Black, hardship, Hispanic) = 0","","",f"F = {F:.1f}, p < 0.001" if p<0.001 else f"F = {F:.1f}, p = {p:.3f}"],["Observations","",n_(S6["M1"]["n"]),n_(S6["M1"]["n"])]]
    return dict(t="table",title="Table 3. Race, class and the speed of service, by reporting channel",cols=[3600,1920,1920,1920],header=["","Phone","Web / app","Aldermanic office"],rows=rows,align=["l","c","c","c"],
        note="Speed sample, created on or after 1 November 2019. Dependent variable: log(1 + hours to completion), winsorized at the type-specific 99th percentile. Tract measures are standardized across the 789 analytic tracts. Panel A estimates each channel separately with request type × year, month-of-sample, weekday and hour fixed effects and log workload. Panel B pools the three channels, interacts each tract measure with channel indicators, and imposes common fixed effects and workload slopes, so its phone gradient (%.3f for Black share) differs slightly from Panel A. Standard errors clustered by community area (77) in parentheses. *** p<0.01, ** p<0.05, * p<0.1."%M["z_pct_black"][0])
def table4():
    M=S6["M3"]["coef"]; W=S6["M3_wardcl"]["coef"]; G=L("S7_gap_pcts")
    rows=[["Panel A. Within-tract model (tract fixed effects)"]]
    for k,lab in (("alder","Aldermanic office − phone (at mean tract)"),("digital","Web / app − phone (at mean tract)"),("alder_B","  × Black share (+1 SD)"),("digital_B","  × Black share (+1 SD)"),("alder_H","  × Hardship (+1 SD)"),("digital_H","  × Hardship (+1 SD)")):
        pass
    rows+=coefrows("Aldermanic − phone gap (mean tract)",[M["alder"],W["alder"]])
    rows+=coefrows("   × Black share (+1 SD)",[M["alder_B"],W["alder_B"]])
    rows+=coefrows("   × Hardship (+1 SD)",[M["alder_H"],W["alder_H"]])
    rows+=coefrows("   × Hispanic share (+1 SD)",[M["alder_L"],W["alder_L"]])
    rows+=coefrows("Web / app − phone gap (mean tract)",[M["digital"],W["digital"]])
    rows+=coefrows("   × Black share (+1 SD)",[M["digital_B"],W["digital_B"]])
    rows+=[["Observations",n_(S6["M3"]["n"]),n_(S6["M3_wardcl"]["n"])],["Clusters",str(S6["M3"]["G"]),str(S6["M3_wardcl"]["G"])],
           ["Panel B. Implied completion-time gap vs. phone (log points) at selected tract Black shares"],["Tract Black share","Aldermanic office","Web / app"]]
    for p in G["pts"]:
        a=G["alder"][str(p)]; d=G["digital"][str(p)]
        rows.append([f"{p:.0f}%",f"{a[0]:.3f} ({a[1]:.3f})",f"{d[0]:.3f} ({d[1]:.3f})"])
    return dict(t="table",title="Table 4. Channel gaps within the same tract",cols=[4300,2530,2530],header=["","(1) Cluster: community area","(2) Cluster: ward"],rows=rows,align=["l","c","c"],
        note="Speed sample, created on or after 1 November 2019. Dependent variable: log(1 + hours). All models include request type × year, month-of-sample, weekday, hour and tract fixed effects, log workload, and the aldermanic and web/app interactions with Black share, hardship and Hispanic share (only some are shown); the channel gaps are therefore identified by comparing requests of the same type, in the same tract, at similar times. Column (2) clusters by 2023-map ward and drops the 431 requests that lack one. Panel B evaluates the interaction model at tract Black shares of 0, 33, 67 and 100 percent (standard errors in parentheses). *** p<0.01, ** p<0.05, * p<0.1.")
def table7():
    keys=[("baseline (post-break)","Baseline (Nov 2019 onward)"),("cluster by ward-period","Clustered by ward-period"),("+ ward-period FE","With ward-period fixed effects"),("excl. mid-term-change wards","Excluding wards 11, 12, 24, 43 (mid-term changes)"),("full window (from Jan 2019)","Full window (January 2019 onward)"),("fixed-scope services","Fixed-scope services only"),("variable-scope services","Variable-scope services only"),("other services","Other services only")]
    rows=[]
    for k,lab in keys:
        r=S5[k]; rows.append([lab,n_(r["n"]),f"{r['phone'][0]:.3f}",f"{r['alder'][0]:.3f}",f"{r['diff'][0]:.3f}{st(r['diff'][2])} ({r['diff'][1]:.3f})"])
    return dict(t="table",title="Table 7. Robustness of the weaker racial gradient in aldermanic requests",cols=[3900,1260,1000,1200,2000],header=["Specification","Observations","Phone gradient","Aldermanic gradient","Difference (se)"],rows=rows,align=["l","c","c","c","c"],
        note="Each row re-estimates the pooled model of Table 3, Panel B, on the stated sample or with the stated change. Gradients are log points of completion time per +1 SD of tract Black share; the difference is the aldermanic minus phone gradient. Fixed-scope, variable-scope and other services follow the classification in the companion paper on race and class. Standard errors clustered by community area unless noted. *** p<0.01, ** p<0.05, * p<0.1.")
