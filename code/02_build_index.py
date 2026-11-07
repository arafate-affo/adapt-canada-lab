"""
02_build_index.py
Prototype "Business Adaptive Capacity Index" (BACI) for Canada, built from the
Canadian Survey on Business Conditions (CSBC), 2026 Q1-Q3.

Unit of observation: geography (Canada, provinces, territories) x quarter x breakdown
(all industries, each NAICS sector, employment-size class).

Pillars (each = sum of the shares of businesses reporting the listed actions, in %):
  P1 market_diversification : seek alternative customers outside the US
                              (+ "increase efforts to sell in Canada" when asked, Q2-Q3)
  P2 supply_reconfiguration : alternative suppliers outside the US + domestic sourcing
  P3 technology_investment  : invest in technology improvements
  P5 digital_readiness      : AI use (Q2: used in last 12 months; Q3: plans next 12 months;
                              Q1: adopted new technologies in last 3 years) - reported
                              separately, NOT in the index (question changes across quarters)
  P4 financial_buffers      : trade-related financial tools + inventory build-up + hiring
  D  retrenchment           : delayed investment/expansion + layoffs + price increases
  N  passivity              : share reporting "none" of the actions

Exposure (reported alongside, not inside the index):
  exposure_us_sales   : share of businesses with any direct sales to the US
  exposure_neg_impact : share reporting a (major or minor) negative impact of US tariffs
  tariffs_imposed     : share of exporters whose goods were tariffed by the US

Index: index_raw  = mean(P1_core, P2, P3, P4) in percentage points (interpretable; all four
                    come from the same tariff-action question asked in every quarter)
       index_norm = 0-100 min-max rescaling of index_raw over all provinces x quarters
       net_score  = index_raw - D/3
This is a transparent prototype to be replaced by the weights/method agreed with the
ADAPT data-science team; every input share is kept in the output for re-weighting.
Note: Q1 measures actions TAKEN (past 12 months); Q2-Q3 measure actions PLANNED (next
12 months). The two are kept in the same file but flagged (horizon column).
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
long = pd.read_csv(ROOT / "data" / "processed" / "csbc_long.csv", low_memory=False)
OUT = ROOT / "data" / "processed"

# --- item dictionary: (question label, regex on category) -> item code
ITEMS = {
    "alt_customers":   ("tariff_actions", r"alternative customers outside"),
    "sell_canada":     ("tariff_actions", r"Increase efforts to sell to customers in Canada"),
    "alt_suppliers":   ("tariff_actions", r"alternative suppliers outside"),
    "domestic_source": ("tariff_actions", r"domestic sourcing"),
    "tech_invest":     ("tariff_actions", r"technology improvements"),
    "fin_tools":       ("tariff_actions", r"trade-related financial tools"),
    "inventory":       ("tariff_actions", r"inventory"),
    "hire":            ("tariff_actions", r"^Hire|^Hired"),
    "delay_invest":    ("tariff_actions", r"Delay(?:ed)? Canadian investment"),
    "layoff":          ("tariff_actions", r"^La(?:y|id) off"),
    "raise_prices":    ("tariff_actions", r"^Raise(?:d)? prices"),
    "none":            ("tariff_actions", r", none$|no actions have been taken$"),
    "ai_use":          ("ai", r"^Yes, business (used AI|plans to use artificial intelligence)"),
    "tech_adopt":      ("tech_adoption_training", r"^Business adopted new technologies"),
    "no_us_sales":     ("us_sales_share", r"did not sell to the United States"),
    "tariffs_yes":     ("us_tariffs_on_sales", r"^Yes, tariffs have been imposed"),
}

def tag_items(df):
    df = df.copy()
    df["item"] = pd.Series([None] * len(df), index=df.index, dtype="object")
    df["category2"] = df["category2"].fillna("")
    for code, (q, pat) in ITEMS.items():
        qmask = df.question.str.startswith(q)
        m = qmask & df.category.str.contains(pat, regex=True)
        df.loc[m, "item"] = code
    # negative impact of US tariffs (two-dimension table)
    us_cat = df.category.str.contains(r"^(?:United States|U\.S\.) tariffs|imposition of tariffs by the United States",
                                      regex=True)
    m = (df.question == "tariff_impact_level") & us_cat & df.category2.str.contains("negative")
    df.loc[m, "item"] = "neg_impact"
    # Q2 2025 used a high/medium/low impact scale: high + medium impact is the closest proxy
    m = (df.question == "tariff_impact_level") & us_cat & df.category2.str.contains("high impact|medium impact")
    df.loc[m, "item"] = "neg_impact"
    return df[df.item.notna()]

t = tag_items(long)
keys = ["geo", "geo_code", "quarter", "breakdown", "breakdown_type", "naics"]
wide = (t.groupby(keys + ["item"])["value"].agg(lambda s: s.sum(min_count=1))
        .unstack("item").reset_index())
wide.columns.name = None
for c in list(ITEMS) + ["neg_impact"]:
    if c not in wide:
        wide[c] = np.nan

def nz(s):  # treat missing optional items as 0 but keep track
    return s.fillna(0)

wide["P1_market_diversification"] = nz(wide.alt_customers) + nz(wide.get("sell_canada"))
wide["P1_core"] = wide.alt_customers  # comparable across the three quarters
wide["P2_supply_reconfiguration"] = nz(wide.alt_suppliers) + nz(wide.domestic_source)
wide["P3_technology_investment"] = wide.tech_invest
# Digital readiness is reported as a separate pillar because its source question changes
# across quarters (Q1: new technologies adopted in last 3 years; Q2: AI used in last 12 months;
# Q3: AI use planned in next 12 months). It is NOT part of index_raw.
wide["P5_digital_readiness"] = wide[["ai_use", "tech_adopt"]].max(axis=1)
wide["P4_financial_buffers"] = nz(wide.fin_tools) + nz(wide.inventory) + nz(wide.hire)
wide["D_retrenchment"] = nz(wide.delay_invest) + nz(wide.layoff) + nz(wide.raise_prices)
wide["N_passivity"] = wide["none"]
wide["exposure_us_sales"] = 100 - wide.no_us_sales
wide["exposure_neg_impact"] = wide.neg_impact
wide["tariffs_imposed"] = wide.tariffs_yes
HORIZON = {"2025Q2": "actions taken, past 3m", "2026Q1": "actions taken, past 12m"}
wide["horizon"] = wide.quarter.map(HORIZON).fillna("actions planned, next 12m")
core = ["alt_customers", "alt_suppliers", "domestic_source", "tech_invest", "fin_tools", "inventory", "hire"]
wide["n_missing_core_items"] = wide[core].isna().sum(axis=1)
pill = ["P1_market_diversification", "P2_supply_reconfiguration", "P3_technology_investment", "P4_financial_buffers"]
# Core index: only items from the tariff-action question, asked identically in Q1-Q3
# (Q1 = actions taken, Q2-Q3 = actions planned). P1 uses the core item (alt. customers) so that
# the "sell more in Canada" item, absent in Q1, does not break comparability.
wide["index_raw"] = wide[["P1_core", "P2_supply_reconfiguration", "P3_technology_investment", "P4_financial_buffers"]].mean(axis=1)
wide.loc[wide.n_missing_core_items >= 3, "index_raw"] = np.nan   # too many suppressed cells
wide["net_score"] = wide.index_raw - wide.D_retrenchment / 3
prov = wide[(wide.breakdown_type == "industry") & (wide.naics == "ALL") & (wide.geo_code != "CA")]
lo, hi = prov.index_raw.min(), prov.index_raw.max()
wide["index_norm"] = 100 * (wide.index_raw - lo) / (hi - lo)
wide["intensity_given_exposure"] = 100 * wide.index_raw / wide.exposure_neg_impact

cols = keys + ["horizon"] + pill + ["P5_digital_readiness", "P1_core", "D_retrenchment", "N_passivity", "exposure_us_sales",
                                    "exposure_neg_impact", "tariffs_imposed", "index_raw", "index_norm",
                                    "net_score", "intensity_given_exposure", "n_missing_core_items"] + \
       [c for c in ITEMS if c in wide] + ["neg_impact"]
out = wide[cols].sort_values(["quarter", "breakdown_type", "geo_code", "naics"])
out.to_csv(OUT / "adaptation_index.csv", index=False)

# Convenience extracts
pr = out[(out.breakdown_type == "industry") & (out.naics == "ALL")]
pr.to_csv(OUT / "adaptation_index_provinces.csv", index=False)
ind = out[(out.breakdown_type == "industry") & (out.geo_code == "CA")]
ind.to_csv(OUT / "adaptation_index_industries_canada.csv", index=False)
print("rows:", len(out))
show = ["geo_code", "quarter", "P1_core", "P2_supply_reconfiguration", "P3_technology_investment", "P4_financial_buffers", "P5_digital_readiness"] + ["D_retrenchment", "N_passivity", "exposure_neg_impact", "index_raw", "index_norm"]
print(pr[show].round(1).to_string(index=False))
print()
print(ind[ind.quarter == "2026Q3"][["naics", "breakdown"] + pill + ["D_retrenchment", "exposure_neg_impact", "index_raw"]].round(1).to_string(index=False))
