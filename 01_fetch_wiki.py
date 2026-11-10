"""Step 1 (optional): download the wikitext of the four Wikipedia pages used for the compiled election tables into data/wiki/. Archived copies are included in the package;
re-fetching returns the current revision, which may differ from the archived one."""
import json, os, re, time, urllib.parse, urllib.request
PAGES = {"ald2019": "2019 Chicago aldermanic election", "ald2023": "2023 Chicago aldermanic election", "mayor2019": "2019 Chicago mayoral election", "mayor2023": "2023 Chicago mayoral election"}
os.makedirs("data/wiki", exist_ok=True)
def wikitext(title, tries=6):
    u = "https://en.wikipedia.org/w/api.php?action=parse&prop=wikitext&format=json&formatversion=2&redirects=1&page=" + urllib.parse.quote(title)
    for i in range(tries):
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "ChicagoResearchReplication/1.0 (academic replication of a published analysis; low request rate)"})
            with urllib.request.urlopen(req, timeout=60) as r: d = json.load(r)
            return d["parse"]["title"], d["parse"]["wikitext"]
        except Exception as e:
            wait = 12 * (i + 1); print(f"  {title}: {type(e).__name__}; waiting {wait}s"); time.sleep(wait)
    raise SystemExit("could not fetch " + title)
for k, t in PAGES.items():
    time.sleep(8); title, wt = wikitext(t); open(f"data/wiki/{k}.wiki", "w", encoding="utf-8").write(wt); print(f"{k}: '{title}' {len(wt):,} characters")
