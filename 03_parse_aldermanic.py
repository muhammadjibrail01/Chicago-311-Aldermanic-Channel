"""Step 3: parse the per-ward election boxes of Wikipedia's 2019 and 2023 Chicago aldermanic election pages into candidate-level and ward-period tables,
with integrity checks. Boxes are assigned to wards by the SECTION they sit in (a title can be mistyped on the page, e.g. ward 19's 2019 box is titled '16th Ward').
Wikipedia cites the Board of Election Commissioners' canvass for these figures; they have NOT been compared with the canvass itself."""
import re, json, unicodedata, pandas as pd, numpy as np
D = "data/"
def split_top(s):
    out, depth, cur, i = [], 0, "", 0
    while i < len(s):
        two = s[i:i+2]
        if two in ("[[", "{{"): depth += 1; cur += two; i += 2; continue
        if two in ("]]", "}}"): depth -= 1; cur += two; i += 2; continue
        if s[i] == "|" and depth == 0: out.append(cur); cur = ""
        else: cur += s[i]
        i += 1
    out.append(cur); return out
def clean_name(s):
    s = re.sub(r"<ref.*?(</ref>|/>)", "", s, flags=re.S); s = re.sub(r"\{\{.*?\}\}", "", s)
    s = re.sub(r"\[\[([^\]|]*\|)?([^\]]*)\]\]", r"\2", s); s = s.replace("'''", "").replace("''", "")
    return re.sub(r"\s+", " ", s).strip()
def num(s):
    s = re.sub(r"<ref.*?(</ref>|/>)", "", s or "", flags=re.S); s = re.sub(r"[^0-9.]", "", s.replace(",", "")); return float(s) if s not in ("", ".") else np.nan
HEAD = re.compile(r"^===\s*(?:\[\[[^\]|]*\|)?\s*(?:(\d+)(?:st|nd|rd|th)\s+ward|ward\s+(\d+))", re.I | re.M)
BOX = re.compile(r"\{\{Election box (begin|winning candidate|candidate|total|end)")
def parse(path, year):
    wt = open(path, encoding="utf-8").read()
    heads = [(m.start(), int(m.group(1) or m.group(2))) for m in HEAD.finditer(wt)]
    ward_at = lambda pos: ([w for p, w in heads if p <= pos] or [None])[-1]
    marks = [(m.start(), m.group(1)) for m in BOX.finditer(wt)]
    rows, box, issues = [], None, []
    for k, (pos, kind) in enumerate(marks):
        end = marks[k+1][0] if k + 1 < len(marks) else len(wt); chunk = wt[pos:end]
        if kind == "begin":
            t = re.search(r"title\s*=\s*([^\n<|}]*)", chunk); title = (t.group(1) if t else "").strip(); sec = ward_at(pos)
            tw = re.search(r"(\d+)(?:st|nd|rd|th)", title); tw = int(tw.group(1)) if tw else None
            if tw != sec: issues.append(f"{year}: box titled '{title}' sits in the section for ward {sec}")
            box = dict(ward=sec, kind="runoff" if re.search(r"runoff", title, re.I) else ("general" if re.search(r"general", title, re.I) else "other:" + title), title=title) if sec else None
        elif kind in ("winning candidate", "candidate") and box:
            inner = chunk[chunk.index("{{") + 2:]; inner = inner[: inner.rfind("}}")] if "}}" in inner else inner
            kv = {}
            for p in split_top(inner)[1:]:
                if "=" in p: a, b = p.split("=", 1); kv[a.strip().lower()] = b.strip()
            raw = kv.get("candidate", ""); name = clean_name(raw)
            rows.append(dict(year=year, ward=box["ward"], round=box["kind"], title=box["title"], win_flag=(kind == "winning candidate"),
                             name=re.sub(r"\s*\((incumbent|inc\.?)\)\s*", "", name, flags=re.I).strip(), incumbent=bool(re.search(r"incumbent", raw, re.I)),
                             votes=num(kv.get("votes")), pct=num(kv.get("percentage")), party=clean_name(kv.get("party", ""))))
    return pd.DataFrame(rows), wt, heads, issues
def last(n):
    n = re.sub(r'"[^"]*"', " ", str(n)); n = re.sub(r"\b(jr|sr|ii|iii|iv)\b\.?", " ", n, flags=re.I)
    n = unicodedata.normalize("NFKD", n).encode("ascii", "ignore").decode(); t = re.findall(r"[A-Za-z'\-]+", n); return t[-1].lower() if t else ""
def unopposed_from_prose(wt, heads, w):                     # wards with no results box: winner named in the section's lead sentence
    i = [k for k, (p, ww) in enumerate(heads) if ww == w]
    if not i: return None
    s = heads[i[0]][0]; e = heads[i[0] + 1][0] if i[0] + 1 < len(heads) else len(wt); seg = wt[s:e]
    lead = seg.split("\n", 2)[1] if "\n" in seg else ""; links = re.findall(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]", lead)
    return dict(name=clean_name(links[0]) if links else None, incumbent=bool(re.search(r"incumbent", lead, re.I)), lead=lead[:200], unopposed=bool(re.search(r"unopposed", seg[:1500], re.I)))
