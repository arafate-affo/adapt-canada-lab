"""
08_geocode_ridings.py
Attach a 2023-Representation-Order federal electoral district to program awards that the
proactive-disclosure dataset publishes without a riding number (CED-Quebec, ACOA, AAFC...),
using the recipient's postal code and the open Represent API (Open North,
https://represent.opennorth.ca, boundary set "federal-electoral-districts-2023-representation-order").

Represent returns the districts containing the postal code's centroid; rural postal codes
can span several ridings, so the match is approximate (flag `fed_match` = "postal_centroid").
The official alternative is Statistics Canada's Postal Code Conversion File (licensed, via
the university Data Liberation Initiative). Results are cached in
data/processed/postal_to_fed_2023.csv so the API is only called for new postal codes
(rate limit: ~60 requests per minute; this script waits 1.1 s between calls).
"""
from pathlib import Path
import time
import json
import urllib.request
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "data" / "processed"
CACHE = P / "postal_to_fed_2023.csv"
SET = "federal-electoral-districts-2023-representation-order"

awards = pd.read_csv(P / "programs_tariff_awards.csv", dtype=str)
pcs = (awards.loc[awards.fed_code.isna(), "recipient_postal_code"].dropna()
       .str.replace(r"\s+", "", regex=True).str.upper().unique())
cache = pd.read_csv(CACHE, dtype=str) if CACHE.exists() else pd.DataFrame(columns=["postal_code", "fed_code", "fed_name", "status"])
done = set(cache.postal_code)
rows = []
for i, pc in enumerate([p for p in pcs if p not in done]):
    url = f"https://represent.opennorth.ca/postcodes/{pc}/"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "adapt-canada-lab research script"})
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.load(r)
        hit = [b for b in d.get("boundaries_centroid", []) + d.get("boundaries_concordance", []) if SET in b.get("url", "")]
        if hit:
            rows.append({"postal_code": pc, "fed_code": hit[0]["external_id"], "fed_name": hit[0]["name"], "status": "ok"})
        else:
            rows.append({"postal_code": pc, "fed_code": None, "fed_name": None, "status": "no_2023_boundary"})
    except Exception as e:  # 404 for unknown postal codes, timeouts
        rows.append({"postal_code": pc, "fed_code": None, "fed_name": None, "status": f"error:{type(e).__name__}"})
    if (i + 1) % 25 == 0:
        pd.concat([cache, pd.DataFrame(rows)]).to_csv(CACHE, index=False)
        print(f"{i + 1} postal codes queried", flush=True)
    time.sleep(1.1)
cache = pd.concat([cache, pd.DataFrame(rows)], ignore_index=True)
cache.to_csv(CACHE, index=False)
print(cache.status.value_counts().to_dict())
