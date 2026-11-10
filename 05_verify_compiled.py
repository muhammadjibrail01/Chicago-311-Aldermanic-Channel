"""Step 5: verify the compiled ward-level tables against the official canvass proclamations wherever the two overlap."""
import re, json, unicodedata, pandas as pd, numpy as np
D = "data/"
def last(n):
    n = re.sub(r"['\"][^'\"]*['\"]|''[^']*''", " ", str(n)); n = re.sub(r"\b(jr|sr|ii|iii|iv)\b\.?", " ", n, flags=re.I)
    n = unicodedata.normalize("NFKD", n).encode("ascii", "ignore").decode(); t = re.findall(r"[A-Za-z]+", n); return (t[0][:3] + "-" + t[-1]).lower() if t else ""      # first three letters of the first name + surname (two candidates in 2023 ward 24 are both named Scott)
off = pd.read_csv(D + "official_runoff_results.csv"); cmp_ = pd.read_csv(D + "candidates_raw.csv"); bal = pd.read_csv(D + "official_ballots_by_ward.csv")
o = off[off.office == "Alderman"].copy(); o["k"] = o.candidate.map(last)
w = cmp_[(cmp_["round"] == "runoff") & ~cmp_.party.fillna("").str.contains("write", case=False)].copy(); w["k"] = w.name.map(last)
m = o.merge(w[["year", "ward", "k", "votes"]].rename(columns={"votes": "votes_compiled"}), on=["year", "ward", "k"], how="outer", indicator=True)
ck = []
def chk(name, ok, detail=""): ck.append(dict(check=name, ok=bool(ok), detail=detail)); print(("PASS  " if ok else "FAIL  ") + name + (f"   [{detail}]" if detail else ""))
both = m[m._merge == "both"]
chk("every official runoff candidate (58) is found in the compiled runoff tables, and vice versa", len(both) == len(o) == len(w) == 58, f"matched {len(both)} of {len(o)} official / {len(w)} compiled")
chk("compiled runoff votes equal the official votes for all 58 candidates", (both.votes == both.votes_compiled).all(), f"mismatches: {both[both.votes != both.votes_compiled][['year','ward','k','votes','votes_compiled']].values.tolist()}")
# compiled winners vs official winners in the 29 runoff wards
we = pd.read_csv(D + "ward_elections.csv"); ow = o[o.winner == 1][["year", "ward", "k"]]
j = ow.merge(we[we.runoff == 1][["year", "ward", "final_winner"]].assign(k2=lambda d: d.final_winner.map(last)), on=["year", "ward"])
chk("compiled final winners equal the official winners in all 29 runoff wards", (j.k == j.k2).all() and len(j) == 29, f"{int((j.k == j.k2).sum())} of {len(j)}")
# compiled runoff margin vs official
om = o.groupby(["year", "ward"]).apply(lambda g: (g.votes.max() - g.votes.min()) / g.total.iloc[0] * 100).rename("off_margin").reset_index()
jm = om.merge(we[we.runoff == 1][["year", "ward", "final_margin"]], on=["year", "ward"]); chk("compiled runoff margins equal official margins (within 0.01 points)", (abs(jm.off_margin - jm.final_margin) < 0.011).all(), f"max gap {abs(jm.off_margin - jm.final_margin).max():.4f}")
# 2019 compiled ward-level mayoral table against the official ballots cast by ward
mr = pd.read_csv(D + "mayor2019_runoff_by_ward.csv").merge(bal[bal.year == 2019][["ward", "ballots"]], on="ward")
mr["undervote"] = mr.ballots - mr.total
chk("2019 ward-level mayoral votes sum to the official citywide totals (Lightfoot 386,039; Preckwinkle 137,765)", mr.lf_votes.sum() == 386039 and mr.pk_votes.sum() == 137765, f"{mr.lf_votes.sum():,.0f} / {mr.pk_votes.sum():,.0f}")
chk("2019 ward-level mayoral votes never exceed official ballots cast in the ward", (mr.undervote >= 0).all(), f"ballots minus mayoral votes: min {mr.undervote.min():.0f}, max {mr.undervote.max():.0f}, total {mr.undervote.sum():,.0f}")
print(f"   citywide: ballots {mr.ballots.sum():,} - mayoral votes {mr.total.sum():,.0f} = {mr.undervote.sum():,.0f} ballots without a mayoral vote ({100*mr.undervote.sum()/mr.ballots.sum():.2f}%)")
json.dump(ck, open(D + "verify_qc.json", "w"), indent=1)
