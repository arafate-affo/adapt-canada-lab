"""Run the whole pipeline in order (downloads are done by code/00_download.sh)."""
import subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
for s in ["01_clean_csbc.py", "02_build_index.py", "03_elections.py", "03b_pollbypoll.py", "04_trade.py",
          "05_analysis.py", "06_btos_vs_csbc.py", "07_programs.py"]:
    print(f"==> {s}", flush=True)
    subprocess.run([sys.executable, str(HERE / s)], check=True)
