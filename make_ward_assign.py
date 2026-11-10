# Step 4: assign every core request to a ward under both maps from its coordinates
import geopandas as gpd, pandas as pd, numpy as np, pyarrow.parquet as pq
old=gpd.read_file("work/ward_old_2015.gpkg"); new=gpd.read_file("work/ward_new_2023.gpkg")
pf=pq.ParquetFile("work/core_raw.parquet"); out=[]
for b in pf.iter_batches(batch_size=600_000,columns=["SR_NUMBER","LATITUDE","LONGITUDE"]):
    df=b.to_pandas(); ok=df.LATITUDE.notna()&df.LONGITUDE.notna()
    pts=gpd.GeoDataFrame(df.loc[ok,["SR_NUMBER"]],geometry=gpd.points_from_xy(df.LONGITUDE[ok],df.LATITUDE[ok]),crs="EPSG:4326"); res=df[["SR_NUMBER"]].copy()
    for nm,poly in (("ward_old",old),("ward_new",new)):
        j=gpd.sjoin(pts,poly,how="left",predicate="within"); j=j[~j.index.duplicated(keep="first")]; res.loc[j.index,nm]=j["ward"].values
    out.append(res)
r=pd.concat(out,ignore_index=True)
for c in ("ward_old","ward_new"): r[c]=r[c].astype("float32")
r.to_parquet("work/ward_assign.parquet",index=False); print(r.ward_old.notna().mean(),r.ward_new.notna().mean())
