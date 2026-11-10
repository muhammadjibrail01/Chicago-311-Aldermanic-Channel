"""Step 4: political-alignment measures from Wikipedia's mayoral pages. (1) 2019 runoff, ward-level Lightfoot vote share (electorate alignment, 2015 map).
(2) Aldermen's runoff endorsements (2019: Lightfoot v. Preckwinkle; 2023: Johnson v. Vallas), matched to the alderman who held each ward after the election."""
import re, json, unicodedata, pandas as pd, numpy as np
D = "data/"
def plain(s):
    s = re.sub(r"<ref.*?(</ref>|/>)", "", s, flags=re.S); s = re.sub(r"\{\{[^{}]*\}\}", "", s); s = re.sub(r"\[\[([^\]|]*\|)?([^\]]*)\]\]", r"\2", s); return re.sub(r"\s+", " ", s).strip()
def last(n):
    n = re.sub(r'"[^"]*"', " ", str(n)); n = re.sub(r"\b(jr|sr|ii|iii|iv)\b\.?", " ", n, flags=re.I); n = unicodedata.normalize("NFKD", n).encode("ascii", "ignore").decode()
    t = re.findall(r"[A-Za-z']+", n); return t[-1].lower() if t else ""
def first(n):
    n = re.sub(r'"[^"]*"', " ", str(n)); n = unicodedata.normalize("NFKD", n).encode("ascii", "ignore").decode(); t = re.findall(r"[A-Za-z']+", n); return t[0].lower() if t else ""
qc = {}
# ---------- (1) 2019 runoff by ward
w19 = open(D + "wiki/mayor2019.wiki", encoding="utf-8").read()
ms = [m for m in re.finditer(r"^(={2,4})\s*Results by ward\s*\1\s*$", w19, flags=re.M)]; st = ms[1].end(); t0 = w19.find('{| class="wikitable collapsible sortable"', st); tab = w19[t0: w19.find("\n|}", t0)]
rows = re.findall(r"^!\s*(?:\[\[[^\]|]*\|)?(\d+)(?:\]\])?\s*\n\|\s*([\d,]+)\s*\|\|\s*([\d.]+)%\s*\|\|\s*([\d,]+)\s*\|\|\s*([\d.]+)%\s*\|\|\s*([\d,]+)\s*\|\|\s*([\d.]+)%", tab, flags=re.M)
rw = pd.DataFrame([dict(ward=int(a), lf_votes=float(b.replace(",", "")), lf_pct=float(c), pk_votes=float(d.replace(",", "")), pk_pct=float(e), total=float(f.replace(",", ""))) for a, b, c, d, e, f, g in rows])
ck = []
def chk(name, ok, detail=""): ck.append(dict(check=name, ok=bool(ok), detail=detail)); print(("PASS  " if ok else "FAIL  ") + name + (f"   [{detail}]" if detail else ""))
chk("2019 runoff ward table has 50 wards", len(rw) == 50 and sorted(rw.ward) == list(range(1, 51)))
chk("ward votes sum to the page's citywide runoff totals", abs(rw.lf_votes.sum() - 386039) < 5 and abs(rw.pk_votes.sum() - 137765) < 5, f"Lightfoot {rw.lf_votes.sum():,.0f}, Preckwinkle {rw.pk_votes.sum():,.0f}")
chk("Lightfoot won all 50 wards (page prose)", (rw.lf_pct > 50).all(), f"range {rw.lf_pct.min():.1f}-{rw.lf_pct.max():.1f}; the legend range is 54-88")
chk("percentages equal votes/total", (abs(100 * rw.lf_votes / rw.total - rw.lf_pct) < 0.02).all())
rw.to_csv(D + "mayor2019_runoff_by_ward.csv", index=False)
# ---------- (2) endorsements
def aldermen_in(text):
    out = []
    for ln in text.split("\n"):
        if not ln.lstrip().startswith("*"): continue
        pl = re.sub(r"<ref.*?(</ref>|/>)", "", ln, flags=re.S)
        if not re.search(r"(?i)alder(wo)?man|alderperson|alderman-elect", pl) and "aldermen" not in text[:0]: continue
        wd = re.search(r"(\d{1,2})(?:st|nd|rd|th)\s+[Ww]ard", pl) or re.search(r"[Ww]ard\s+(\d{1,2})", pl)
        nm = re.search(r"\[\[([^\]|]+)(?:\|([^\]]*))?\]\]", pl)
        if wd and nm: out.append(dict(name=(nm.group(2) or nm.group(1)), ward=int(wd.group(1)), line=plain(pl)[:110]))
    return out
_s = re.search(r"^={2,4}\s*Endorsements\s*={2,4}\s*$", w19, flags=re.M).end(); _r = [m for m in re.finditer(r"^===\s*Runoff\s*===\s*$", w19[_s:], flags=re.M)][0]; _s += _r.end()
_e = re.search(r"^==[^=]", w19[_s:], flags=re.M); seg19 = w19[_s: _s + _e.start()]
bx = [m.start() for m in re.finditer(r"\{\{Endorsements box", seg19)]; end19 = {}
for k, b in enumerate(bx):
    blk = seg19[b: bx[k + 1] if k + 1 < len(bx) else len(seg19)]; end19[re.search(r"title\s*=\s*([^\n|]*)", blk).group(1).strip()] = aldermen_in(blk)
