"""Step 8: the 2023 turnover model on the full speed sample (robustness to the comparable-closure restriction)."""
import sys, json, os, time; sys.path.insert(0, "code")
from p2lib import *
OUT = "results/S19_election.json"; R = json.load(open(OUT)); T0 = time.time()
if "turnover_full" not in R:
    d = load("2019-11-01", extra=("ward_new",)); we = pd.read_csv("data/ward_period_variables.csv"); n23 = we[we.period == 2].set_index("ward").newh
    d["exposed"] = d.ward_new.map(n23).astype("float32"); d["post"] = (d.created >= pd.Timestamp("2023-05-15")).astype("float32"); d["post_exp"] = (d.post * d.exposed).astype("float32")
    for ch in ("alder", "digital"):
        d[f"{ch}_post"] = (d[ch] * d.post).astype("float32"); d[f"{ch}_exp"] = (d[ch] * d.exposed).astype("float32"); d[f"{ch}_post_exp"] = (d[ch] * d.post * d.exposed).astype("float32")
    dd = d[d.exposed.notna()].copy(); del d
    X = X3 + ["alder_post", "digital_post", "alder_exp", "digital_exp", "alder_post_exp", "digital_post_exp", "post_exp"]; r = reg(dd, "lhrs", X, FE0 + ["tract"], "ward_new")
    R["turnover_full"] = dict(n=int(r.n), G=int(r.G), share_exposed=float(dd.exposed.mean()), coef={k: [float(r.b[k]), r.se(k), r.p(k)] for k in X[len(X3):]}); json.dump(R, open(OUT, "w"), indent=1, default=float)
    print(f"[{time.time()-T0:.0f}s] turnover_full: n={r.n:,} G={r.G}; alder_post_exp {r.b['alder_post_exp']:.3f} ({r.se('alder_post_exp'):.3f}); web {r.b['digital_post_exp']:.3f} ({r.se('digital_post_exp'):.3f}); alder_exp {r.b['alder_exp']:.3f} ({r.se('alder_exp'):.3f})")
