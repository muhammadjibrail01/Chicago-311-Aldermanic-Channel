# repeat-report diagnostic summary (run after diag2.py and build_p2.py)
import pandas as pd, json
f=pd.read_parquet("work/repeat_flags.parquet"); p=pd.read_parquet("work/p2_data.parquet",columns=["sr","chan"]); m=f.merge(p,on="sr")
g=(m.groupby("chan")[["rep30","rep90"]].mean()*100).round(1); json.dump(g.to_dict(),open("results/S9_repeat.json","w")); print(g)
