# Step 1: from the three raw 311 CSVs, keep the 49 core request types with a valid community area (reproduces the main paper's 4,648,843 requests)
import pandas as pd, numpy as np, glob, re, pyarrow as pa, pyarrow.parquet as pq
TYPES="""Stray Animal Complaint|Report an Injured Animal|Vicious Animal Complaint|Nuisance Animal Complaint|Pet Wellness Check Request|Street Light Out Complaint|Pothole in Street Complaint|Traffic Signal Out Complaint|Sign Repair Request - All Other Signs|Alley Light Out Complaint|Alley Pothole Complaint|Sidewalk Inspection Request|Inspect Public Way Request|Sign Repair Request - Stop Sign|Street Light Pole Damage Complaint|Snow - Uncleared Sidewalk Complaint|Sign Repair Request - One Way Sign|Building Violation|Buildings - Plumbing Violation|Vacant/Abandoned Building Complaint|No Building Permit and Construction Violation|Sewer Cleaning Inspection Request|Check for Leak|Water On Street Complaint|Water in Basement Complaint|Open Fire Hydrant Complaint|Sewer Cave-In Inspection Request|No Water Complaint|Low Water Pressure Complaint|Graffiti Removal Request|Rodent Baiting/Rat Complaint|Garbage Cart Maintenance|Abandoned Vehicle Complaint|Weed Removal Request|Tree Debris Clean-Up Request|Blue Recycling Cart|Tree Emergency|Tree Removal Inspection|Sanitation Code Violation|Dead Animal Pick-Up Request|Tree Planting Request|Yard Waste Pick-Up Request|Fly Dumping Complaint|Missed Garbage Pick-Up Complaint|Recycling Pick Up|Ice and Snow Removal Request|Clean Vacant Lot Request|Street Cleaning Request|Snow - Object/Dibs Removal Request""".split("|")
norm=lambda s: re.sub(r"\s+"," ",str(s).replace("–","-").replace("—","-")).strip().lower()
types={norm(k) for k in TYPES}
cols=["SR_NUMBER","SR_TYPE","OWNER_DEPARTMENT","STATUS","ORIGIN","CREATED_DATE","CLOSED_DATE","DUPLICATE","PARENT_SR_NUMBER","COMMUNITY_AREA","WARD","LATITUDE","LONGITUDE","STREET_ADDRESS"]
w=None; n=0
for f in sorted(glob.glob("raw_data/raw311/*.csv")):
    for ch in pd.read_csv(f,usecols=cols,chunksize=500_000,dtype=str):
        ca=pd.to_numeric(ch.COMMUNITY_AREA,errors="coerce"); m=ch.SR_TYPE.map(norm).isin(types)&ca.between(1,77)
        ch=ch[m].copy(); ch["COMMUNITY_AREA"]=ca[m].astype("int16")
        for c in ["CREATED_DATE","CLOSED_DATE"]: ch[c]=pd.to_datetime(ch[c],format="%m/%d/%Y %I:%M:%S %p",errors="coerce")
        ch["WARD"]=pd.to_numeric(ch.WARD,errors="coerce").astype("float32")
        for c in ["LATITUDE","LONGITUDE"]: ch[c]=pd.to_numeric(ch[c],errors="coerce")
        n+=len(ch); t=pa.Table.from_pandas(ch.reset_index(drop=True),preserve_index=False)
        if w is None: w=pq.ParquetWriter("work/core_raw.parquet",t.schema,compression="zstd")
        w.write_table(t)
w.close(); print("rows written:",f"{n:,}")