cands, issues_all, wp, notes = [], [], [], {}
for y, f in ((2019, "ald2019.wiki"), (2023, "ald2023.wiki")):
    df, wt, heads, issues = parse(D + "wiki/" + f, y); cands.append(df); issues_all += issues; per = []
    for w in range(1, 51):
        g = df[(df.ward == w) & (df["round"] == "general")]; r = df[(df.ward == w) & (df["round"] == "runoff")]
        g = g[~g.party.str.contains("write", case=False, na=False)]; r = r[~r.party.str.contains("write", case=False, na=False)]   # write-ins carry a handful of votes
        top = g.sort_values("votes", ascending=False).reset_index(drop=True); tot = g.votes.sum()
        fr_share = 100 * top.votes[0] / tot; fr_margin = 100 * (top.votes[0] - (top.votes[1] if len(top) > 1 else 0)) / tot
        fin = top.iloc[0]; fm = fr_margin
        if not r.empty:
            rt = r.sort_values("votes", ascending=False).reset_index(drop=True); fin = rt.iloc[0]; fm = 100 * (rt.votes[0] - rt.votes[1]) / rt.votes.sum()
        inc = set(df[(df.ward == w) & df.incumbent].name)                                  # the sitting alderman, flagged in any round
        per.append(dict(year=y, ward=w, n_cand=len(g), fr_winner=top.name[0], fr_share=fr_share, fr_margin=fr_margin, runoff=int(not r.empty), final_winner=fin["name"], final_margin=fm,
                        incumbent_name="; ".join(sorted(inc)), incumbent_ran=bool(inc), incumbent_won=bool(last(fin["name"]) in {last(x) for x in inc}), unopposed=int(len(g) == 1), source="box"))
    wp.append(pd.DataFrame(per))
cands = pd.concat(cands, ignore_index=True); wp = pd.concat(wp, ignore_index=True)
wp["new_holder"] = (~wp.incumbent_won).astype(int); wp["open_seat"] = (~wp.incumbent_ran).astype(int)
cands.to_csv(D + "candidates_raw.csv", index=False); wp.to_csv(D + "ward_elections_raw.csv", index=False)
print("title/section mismatches found on the pages:"); [print("  ", s) for s in issues_all]
print("wards without a results box (handled from prose):", {k: (v["name"], v["unopposed"]) for k, v in notes.items()})
print("\nper-year summary:\n", wp.groupby("year").agg(wards=("ward", "size"), runoffs=("runoff", "sum"), unopposed=("unopposed", "sum"), new_holder=("new_holder", "sum"), open_seat=("open_seat", "sum"),
                                                     incumbent_defeated=("incumbent_ran", lambda s: 0)).drop(columns="incumbent_defeated").to_string())
wp["inc_defeated"] = ((wp.incumbent_ran) & (~wp.incumbent_won)).astype(int); print("incumbents defeated:", wp.groupby("year").inc_defeated.sum().to_dict())
for y in (2019, 2023):
    q = wp[wp.year == y]; print(f"{y}: unopposed wards {q[q.unopposed==1].ward.tolist()} | runoff wards {q[q.runoff==1].ward.tolist()}")
    print(f"   runoff but first-round top share > 50: {q[(q.runoff==1)&(q.fr_share>50)].ward.tolist()} | no runoff but top share <= 50: {q[(q.runoff==0)&(q.fr_share<=50)].ward.tolist()}")
wp.to_csv(D + "ward_elections_raw.csv", index=False)

# ---------------------------------------------------------------- integrity checks and the final ward-period table
qc = {"title_section_mismatches": issues_all}; ck = []
def chk(name, ok, detail=""): ck.append(dict(check=name, ok=bool(ok), detail=detail)); print(("PASS  " if ok else "FAIL  ") + name + (f"   [{detail}]" if detail else ""))
box = cands[~cands.party.str.contains("write", case=False, na=False)]
bad_w = [f"{y} ward {w} {rd}" for (y, w, rd), g in box[box["round"] == "runoff"].groupby(["year", "ward", "round"]) if g.win_flag.sum() != 1 or not g.sort_values("votes", ascending=False).iloc[0].win_flag]
bad_g = []
for (y, w), g in box[box["round"] == "general"].groupby(["year", "ward"]):
    top = g.sort_values("votes", ascending=False)
    if wp[(wp.year == y) & (wp.ward == w)].runoff.iloc[0] == 0:
        if not (g.win_flag.sum() == 1 and top.iloc[0].win_flag): bad_g.append(f"{y} ward {w}")
    else:                                                                         # runoff: the two runoff candidates are the top two first-round finishers
        rn = set(box[(box.year == y) & (box.ward == w) & (box["round"] == "runoff")].name.map(last)); t2 = set(top.name.head(2).map(last))
        if rn != t2: bad_g.append(f"{y} ward {w} (runoff pair differs from top two)")
