"""
04_trade.py
Extract provincial merchandise trade with the United States from Statistics Canada
table 12-10-0175-01 (International merchandise trade by province, commodity and
Principal Trading Partners, monthly, customs basis, current dollars).

The raw file is ~700 MB; we stream it in chunks and keep:
  - Trade in {Domestic export, Import}
  - partners in {All countries, United States}
  - all NAPCS commodity groups (14), all provinces
  - months from 2019-01 onward
Output: data/processed/trade_province_us_monthly.csv
        data/processed/trade_province_exposure.csv  (US share of exports, 2024, and
        12-month change in exports to the US, by province and commodity group)
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "trade" / "12100175.csv"
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

usecols = ["REF_DATE", "GEO", "Trade", "North American Product Classification System (NAPCS)",
           "Principal trading partners", "VALUE", "STATUS"]
keep = []
for chunk in pd.read_csv(RAW, usecols=usecols, chunksize=500_000, low_memory=False):
    c = chunk[(chunk["REF_DATE"] >= "2019-01")
              & chunk["Trade"].isin(["Domestic export", "Import"])
              & chunk["Principal trading partners"].isin(["All countries", "United States"])]
    keep.append(c)
d = pd.concat(keep, ignore_index=True)
d = d.rename(columns={"REF_DATE": "month", "GEO": "geo", "Trade": "flow",
                      "North American Product Classification System (NAPCS)": "napcs",
                      "Principal trading partners": "partner", "VALUE": "value_kcad", "STATUS": "status"})
d["year"] = d["month"].str[:4].astype(int)
d.to_csv(OUT / "trade_province_us_monthly.csv", index=False)

# Exposure metrics by province x commodity group
ann = d.groupby(["geo", "flow", "napcs", "partner", "year"])["value_kcad"].sum().unstack("partner")
ann["us_share"] = 100 * ann["United States"] / ann["All countries"]
exp_ = ann.xs("Domestic export", level="flow")
us = exp_["United States"].unstack("year")
share24 = exp_["us_share"].unstack("year")[2024].rename("us_share_exports_2024")
# Jan-Sep comparison 2026 vs 2025 (latest month available is 2026-09)
ytd = (d[(d.flow == "Domestic export") & (d.partner == "United States") & (d.month.str[5:7] <= "09")]
       .groupby(["geo", "napcs", "year"])["value_kcad"].sum().unstack("year"))
ytd["chg_us_exports_ytd_2026_vs_2025_pct"] = 100 * (ytd[2026] / ytd[2025] - 1)
ytd["chg_us_exports_ytd_2025_vs_2024_pct"] = 100 * (ytd[2025] / ytd[2024] - 1)
expo = pd.concat([share24, us[2024].rename("us_exports_2024_kcad"),
                  ytd[["chg_us_exports_ytd_2025_vs_2024_pct", "chg_us_exports_ytd_2026_vs_2025_pct"]]], axis=1).reset_index()
expo.to_csv(OUT / "trade_province_exposure.csv", index=False)
print(d.shape, d.month.min(), d.month.max())
tot = expo[expo.napcs == "Total of all merchandise"].round(1)
print(tot.to_string(index=False))
