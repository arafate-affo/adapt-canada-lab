"""
06_btos_vs_csbc.py
US-Canada comparison of business AI adoption by industry: a first "replication with
Canadian data" of a US measure.

US  : Census Bureau Business Trends and Outlook Survey (BTOS), Sector file, question 7
      ("In the last two weeks, did this business use AI in any of its business functions?"),
      share answering "Yes", average of the biweekly estimates published in 2026 and
      the latest period.
CA  : Canadian Survey on Business Conditions (CSBC), Q2 2026, table 33-10-0167-01
      ("Yes, business used AI for producing goods or delivering services over the last
      12 months"), by NAICS sector; Q3 2026 table 33-10-0207-01 for planned use.

Definitions differ (reference window: 2 weeks vs 12 months; scope: any business
function vs producing goods/delivering services; US question re-worded in Nov. 2025),
so the comparison is indicative. The sector crosswalk is 2-digit NAICS; BTOS codes
wholesale as 42 (Canada: 41), and has sectors 22, 55 and 61 that the CSBC omits.
Output: output/tables/ai_adoption_us_vs_canada_by_sector.csv/.md and figure 8.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
BT = ROOT / "data" / "raw" / "btos" / "Sector.xlsx"
P = ROOT / "data" / "processed"
TAB = ROOT / "output" / "tables"
FIG = ROOT / "output" / "figures"

C = {"blue": "#2a78d6", "orange": "#eb6834", "text": "#0b0b0b", "text2": "#52514e", "grid": "#e6e5e1", "surface": "#fcfcfb"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.facecolor": C["surface"], "axes.facecolor": C["surface"],
                     "axes.grid": True, "grid.color": C["grid"], "grid.linewidth": 0.6, "axes.axisbelow": True,
                     "legend.frameon": False, "axes.edgecolor": C["text2"], "axes.labelcolor": C["text2"],
                     "xtick.color": C["text2"], "ytick.color": C["text2"]})

# ---- US: BTOS sector file
bt = pd.read_excel(BT, sheet_name="Response Estimates")
q7 = bt[(bt["Question ID"] == 7) & (bt["Answer ID"] == 1)].copy()
periods = [c for c in q7.columns if str(c).isdigit()]
p2026 = [c for c in periods if str(c).startswith("2026")]
latest = max(periods, key=lambda c: int(c))


def pct(v):
    v = str(v).strip().replace("%", "")
    return float(v) if v.replace(".", "", 1).isdigit() else np.nan


us = pd.DataFrame({"sector_us": q7["Sector"].astype(str),
                   "us_ai_use_latest": q7[latest].map(pct).values,
                   "us_ai_use_2026_avg": q7[p2026].map(pct).mean(axis=1).values})
MAP = {"11": "11", "21": "21", "23": "23", "31": "31-33", "42": "41", "44": "44-45", "48": "48-49",
       "51": "51", "52": "52", "53": "53", "54": "54", "56": "56", "62": "62", "71": "71", "72": "72",
       "81": "81", "XX": "ALL"}
us["naics"] = us.sector_us.map(MAP)

# ---- Canada: CSBC
ca = pd.read_csv(P / "adaptation_index_industries_canada.csv")
ca_q2 = ca[ca.quarter == "2026Q2"][["naics", "breakdown", "ai_use"]].rename(columns={"ai_use": "ca_ai_use_last12m_Q2"})
ca_q3 = ca[ca.quarter == "2026Q3"][["naics", "ai_use"]].rename(columns={"ai_use": "ca_ai_planned_next12m_Q3"})
cmp_ = (us.merge(ca_q2, on="naics", how="outer").merge(ca_q3, on="naics", how="left"))
cmp_["label"] = (cmp_.breakdown.fillna("BTOS-only sector " + cmp_.sector_us.astype(str))
                 .str.replace(r" \[.*\]$", "", regex=True)
                 .str.replace("North American Industry Classification System (NAICS), all industries", "All industries")
                 .str.replace("Administrative and support, waste management and remediation services", "Administrative and support services"))
cmp_["gap_us_minus_ca_pts"] = cmp_.us_ai_use_2026_avg - cmp_.ca_ai_use_last12m_Q2
cols = ["naics", "label", "us_ai_use_latest", "us_ai_use_2026_avg", "ca_ai_use_last12m_Q2",
        "ca_ai_planned_next12m_Q3", "gap_us_minus_ca_pts"]
out = cmp_[cols].sort_values("us_ai_use_2026_avg", ascending=False).round(1)
out.to_csv(TAB / "ai_adoption_us_vs_canada_by_sector.csv", index=False)
(TAB / "ai_adoption_us_vs_canada_by_sector.md").write_text(
    f"Business AI use by sector: US (BTOS, share 'yes', 2026 biweekly average; latest period {latest}) "
    "vs Canada (CSBC Q2 2026, used AI in last 12 months; Q3 2026, plans to use in next 12 months)\n\n"
    + out.to_markdown(index=False), encoding="utf-8")
print(out.to_string(index=False))

# ---- Figure 8: dumbbell US vs Canada
d = out.dropna(subset=["us_ai_use_2026_avg", "ca_ai_use_last12m_Q2"]).sort_values("us_ai_use_2026_avg")
fig, ax = plt.subplots(figsize=(9.5, 6.2))
y = np.arange(len(d))
ax.hlines(y, d.ca_ai_use_last12m_Q2, d.us_ai_use_2026_avg, color=C["grid"], linewidth=2.5, zorder=1)
ax.scatter(d.us_ai_use_2026_avg, y, s=60, color=C["blue"], zorder=3, label="United States (BTOS, 2026 avg., last 2 weeks)")
ax.scatter(d.ca_ai_use_last12m_Q2, y, s=60, color=C["orange"], zorder=3, label="Canada (CSBC Q2 2026, last 12 months)")
ax.set_yticks(y); ax.set_yticklabels(d.label)
ax.set_xlabel("Share of businesses using AI (%)")
ax.set_title("Business AI adoption by sector, US vs Canada, 2026", loc="left", color=C["text"])
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.09), ncol=2, fontsize=8)
fig.tight_layout()
fig.savefig(FIG / "fig8_ai_adoption_us_vs_canada.png", dpi=160)
fig.savefig(FIG / "fig8_ai_adoption_us_vs_canada.svg")
print("latest BTOS period:", latest, "| 2026 periods:", len(p2026))
