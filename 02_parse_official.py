"""Step 2: parse the Chicago Board of Election Commissioners' official canvass proclamations for the April 2, 2019 and April 4, 2023 municipal runoff elections
(PDF files supplied with the project) into tables, and check them against their own totals."""
import re, subprocess, json, unicodedata, pandas as pd, numpy as np
U = "data/official/"; D = "data/"; os_ = {}
def pdftext(f, page, crop=None):
    cmd = ["pdftotext", "-layout", "-f", str(page), "-l", str(page)]
    if crop: cmd += ["-x", str(crop[0]), "-y", "0", "-W", str(crop[1]), "-H", "792"]
    return subprocess.run(cmd + [U + f, "-"], capture_output=True, text=True).stdout
CAND = re.compile(r"^\s*([A-ZÉÁÍÓÚÑ][A-ZÉÁÍÓÚÑ0-9 .,'\"\-]+?)\s{2,}([\d,]+)\s+([\d.]+)%\s*$")
def contests(lines):
    out, cur = [], None
    for ln in lines:
        m = re.match(r"^\s*(Mayor|Treasurer|Alder(?:man|person)\s+(\d+)(?:st|nd|rd|th)\s+Ward)\b", ln)
        if m: cur = dict(office=m.group(1).strip(), ward=int(m.group(2)) if m.group(2) else None, cands=[], total=None); out.append(cur); continue
        if cur is None: continue
        t = re.match(r"^\s*Total\s+([\d,]+)\s*$", ln)
        if t: cur["total"] = int(t.group(1).replace(",", "")); cur = None; continue
        c = CAND.match(ln)
        if c: cur["cands"].append((re.sub(r"\s+", " ", c.group(1)).strip(), int(c.group(2).replace(",", "")), float(c.group(3))))
    return out
res = {}
# ---------------- 2019: single-column layout
t19 = "\n".join(pdftext("Proc-2019-04-02_Elections.pdf", p) for p in (4, 5, 6)); c19 = contests(t19.split("\n"))
bal19 = {}
for ln in pdftext("Proc-2019-04-02_Elections.pdf", 3).split("\n"):
    m = re.match(r"^\s*(\d+)(?:st|nd|rd|th)\s+Ward\s+([\d,]+)\s*$", ln)
    if m: bal19[int(m.group(1))] = int(m.group(2).replace(",", ""))
reg19 = re.search(r"Total Registration and Turnout\s+([\d,]+)\s+([\d,]+)\s+([\d.]+)%", t19)
# ---------------- 2023: ballots by ward and a two-column summary page
bal23 = {}
for p in (4, 5):
    for ln in pdftext("Proc-2023-04-04_Elections.pdf", p).split("\n"):
        m = re.match(r"^\s*(\d+)(?:st|nd|rd|th)\s+Ward\s+([\d,]+)\s*$", ln)
        if m: bal23[int(m.group(1))] = int(m.group(2).replace(",", ""))
left = pdftext("Proc-2023-04-04_Elections.pdf", 6, (0, 300)); right = pdftext("Proc-2023-04-04_Elections.pdf", 6, (300, 312))
c23 = contests(left.split("\n")) + contests(right.split("\n")); reg23 = re.search(r"Total Registration and Turnout\s+([\d,]+)\s+([\d,]+)", left + right)
rows = []
for y, cs in ((2019, c19), (2023, c23)):
    for c in cs:
        tot = c["total"]; top = max(v for _, v, _ in c["cands"])
        for n, v, p in c["cands"]: rows.append(dict(year=y, office="Mayor" if c["office"] == "Mayor" else "Treasurer" if c["office"] == "Treasurer" else "Alderman", ward=c["ward"], candidate=n, votes=v, pct=p, total=tot, winner=int(v == top)))
off = pd.DataFrame(rows); off.to_csv(D + "official_runoff_results.csv", index=False)
bal = pd.DataFrame([dict(year=2019, ward=w, ballots=b) for w, b in bal19.items()] + [dict(year=2023, ward=w, ballots=b) for w, b in bal23.items()]); bal.to_csv(D + "official_ballots_by_ward.csv", index=False)
ck = []
def chk(name, ok, detail=""): ck.append(dict(check=name, ok=bool(ok), detail=detail)); print(("PASS  " if ok else "FAIL  ") + name + (f"   [{detail}]" if detail else ""))
for y, cover in ((2019, [5, 6, 15, 16, 20, 21, 25, 30, 31, 33, 39, 40, 43, 46, 47]), (2023, [4, 5, 6, 10, 11, 21, 24, 29, 30, 36, 43, 45, 46, 48])):
    a = off[(off.year == y) & (off.office == "Alderman")]; ws = sorted(a.ward.unique())
    chk(f"{y}: aldermanic contests parsed are exactly the wards named on the proclamation's cover", ws == cover, f"{len(ws)} wards")
    chk(f"{y}: every contest has two candidates and the candidate votes sum to the printed total", (a.groupby("ward").size() == 2).all() and (a.groupby("ward").votes.sum() == a.groupby("ward").total.first()).all())
    chk(f"{y}: printed percentages equal votes/total (within 0.01)", (abs(100 * a.votes / a.total - a.pct) < 0.011).all(), f"max gap {abs(100 * a.votes / a.total - a.pct).max():.3f}")
    b = bal[bal.year == y]; chk(f"{y}: ballots cast reported for all 50 wards", sorted(b.ward) == list(range(1, 51)), f"citywide sum {b.ballots.sum():,}")
    m = off[(off.year == y) & (off.office == "Mayor")]
    chk(f"{y}: mayoral runoff candidate votes sum to the printed total", m.votes.sum() == m.total.iloc[0], f"{m.votes.sum():,}")
chk("2019: citywide ballots cast equal the printed turnout 526,886", bal[bal.year == 2019].ballots.sum() == 526886, f"{bal[bal.year == 2019].ballots.sum():,}")
chk("2023: citywide ballots cast equal the printed turnout 613,795", bal[bal.year == 2023].ballots.sum() == 613795, f"{bal[bal.year == 2023].ballots.sum():,}")
print("\nmayor 2019:", off[(off.year == 2019) & (off.office == "Mayor")][["candidate", "votes", "pct"]].values.tolist(), "| mayor 2023:", off[(off.year == 2023) & (off.office == "Mayor")][["candidate", "votes", "pct"]].values.tolist())
print("registration/turnout:", reg19.groups() if reg19 else None, reg23.groups() if reg23 else None)
json.dump(ck, open(D + "official_qc.json", "w"), indent=1)
