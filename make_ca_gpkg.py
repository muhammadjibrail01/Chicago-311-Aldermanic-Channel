# community-area polygons for the Paper 1 pipeline (replaces ca.gpkg from the main-paper package)
import pandas as pd, geopandas as gpd
from shapely import wkt
d=pd.read_csv("raw_data/Boundaries_-_Community_Areas_20260923.csv")
g=gpd.GeoDataFrame({"ca":d.AREA_NUMBE.astype(int),"name":d.COMMUNITY.str.title()},geometry=d.the_geom.apply(wkt.loads),crs="EPSG:4326"); g.to_file("work/ca.gpkg",driver="GPKG"); print(len(g))