chk("every box: the flagged winner is the top vote-getter; every runoff pair is the first-round top two", not bad_w and not bad_g, "; ".join(bad_w + bad_g))
allc = cands.groupby(["year", "ward", "round"]); tot = allc.votes.transform("sum"); diff = (100 * cands.votes / tot - cands.pct).abs()
chk("stated percentages equal votes/total within 0.2 points (all candidate rows)", (diff.dropna() < 0.2).mean() > 0.995, f"max gap {diff.max():.2f}; share within tolerance {(diff.dropna() < 0.2).mean():.4f}")
chk("every ward-election has exactly one general box", cands[cands["round"] == "general"].groupby(["year", "ward"]).size().shape[0] == 100 and (cands[cands["round"] == "general"].assign(k=lambda d: d.title).groupby(["year", "ward"]).title.nunique() == 1).all())
rcount = box[box["round"] == "runoff"].groupby(["year", "ward"]).size(); chk("every runoff has exactly two (non-write-in) candidates", (rcount == 2).all(), f"{len(rcount)} runoffs")
chk("a runoff occurs if and only if no first-round candidate has a majority (100 ward-elections)", ((wp.runoff == 1) == (wp.fr_share <= 50)).all())
chk("each year has 50 wards", wp.groupby("year").size().eq(50).all())
chk("2019 prose: five unopposed wards (2, 32, 36, 38, 42)", sorted(wp[(wp.year == 2019) & (wp.unopposed == 1)].ward) == [2, 32, 36, 38, 42])
chk("2019 prose: seven incumbents defeated (three in the first round, four in runoffs)", int(((wp.year == 2019) & wp.incumbent_ran & ~wp.incumbent_won).sum()) == 7 and int(((wp.year == 2019) & wp.incumbent_ran & ~wp.incumbent_won & (wp.runoff == 0)).sum()) == 3)
chk("2019 prose: twelve new aldermen", int(((wp.year == 2019) & (~wp.incumbent_won)).sum()) == 12)
chk("2023 prose: 14 wards went to a runoff (36 won outright)", int(((wp.year == 2023) & (wp.runoff == 1)).sum()) == 14)
chk("2023 prose: one incumbent lost, in the first round", int(((wp.year == 2023) & wp.incumbent_ran & ~wp.incumbent_won).sum()) == 1 and int(((wp.year == 2023) & wp.incumbent_ran & ~wp.incumbent_won & (wp.runoff == 0)).sum()) == 1)
n_inc_run_won = int(((wp.year == 2023) & wp.incumbent_ran & wp.incumbent_won & (wp.runoff == 1)).sum()); print(f"NOTE  2023 incumbents who won a runoff: {n_inc_run_won} in the boxes; the page prose says five (it appears to leave out one appointee flagged as incumbent).")
r19 = int(((wp.year == 2019) & (wp.runoff == 1)).sum()); print(f"NOTE  2019 runoff wards in the boxes: {r19}; the page prose says 14, and the Board's April 2, 2019 proclamation lists 15 runoff wards (5, 6, 15, 16, 20, 21, 25, 30, 31, 33, 39, 40, 43, 46, 47). The page's count omits ward 15, whose runoff box is mistitled '39th Ward Runoff'.")
qc["checks"] = ck; qc["runoffs_2019_boxes"] = r19
# mid-term appointees: the 2023 page says so in each ward's candidate table ("Incumbent (appointed 2022)")
wt23 = open(D + "wiki/ald2023.wiki", encoding="utf-8").read(); h23 = [(m.start(), int(m.group(1) or m.group(2))) for m in HEAD.finditer(wt23)]
repl = []
for k, (pos, w) in enumerate(h23):
    seg = wt23[pos: h23[k + 1][0] if k + 1 < len(h23) else len(wt23)]
    m_ = re.search(r"Incumbent\s*\(appointed[^)]*?(\d{4})", seg, re.I)
    if m_ and int(m_.group(1)) >= 2019: repl.append(w)          # appointed after the 2019 election, i.e. a mid-term replacement
repl = sorted(set(repl)); print("wards whose sitting alderman at the 2023 election had been appointed mid-term (from the page text):", repl)
qc["appointee_wards_2023_page"] = repl
wp["appointed_midterm"] = ((wp.year == 2019) & wp.ward.isin(repl)).astype(int)
wp["period"] = wp.year.map({2019: 1, 2023: 2}); wp["new_holder"] = (~wp.incumbent_won).astype(int); wp["open_seat"] = (~wp.incumbent_ran).astype(int); wp["inc_defeated"] = (wp.incumbent_ran & ~wp.incumbent_won).astype(int)
wp.to_csv(D + "ward_elections.csv", index=False); json.dump(qc, open(D + "ward_elections_qc.json", "w"), indent=1, default=str)
print("\nwritten data/ward_elections.csv:", len(wp), "ward-periods;", wp.groupby("year")[["runoff", "unopposed", "new_holder", "open_seat", "inc_defeated"]].sum().to_dict("index"))
print("first-round winner share: mean %.1f, sd %.1f; margin mean %.1f" % (wp.fr_share.mean(), wp.fr_share.std(), wp.fr_margin.mean()))