w23 = open(D + "wiki/mayor2023.wiki", encoding="utf-8").read(); s23 = re.search(r"^={2,4}\s*Runoff endorsements\s*={2,4}\s*$", w23, flags=re.M).end(); seg23 = w23[s23: s23 + w23[s23:].find("===Runoff results")]
end23 = {}
for key, nm in (("johnsonendorsements", "Brandon Johnson"), ("vallasendorsements", "Paul Vallas"), ("declinedtoendorse", "Declined to endorse")):
    a = seg23.find(f'section begin="{key}"'); b = seg23.find(f'section end="{key}"'); blk = seg23[a:b]
    c = blk.find(";Chicago aldermen"); nxt = re.search(r"^;[A-Z]|^'''[A-Z]", blk[c + 5:], flags=re.M); blk = blk[c: c + 5 + (nxt.start() if nxt else len(blk))] if c >= 0 else ""
    end23[nm] = [dict(x, line=x["line"]) for x in aldermen_in(blk.replace(";Chicago aldermen", "") if False else blk) ] if blk else []
# the 2023 lists sit under ';Chicago aldermen' so the keyword test is not needed: re-parse those bullets without it
def bullets_with_ward(blk):
    out = []
    for ln in blk.split("\n"):
        if not ln.lstrip().startswith("*"): continue
        pl = re.sub(r"<ref.*?(</ref>|/>)", "", ln, flags=re.S); wd = re.search(r"(\d{1,2})(?:st|nd|rd|th)\s+[Ww]ard", pl); nm = re.search(r"\[\[([^\]|]+)(?:\|([^\]]*))?\]\]", pl)
        if wd and nm: out.append(dict(name=(nm.group(2) or nm.group(1)), ward=int(wd.group(1)), line=plain(pl)[:110]))
    return out
for key, nm in (("johnsonendorsements", "Brandon Johnson"), ("vallasendorsements", "Paul Vallas"), ("declinedtoendorse", "Declined to endorse")):
    a = seg23.find(f'section begin="{key}"'); b = seg23.find(f'section end="{key}"'); blk = seg23[a:b]; c = blk.find(";Chicago aldermen")
    nxt = re.search(r"^;[A-Z]|^'''[A-Z]", blk[c + 5:], flags=re.M); sub = blk[c: c + 5 + nxt.start()] if (c >= 0 and nxt) else (blk[c:] if c >= 0 else ""); end23[nm] = bullets_with_ward(sub)
print("\n2019 runoff endorsements by aldermen (bullets with an alderman and a ward):", {k: len(v) for k, v in end19.items()})
print("2023 runoff endorsements, ';Chicago aldermen' lists:", {k: len(v) for k, v in end23.items()})
json.dump({"2019": end19, "2023": end23}, open(D + "endorsements_raw.json", "w"), indent=1)
we = pd.read_csv(D + "ward_elections.csv")
def match(end, year, winner_col, names):
    """endorsers matched to the alderman who held the ward after the election (surname + first name, or surname when first names differ only by nickname)"""
    res = {}
    for cand, lst in end.items():
        for e in lst:
            w = e["ward"]; row = we[(we.year == year) & (we.ward == w)]
            if row.empty: continue
            wn = row.iloc[0][winner_col]
            if isinstance(wn, str) and last(wn) == last(e["name"]) and (first(wn)[:3] == first(e["name"])[:3] or first(wn)[0] == first(e["name"])[0]): res.setdefault(w, set()).add(cand)
    return res
m19 = match(end19, 2019, "final_winner", None); m23 = match(end23, 2023, "final_winner", None)
rows = []
for y, m, win, run in ((2019, m19, "Lori Lightfoot", "Toni Preckwinkle"), (2023, m23, "Brandon Johnson", "Paul Vallas")):
    for w in range(1, 51):
        r = we[(we.year == y) & (we.ward == w)].iloc[0]; cs = m.get(w, set())
        cont = bool(r.incumbent_ran and r.incumbent_won) and not (y == 2019 and r.appointed_midterm == 1)      # the same person held the ward before and after the election
        cat = ("aligned" if win in cs else "opposed" if run in cs else "none") if cont else "unknown"
        rows.append(dict(year=y, ward=w, endorsed=";".join(sorted(cs)), continuing_incumbent=int(cont), alignment=cat))
al = pd.DataFrame(rows); al.to_csv(D + "ward_alignment.csv", index=False)
print("\nalignment categories by period (aligned = endorsed the eventual mayor; opposed = endorsed the runner-up; none = continuing alderman with no listed endorsement; unknown = new or replaced alderman):")
print(pd.crosstab(al.year, al.alignment).to_string())
# validation against the 2023 page's own legend ("endorsements by incumbent aldermen": Johnson 14, Vallas 22): count sitting aldermen only
def sitting(lst):
    out = []
    for x in lst:
        m = re.search(r"ward\s*\((\d{4})\s*[\u2013-]\s*([^),]*)", x["line"]); former = bool(m and m.group(2).strip().isdigit())      # tenure right after the ward has an end year
        if "elect" not in x["line"].lower() and not former: out.append(x)
    return out
sj, sv = len(sitting(end23["Brandon Johnson"])), len(sitting(end23["Paul Vallas"]))
chk("2023 legend: sitting aldermen listed for Vallas equal the page's 22", sv == 22, f"parsed {sv}")
chk("2023 legend: sitting aldermen listed for Johnson are within one of the page's 14", abs(sj - 14) <= 1, f"parsed {sj}; the page's own list and legend differ by one")
qc["checks"] = ck; json.dump(qc, open(D + "mayoral_qc.json", "w"), indent=1, default=str)
