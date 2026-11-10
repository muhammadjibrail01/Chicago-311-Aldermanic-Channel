"""Step 7: electoral incentives and political alignment. (0) replication checks against the stored results of the companion analysis; (1) channel gaps (aldermanic and web/app relative to phone,
within tract) interacted with ward-period political variables; (2) the 2023 turnover. Preferred sample: the comparable-closure sample (Section 3.2)."""
import sys, time, json, os; sys.path.insert(0, "code"); sys.path.insert(0, "code")
from p2lib import *
D = "data/"; OUT = "results/S19_election.json"; T0 = time.time()
R = json.load(open(OUT)) if os.path.exists(OUT) else {}
def log(m): print(f"[{time.time()-T0:6.0f}s] {m}", flush=True)
def save(): json.dump(R, open(OUT, "w"), indent=1, default=float)
SIGN = ["Sign Repair Request - All Other Signs", "Sign Repair Request - Stop Sign", "Sign Repair Request - One Way Sign"]
d = load("2019-11-01", extra=("ward_new",)); log(f"speed sample loaded: {len(d):,} (paper: 3,055,485)")
dc = d[(d.lhrs >= 0.0166) & ~d.type.astype(str).isin(SIGN)].copy(); log(f"comparable-closure sample: {len(dc):,} (stored: 2,896,497)")
# ---------------- ward-period political variables (compiled tables, with the runoff margin taken from the official proclamations)
we = pd.read_csv(D + "ward_elections.csv"); we["wp"] = we.period * 100 + we.ward
off = pd.read_csv(D + "official_runoff_results.csv"); o = off[off.office == "Alderman"]
om = o.groupby(["year", "ward"]).apply(lambda g: 100 * (g.votes.max() - g.votes.min()) / g.total.iloc[0]).rename("off_margin").reset_index(); om["wp"] = om.year.map({2019: 1, 2023: 2}) * 100 + om.ward
we = we.merge(om[["wp", "off_margin"]], on="wp", how="left")
al = pd.read_csv(D + "ward_alignment.csv"); al["wp"] = al.year.map({2019: 1, 2023: 2}) * 100 + al.ward; we = we.merge(al[["wp", "alignment"]], on="wp", how="left")
lf = pd.read_csv(D + "mayor2019_runoff_by_ward.csv"); we = we.merge(lf[["ward", "lf_pct"]].assign(wp=lambda x: 100 + x.ward)[["wp", "lf_pct"]], on="wp", how="left")
z = lambda s: (s - s.mean()) / s.std()
we["safe_z"] = z(we.fr_share); we["runoff"] = we.runoff.astype(float); we["newh"] = we.new_holder.astype(float)
we["margin_z"] = np.where(we.runoff == 1, z(we.off_margin.where(we.runoff == 1)), np.nan)
we["aligned"] = np.where(we.alignment == "unknown", np.nan, (we.alignment == "aligned").astype(float)); we["opposed"] = np.where(we.alignment == "unknown", np.nan, (we.alignment == "opposed").astype(float))
we["lf_z"] = np.where(we.period == 1, z(we.lf_pct.where(we.period == 1)), np.nan); we["appt"] = we.appointed_midterm.astype(float)
we.to_csv(D + "ward_period_variables.csv", index=False)
V = we.set_index("wp")
for df in (d, dc):
    for k in ("safe_z", "runoff", "newh", "margin_z", "aligned", "opposed", "lf_z", "appt"): df[k] = df.wp.map(V[k]).astype("float32")
    df["per2"] = (df.period == 2).astype("float32")
    for ch in ("alder", "digital"): df[f"{ch}_per2"] = (df[ch] * df.per2).astype("float32")
def addP(df, names):
    cols = []
    for P in names:
        for ch in ("alder", "digital"): df[f"{ch}_{P}"] = (df[ch] * df[P]).astype("float32"); cols += [f"{ch}_{P}"]
        cols.append(P)
    return cols
FE = FE0 + ["tract"]; PER = ["alder_per2", "digital_per2"]
def run(key, df, names, label, per2=True, fes=FE, cluster="wp"):
    if key in R: log(f"cached {key}"); return
    cols = addP(df, names); X = X3 + cols + (PER if per2 else []); r = reg(df, "lhrs", X, fes, cluster)
    keys = [c for c in cols] + ["alder", "digital"]; R[key] = dict(label=label, n=int(r.n), G=int(r.G), coef={k: [float(r.b[k]), r.se(k), r.p(k)] for k in keys},
                                                                  wald_alder=r.wald([f"alder_{P}" for P in names]), wald_digital=r.wald([f"digital_{P}" for P in names])); save()
    log(f"{key}: n={r.n:,} G={r.G} | " + "; ".join(f"alder_{P} {r.b['alder_'+P]:.3f} ({r.se('alder_'+P):.3f}) web_{P} {r.b['digital_'+P]:.3f} ({r.se('digital_'+P):.3f})" for P in names))
