# Step 2: ward polygons for the 2015 map (Paul Smith repository, from Board of Elections files) and the 2023 map (copy of the City data set)
import geopandas as gpd, pandas as pd
from shapely import wkt
old=gpd.read_file("work/chicago_wards_and_precincts-master/chicago_2015_wards.shp")
old=old.rename(columns={[c for c in old.columns if c.lower()=="ward"][0]:"ward"})[["ward","geometry"]]; old["ward"]=old.ward.astype(int)
old=old.set_crs("EPSG:4326") if old.crs is None else old.to_crs("EPSG:4326"); old.to_file("work/ward_old_2015.gpkg",driver="GPKG")
d=pd.read_csv("work/ChicagoWardGeoJSON-main/Boundaries_-_Wards__2023-__20250311.csv")
new=gpd.GeoDataFrame(d[["Ward"]].rename(columns={"Ward":"ward"}),geometry=d["the_geom"].apply(wkt.loads),crs="EPSG:4326"); new.to_file("work/ward_new_2023.gpkg",driver="GPKG"); print(len(old),len(new))
