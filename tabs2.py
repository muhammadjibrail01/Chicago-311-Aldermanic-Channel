# Table builders for the election-free version of Paper 2 (Tables 1-3 reused from tabs.py)
import json
from tabs import table1, table2, table3, L, st, cs, se, n_, coefrows, S0, S5, S6
S10=L("S10_quality"); S11=L("S11_departments"); S11b=L("S11b_dept_gaps"); S12=L("S12_concentration"); S14=L("S14_artifacts"); S15=L("S15_dept_comparable"); S16=L("S16_comparable_pooled"); S7=L("S7_gap_pcts")
def cell(v,d=2): return f"{v[0]:.{d}f}{st(v[2])} ({v[1]:.{d}f})"
def gcell(v,d=3): return f"{v[0]:.{d}f}{st(v[2])} ({v[1]:.{d}f})"
def table4():
    M3=S6["M3"]["coef"]; MW=S6["M3_wardcl"]["coef"]; C=S16["pooled_within"]["coef"]
    rows=[["Panel A. Within-tract model (tract fixed effects)"]]
    rows+=coefrows("Aldermanic − phone gap (mean tract)",[M3["alder"],MW["alder"],C["alder"]])
    rows+=coefrows("   × Black share (+1 SD)",[M3["alder_B"],MW["alder_B"],C["alder_B"]])
    rows+=coefrows("Web / app − phone gap (mean tract)",[M3["digital"],MW["digital"],C["digital"]])
    rows+=coefrows("   × Black share (+1 SD)",[M3["digital_B"],MW["digital_B"],C["digital_B"]])
    rows+=[["Observations",n_(S6["M3"]["n"]),n_(S6["M3_wardcl"]["n"]),n_(S16["pooled_within"]["n"])],["Clusters",str(S6["M3"]["G"]),str(S6["M3_wardcl"]["G"]),str(S6["M3"]["G"])]]
    # pad Panel A rows to 5 columns
    rows=[r if len(r)==1 else r+[""] for r in rows]
    rows+=[["Panel B. Implied gap relative to phone (log points) at selected tract Black shares"],["Tract Black share","Aldermanic, all completed","Web / app, all completed","Aldermanic, comparable closures","Web / app, comparable closures"]]
    for p in S7["pts"]:
        a=S7["alder"][str(p)]; dd=S7["digital"][str(p)]; ca=S16["pooled_within"]["alder"][str(p)]; cd=S16["pooled_within"]["digital"][str(p)]
        rows.append([f"{p:.0f}%"]+[f"{v[0]:.3f} ({v[1]:.3f})" for v in (a,dd,ca,cd)])
    hdr=[i for i,r in enumerate(rows) if r and r[0]=='Tract Black share'][0]; kn=list(range(hdr,len(rows)-1))
    return dict(kn=kn,t="table",title="Table 4. Channel gaps within the same tract",cols=[2760,1650,1650,1650,1650],header=["","(1) Baseline, cluster: community area","(2) Baseline, cluster: ward","(3) Comparable closures, cluster: community area",""],rows=rows,align=["l","c","c","c","c"],
        note="Speed sample, created on or after 1 November 2019. Dependent variable: log(1 + hours). All models include request type × year, month-of-sample, weekday, hour and tract fixed effects, log workload, and the aldermanic and web/app interactions with Black share, hardship and Hispanic share (only some are shown), so the channel gaps compare requests of the same type, in the same tract, at similar times. Column (2) clusters by 2023-map ward and drops the 431 requests that lack one. Column (3) and the comparable-closure columns of Panel B drop requests completed within about one minute and the three sign-repair request types (Section 3.2). Panel B evaluates the interaction models at tract Black shares of 0, 33, 67 and 100 percent. Standard errors in parentheses. *** p<0.01, ** p<0.05, * p<0.1.")
def table5d():
    keys=["Streets and Sanitation","CDOT - Department of Transportation","DWM - Department of Water Management","DOB - Buildings","Animal Care and Control"]
    rows=[["Panel A. All completed requests"]]
    for k in keys:
        o=S11[k]; p=o["pooled"]; g=S11b.get(k,{}).get("alder"); 
        rows.append([o["label"],f"{o['share_alder']:.1f}",f"{p['phone'][0]:.3f}",f"{p['alder'][0]:.3f}",f"{p['diff'][0]:.3f}{st(p['diff'][2])} ({p['diff'][1]:.3f})",(gcell(g["0"]) if g else "—"),(gcell(g["100"]) if g else "—")])
    rows.append(["Panel B. Comparable-closure sample"])
    for k in keys:
        o=S15[k]; p=o["pooled"]; g=o.get("alder")
        rows.append([o["label"],f"{o['share_alder']:.1f}",f"{p['phone'][0]:.3f}",f"{p['alder'][0]:.3f}",f"{p['diff'][0]:.3f}{st(p['diff'][2])} ({p['diff'][1]:.3f})",(gcell(g["0"]) if g else "—"),(gcell(g["100"]) if g else "—")])
    return dict(t="table",title="Table 5. The weaker racial gradient and the channel gap, by operating department",cols=[1700,1000,900,1000,1500,1630,1630],header=["Department","Aldermanic share (%)","Phone gradient","Aldermanic gradient","Difference (se)","Aldermanic − phone gap, 0% Black (se)","Aldermanic − phone gap, 100% Black (se)"],rows=rows,align=["l","c","c","c","c","c","c"],
        note="Gradients are log points of completion time per +1 SD of tract Black share from the pooled model of Table 3, Panel B, estimated within each department; the difference is aldermanic minus phone. The last two columns evaluate the within-tract model of Table 4 at 0 and 100 percent Black share, estimated only where the department has at least 8,000 aldermanic requests. Panel B drops requests completed within about one minute and the three sign-repair types (all in Transportation). Shares are of each department’s resident requests in the speed sample. Standard errors clustered by community area. *** p<0.01, ** p<0.05, * p<0.1.")
