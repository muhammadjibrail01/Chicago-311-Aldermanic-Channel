"""Step 6: build the Paper 2 analysis file. Starts from the processed core request file (4,648,843 requests; the same file the companion studies use), locates every
resident request in a census tract and in a ward under both ward maps from its coordinates, and flags the ward whose alderman held the location on the creation date."""
import os, io, zipfile, urllib.request, numpy as np, pandas as pd, geopandas as gpd, shapely
from shapely import wkt
B = os.environ.get("P2_WORK", "work") + "/"; P1 = os.environ.get("P1_WORK", "../paper1_replication/work") + "/"
CORE_ZIP = os.environ.get("CORE_ZIP", "../Paper3_replication_package.zip")
os.makedirs(B, exist_ok=True)
core = B + "core_request_file.parquet"
if not os.path.exists(core):
    with zipfile.ZipFile(CORE_ZIP) as z, open(core, "wb") as f: f.write(z.read("p3pkg/data/core_request_file.parquet"))
cols = ["sr", "type", "chan", "year", "ym", "dow", "hod", "ca", "ward", "lwl", "dept", "speed_s", "lhrs", "lat", "lon", "created", "nd"]
c = pd.read_parquet(core, columns=cols); print("core rows:", f"{len(c):,}", "| channels:", c.chan.value_counts().to_dict(), flush=True)
# ---- ward maps: 2015 map (Board of Elections files, via a public repository) and the 2023 map (copy of the City data set)
def fetch(url, dest):
    if not os.path.exists(dest): urllib.request.urlretrieve(url, dest)
fetch("https://codeload.github.com/paulsmith/chicago_wards_and_precincts/zip/refs/heads/master", B + "wards_2015_repo.zip")
fetch("https://codeload.github.com/PaulPrice1/ChicagoWardGeoJSON/zip/refs/heads/main", B + "wards_2023_repo.zip")
zo = zipfile.ZipFile(B + "wards_2015_repo.zip"); zn = zipfile.ZipFile(B + "wards_2023_repo.zip")
base = [n for n in zo.namelist() if n.endswith("chicago_2015_wards.shp")][0][:-4]
for ext in (".shp", ".shx", ".dbf", ".prj", ".cpg"):
    if base + ext in zo.namelist():
        with open(B + "wards2015" + ext, "wb") as f: f.write(zo.read(base + ext))
old = gpd.read_file(B + "wards2015.shp"); old = old.rename(columns={[x for x in old.columns if x.lower() == "ward"][0]: "ward"})[["ward", "geometry"]]
old["ward"] = old.ward.astype(int); old = old.set_crs("EPSG:4326") if old.crs is None else old.to_crs("EPSG:4326")
csvn = [n for n in zn.namelist() if n.endswith("Boundaries_-_Wards__2023-__20250311.csv")][0]; d = pd.read_csv(io.BytesIO(zn.read(csvn)))
new = gpd.GeoDataFrame(d[["Ward"]].rename(columns={"Ward": "ward"}), geometry=d["the_geom"].apply(wkt.loads), crs="EPSG:4326"); new["ward"] = new.ward.astype(int)
print("ward polygons:", len(old), len(new), flush=True)
# ---- tracts: the 789 analytic tracts of the companion studies
t = pd.read_csv(P1 + "tract.csv", dtype={"GEOID": str}).set_index("GEOID"); t = t[t.analytic]
tr = gpd.read_file(P1 + "data/tracts/cb_2023_17_tract_500k.shp").set_index("GEOID").loc[t.index].to_crs("EPSG:4326")
def locate(lon, lat, polys, ids, step=500_000):
    out = np.full(len(lon), -1, dtype=np.int32); ok = np.flatnonzero(~(np.isnan(lon) | np.isnan(lat))); tree = shapely.STRtree(polys.geometry.values)
    for s in range(0, len(ok), step):
        sl = ok[s:s + step]; pi, ti = tree.query(shapely.points(lon[sl], lat[sl]), predicate="within")
        first = pd.Series(ti).groupby(pi).first(); out[sl[first.index.values]] = np.asarray(ids)[first.values]
    return out
r = c[c.chan != "city"].copy(); lon, lat = r.lon.to_numpy(), r.lat.to_numpy()
r["tract"] = locate(lon, lat, tr, np.arange(len(tr))); print("tracts located", flush=True)
r["ward_old"] = locate(lon, lat, old, old.ward.to_numpy()); r["ward_new"] = locate(lon, lat, new, new.ward.to_numpy()); print("wards located", flush=True)
r = r[r.tract >= 0].copy()
for v in ["hardship", "pct_black", "pct_hisp", "poverty", "pct_white"]:
    z = ((t[v] - t[v].mean()) / t[v].std()).to_numpy().astype("float32"); r["z_" + v] = z[r.tract.to_numpy()]
for col in ("ward_old", "ward_new"): r[col] = r[col].where(r[col] > 0).astype("float32")
t1, t2 = pd.Timestamp("2019-05-20"), pd.Timestamp("2023-05-15")       # dates the 2019 and 2023 councils were seated
r["period"] = np.select([r.created < t1, r.created < t2], [0, 1], default=2).astype("int8")
r["aw"] = np.where(r.period == 1, r.ward_old, np.where(r.period == 2, r.ward_new, np.nan))   # ward whose alderman held this location on the request date
r["alder"] = (r.chan == "alderman").astype("int8"); r["digital"] = (r.chan == "digital").astype("int8")
for k in ("type", "chan", "dept"): r[k] = r[k].astype("category")
r = r.drop(columns=["lat", "lon"]); r.to_parquet(B + "p2_data.parquet", index=False)
s = r[r.speed_s & (r.created >= "2019-11-01")]
print(f"resident requests in analytic tracts: {len(r):,} | speed sample from 2019-11-01: {len(s):,} (target 3,055,485)")
print("channels in that sample:", s.chan.value_counts().to_dict(), "| aldermanic share of resident requests by period:", (r.groupby("period").alder.mean() * 100).round(2).to_dict())
