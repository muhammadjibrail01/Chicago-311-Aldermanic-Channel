"""Run steps 2 to 10 of the election analysis and the manuscript build from this folder:  python run_all.py   (resume with --from N)"""
import argparse, os, subprocess, sys
ap = argparse.ArgumentParser(); ap.add_argument("--from", dest="start", type=int, default=2); a = ap.parse_args()
env = dict(os.environ, PYTHONPATH="code", BODY_SZ="21", LINE_SP="252", PARA_AFTER="100", NOTE_SZ="15", MARGIN_TOP="1200", MARGIN_BOT="1100", TBL_SZ="16", FIG_SCALE="90")
steps = [(2, "python code/02_parse_official.py"), (3, "python code/03_parse_aldermanic.py"), (4, "python code/04_parse_mayoral.py"), (5, "python code/05_verify_compiled.py"), (6, "python code/06_build_data.py"),
         (7, "python code/07_election_models.py"), (8, "python code/08_turnover_full.py"), (9, "python doc/build_content2.py && python doc/build_content3.py"), (10, "node doc/render.js doc/content3.json Paper2.docx")]
for k, cmd in steps:
    if k < a.start: continue
    rc = subprocess.run(cmd, shell=True, env=env).returncode; print(f"[{'OK' if rc == 0 else 'FAIL'}] step {k}: {cmd}", flush=True)
    if rc: sys.exit(1)