def table6q():
    rows=[]
    for y in ("canceled","unresolved","rr30","rr90"):
        o=S10[y]; w=o["within"]["coef"]
        rows.append([o["label"],f"{o['means']['phone']:.2f}",f"{o['means']['digital']:.2f}",f"{o['means']['alderman']:.2f}",cell(w["digital"]),cell(w["alder"]),cell(w["alder_B"]),n_(o["n"])])
    rows.append(["Comparable-closure sample (re-reporting only)"])
    for y,lab in (("rr30","Re-reported within 30 days"),("rr90","Re-reported within 90 days")):
        o=S16[y]; w=o["coef"]; rows.append([lab,f"{o['means']['phone']:.2f}",f"{o['means']['digital']:.2f}",f"{o['means']['alderman']:.2f}",cell(w["digital"]),cell(w["alder"]),cell(w["alder_B"]),n_(o["n"])])
    return dict(t="table",title="Table 6. Resolution outcomes by reporting channel",cols=[2000,800,800,1000,1300,1300,1300,860],header=["Outcome (percent of requests)","Phone","Web / app","Aldermanic office","Web / app − phone","Aldermanic − phone","Aldermanic × Black share (+1 SD)","N"],rows=rows,align=["l","c","c","c","c","c","c","c"],
        note="Columns 2-4 are channel means. Columns 5-7 come from within-tract linear probability models (outcome × 100, so coefficients are percentage points) with tract, request type × year, month-of-sample, weekday and hour fixed effects, log workload, and channel interactions with Black share, hardship and Hispanic share. Canceled and unresolved use all resident non-duplicate requests created from 1 November 2019. Re-reporting uses completed requests with a full follow-up window and the main paper’s definition: a new resident request of the same type at the same address within 30 or 90 days of closure. The lower panel drops requests completed within about one minute and sign-repair types. Standard errors clustered by community area (77) in parentheses. *** p<0.01, ** p<0.05, * p<0.1.")
def table7c():
    A=[("baseline (post-break)","Baseline (Nov 2019 onward)"),("cluster by ward-period","Clustered by ward-period"),("+ ward-period FE","With ward-period fixed effects"),("full window (from Jan 2019)","Full window (January 2019 onward)")]
    B=[("fixed-scope services","Fixed-scope services only"),("variable-scope services","Variable-scope services only"),("other services","Other services only")]
    D=[("all departments, excluding sign-repair types","Excluding sign-repair types"),("all departments, excluding sub-minute closures","Excluding closures within one minute"),("all departments, excluding both","Excluding both")]
    C=["Lowest-use third of ward-periods","Middle third of ward-periods","Highest-use third of ward-periods","Excluding the 3 highest-use ward-periods","Excluding the 5 highest-use ward-periods","Excluding the 10 highest-use ward-periods"]
    def row(lab,r): return [lab,n_(r["n"]),f"{r['phone'][0]:.3f}",f"{r['alder'][0]:.3f}",f"{r['diff'][0]:.3f}{st(r['diff'][2])} ({r['diff'][1]:.3f})"]
    rows=[["Specification and sample"]]+[row(l,S5[k]) for k,l in A]+[["Type of service"]]+[row(l,S5[k]) for k,l in B]+[["Phone-specific fast closures"]]+[row(l,S14[k]["pooled"]) for k,l in D]+[["Concentration of aldermanic use"]]+[row(c,S12[c]) for c in C]
    return dict(t="table",title="Table 7. Robustness of the weaker racial gradient in aldermanic requests",cols=[3900,1260,1000,1200,2000],header=["","Observations","Phone gradient","Aldermanic gradient","Difference (se)"],rows=rows,align=["l","c","c","c","c"],
        note="Each row re-estimates the pooled model of Table 3, Panel B, on the stated sample or with the stated change. Gradients are log points of completion time per +1 SD of tract Black share; the difference is the aldermanic minus phone gradient. Ward-periods are the 50 wards of the map in force before and after 15 May 2023, ranked by the aldermanic share of their resident requests from November 2019. Fixed-scope, variable-scope and other services follow the classification in the companion paper on race and class. Standard errors clustered by community area unless noted; the three ward-use thirds contain 53, 60 and 64 community areas, so their degrees of freedom are lower. *** p<0.01, ** p<0.05, * p<0.1.")
def tableA1t():
    t=S0["type_mix"]; rows=[["Over-represented among aldermanic requests"]]
    for r in reversed(t["over"]): rows.append([r[0],f"{r[1]:.1f}",f"{r[2]:.1f}",f"{r[3]:+.1f}"])
    rows.append(["Under-represented among aldermanic requests"])
    for r in t["under"]: rows.append([r[0],f"{r[1]:.1f}",f"{r[2]:.1f}",f"{r[3]:+.1f}"])
    return dict(t="table",title="Table A1. Request types most unevenly represented across channels",cols=[4560,1600,1600,1600],header=["Request type","Aldermanic (% of requests)","Phone (% of requests)","Difference (points)"],rows=rows,align=["l","c","c","c"],
        note="Shares of resident requests created from 1 November 2019 in the 789 analytic tracts, within channel. The five most over-represented and four most under-represented types are shown, ranked by the difference.")