# ---------------- (0) replication of stored results
if "rep_M1" not in R:
    r = reg(d, "lhrs", X1, FE0, "ca"); R["rep_M1"] = dict(n=int(r.n), alder_B=[float(r.b["alder_B"]), r.se("alder_B")], z_pct_black=[float(r.b["z_pct_black"]), r.se("z_pct_black")]); save()
    S6 = json.load(open("results/S6_main.json"))["M1"]["coef"]
    log(f"REPLICATION M1: n={r.n:,} (stored {json.load(open('results/S6_main.json'))['M1']['n']:,}); alder_B {r.b['alder_B']:.4f} ({r.se('alder_B'):.4f}) vs stored {S6['alder_B'][0]:.4f} ({S6['alder_B'][1]:.4f}); z_pct_black {r.b['z_pct_black']:.4f} vs {S6['z_pct_black'][0]:.4f}")
if "rep_within" not in R:
    r = reg(dc, "lhrs", X3, FE, "ca"); S16 = json.load(open("results/S16_comparable_pooled.json"))["pooled_within"]
    R["rep_within"] = dict(n=int(r.n), alder=[float(r.b["alder"]), r.se("alder")], alder_B=[float(r.b["alder_B"]), r.se("alder_B")]); save()
    log(f"REPLICATION comparable within-tract: n={r.n:,} (stored {S16['n']:,}); alder {r.b['alder']:.4f} ({r.se('alder'):.4f}) vs stored {S16['coef']['alder'][0]:.4f} ({S16['coef']['alder'][1]:.4f}); alder_B {r.b['alder_B']:.4f} vs {S16['coef']['alder_B'][0]:.4f}")
# ---------------- (1) electoral incentives (comparable-closure sample, clustered by ward-period)
run("safety", dc, ["safe_z"], "seat safety (first-round winner share, +1 SD)")
run("runoff_new", dc, ["runoff", "newh"], "runoff required; new office-holder")
run("all3", dc, ["safe_z", "runoff", "newh"], "seat safety, runoff and new office-holder together")
run("margin_official", dc[dc.runoff == 1].copy(), ["margin_z"], "runoff wards only: official runoff margin (+1 SD)")
# ---------------- (2) alignment
da = dc[dc.aligned.notna()].copy(); run("align_endorse", da, ["aligned", "opposed"], "endorsed the eventual mayor (aligned) or the runner-up (opposed), relative to no recorded endorsement")
dl = dc[(dc.period == 1)].copy(); run("align_vote", dl, ["lf_z"], "ward's runoff vote for the eventual mayor, 2019 (+1 SD); Lightfoot term only", per2=False)
dl2 = dl[dl.aligned.notna()].copy(); run("align_both", dl2, ["aligned", "opposed", "lf_z"], "endorsement and ward vote together; Lightfoot term only", per2=False)
import gc; del da, dl, dl2; gc.collect()
# ---------------- robustness: full speed sample, and without mid-term appointee wards
run("safety_full", d, ["safe_z"], "seat safety; full speed sample"); run("align_endorse_full", d[d.aligned.notna()].copy(), ["aligned", "opposed"], "alignment by endorsement; full speed sample")
run("safety_noappt", dc[dc.appt != 1].copy(), ["safe_z"], "seat safety; excluding wards with a mid-term appointee"); gc.collect()
run("align_vote_full", d[d.period == 1].copy(), ["lf_z"], "ward vote for the mayor; full speed sample, Lightfoot term", per2=False); del d; gc.collect()
# ---------------- (3) the 2023 turnover: locations whose 2023-map ward elected a new office-holder
n23 = we[we.period == 2].set_index("ward").newh
for df in (dc,):
    df["exposed"] = df.ward_new.map(n23).astype("float32"); df["post"] = (df.created >= pd.Timestamp("2023-05-15")).astype("float32"); df["post_exp"] = (df.post * df.exposed).astype("float32")
    for ch in ("alder", "digital"):
        df[f"{ch}_post"] = (df[ch] * df.post).astype("float32"); df[f"{ch}_exp"] = (df[ch] * df.exposed).astype("float32"); df[f"{ch}_post_exp"] = (df[ch] * df.post * df.exposed).astype("float32")
if "turnover" not in R:
    dd = dc[dc.exposed.notna()].copy(); X = X3 + ["alder_post", "digital_post", "alder_exp", "digital_exp", "alder_post_exp", "digital_post_exp", "post_exp"]
    r = reg(dd, "lhrs", X, FE, "ward_new"); R["turnover"] = dict(n=int(r.n), G=int(r.G), share_exposed=float(dd.exposed.mean()), coef={k: [float(r.b[k]), r.se(k), r.p(k)] for k in X[len(X3):]}); save()
    log(f"turnover: n={r.n:,} G={r.G}; alder_post_exp {r.b['alder_post_exp']:.3f} ({r.se('alder_post_exp'):.3f}); web {r.b['digital_post_exp']:.3f} ({r.se('digital_post_exp'):.3f}); alder_exp {r.b['alder_exp']:.3f} ({r.se('alder_exp'):.3f})")
log("done")
