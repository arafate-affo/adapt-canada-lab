"""
05_analysis.py
First exploratory analyses linking the prototype adaptation index to (i) tariff exposure,
(ii) provincial trade dependence on the United States and (iii) the 2025 federal election
results. Produces figures (PNG + SVG) and tables (CSV + Markdown).

Caveats printed with the results: 10 provinces (territories excluded: small samples,
heavy suppression), ecological correlations, survey shares not firm-level data.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "data" / "processed"
FIG = ROOT / "output" / "figures"; FIG.mkdir(parents=True, exist_ok=True)
TAB = ROOT / "output" / "tables"; TAB.mkdir(parents=True, exist_ok=True)

# Palette (validated categorical slots) and neutral inks
C = {"blue": "#2a78d6", "orange": "#eb6834", "aqua": "#1baf7a", "yellow": "#eda100",
     "text": "#0b0b0b", "text2": "#52514e", "grid": "#e6e5e1", "surface": "#fcfcfb"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": C["text2"],
                     "axes.labelcolor": C["text2"], "xtick.color": C["text2"], "ytick.color": C["text2"],
                     "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": C["surface"],
                     "axes.facecolor": C["surface"], "axes.grid": True, "grid.color": C["grid"],
                     "grid.linewidth": 0.6, "axes.axisbelow": True, "legend.frameon": False})


def save(fig, name):
    fig.tight_layout()
    fig.savefig(FIG / f"{name}.png", dpi=160)
    fig.savefig(FIG / f"{name}.svg")
    plt.close(fig)


NAME = {"NL": "Newfoundland and Labrador", "PE": "Prince Edward Island", "NS": "Nova Scotia",
        "NB": "New Brunswick", "QC": "Quebec", "ON": "Ontario", "MB": "Manitoba",
        "SK": "Saskatchewan", "AB": "Alberta", "BC": "British Columbia"}
CODE = {v: k for k, v in NAME.items()}
PROVS = list(NAME)

idx = pd.read_csv(P / "adaptation_index_provinces.csv")
ele = pd.read_csv(P / "elections_2025_province.csv").rename(columns={"prov_code": "geo_code"})
trd = pd.read_csv(P / "trade_province_exposure.csv")
trd = (trd[trd.napcs == "Total of all merchandise"]
       .assign(geo_code=lambda d: d.geo.map(CODE)).dropna(subset=["geo_code"]))

# ---------- merged provincial dataset (Q3 2026 index) ----------
q3 = idx[(idx.quarter == "2026Q3") & idx.geo_code.isin(PROVS)]
m = q3.merge(ele, on="geo_code").merge(trd.drop(columns=["geo", "napcs"]), on="geo_code")
seat_cols = [c for c in m if c.startswith("seats_")]
m["seat_share_CPC"] = 100 * m.seats_CPC / m[seat_cols].sum(axis=1)
m.to_csv(TAB / "merged_province_dataset_2026Q3.csv", index=False)

# ---------- correlation table ----------
VARS = [("exposure_neg_impact", "Share of businesses reporting a negative impact of US tariffs (Q3 2026)"),
        ("exposure_us_sales", "Share of businesses with direct sales to the US (Q3 2026)"),
        ("us_share_exports_2024", "US share of provincial merchandise exports, 2024"),
        ("chg_us_exports_ytd_2026_vs_2025_pct", "Change in exports to the US, Jan-Sep 2026 vs 2025 (%)"),
        ("chg_us_exports_ytd_2025_vs_2024_pct", "Change in exports to the US, Jan-Sep 2025 vs 2024 (%)"),
        ("CPC", "Conservative vote share, 2025 federal election (%)"),
        ("LIB", "Liberal vote share, 2025 federal election (%)"),
        ("turnout_pct", "Voter turnout, 2025 (%)")]
rows = []
for var, label in VARS:
    x, y = m[var], m.index_raw
    ok = x.notna() & y.notna()
    r, pr = stats.pearsonr(x[ok], y[ok])
    rho, ps = stats.spearmanr(x[ok], y[ok])
    rows.append({"variable": label, "n": int(ok.sum()), "pearson_r": round(r, 2), "p_pearson": round(pr, 3),
                 "spearman_rho": round(rho, 2), "p_spearman": round(ps, 3)})
corr = pd.DataFrame(rows)
corr.to_csv(TAB / "correlations_provinces_2026Q3.csv", index=False)
(TAB / "correlations_provinces_2026Q3.md").write_text(
    "Correlation of the core adaptation index (Q3 2026) with exposure, trade and electoral "
    "variables, 10 provinces (ecological correlations; territories excluded)\n\n"
    + corr.to_markdown(index=False), encoding="utf-8")
print(corr.to_string(index=False))

# ---------- Figure 1: index by province, latest quarter with the range over 2025Q2-2026Q3 ----------
piv = (idx[idx.geo_code.isin(PROVS)]
       .pivot(index="geo_code", columns="quarter", values="index_raw").loc[PROVS])
order = piv["2026Q3"].sort_values(ascending=True).index
fig, ax = plt.subplots(figsize=(8, 5.2))
yv = np.arange(len(order))
ax.hlines(yv, piv.loc[order].min(axis=1), piv.loc[order].max(axis=1), color=C["grid"], linewidth=6, zorder=1,
          label="Range over the six quarters (Q2 2025 - Q3 2026)")
ax.scatter(piv.loc[order, "2025Q3"], yv, s=55, color=C["orange"], zorder=3, label="Q3 2025 (first quarter of planned actions)")
ax.scatter(piv.loc[order, "2026Q3"], yv, s=70, color=C["blue"], zorder=4, label="Q3 2026 (latest quarter)")
ax.set_yticks(yv); ax.set_yticklabels([NAME[c] for c in order])
ax.set_xlabel("Core adaptation index (mean % of businesses per pillar)")
ax.set_title("Prototype business adaptation index by province, CSBC 2025-2026", loc="left", color=C["text"])
ax.legend(loc="lower right", fontsize=8)
save(fig, "fig1_index_by_province_quarter")

# ---------- Figure 1b: national series, Canada and the four largest provinces ----------
fig, ax = plt.subplots(figsize=(7.2, 4.4))
qs = list(piv.columns)
for code, colr, lab in [("CA", C["text2"], "Canada"), ("ON", C["blue"], "Ontario"), ("QC", C["orange"], "Quebec"),
                        ("AB", C["aqua"], "Alberta"), ("BC", C["yellow"], "British Columbia")]:
    ser = idx[idx.geo_code == code].set_index("quarter").index_raw.reindex(qs)
    ax.plot(qs, ser, marker="o", markersize=5, linewidth=2 if code == "CA" else 1.6, color=colr, label=lab,
            linestyle="-" if code == "CA" else "-")
ax.axvspan(-0.5, 0.5, color=C["grid"], alpha=0.5, lw=0)
ax.text(0, ax.get_ylim()[1] * 0.98, " actions taken\n (3 months)", fontsize=7.5, color=C["text2"], va="top")
ax.axvspan(2.5, 3.5, color=C["grid"], alpha=0.5, lw=0)
ax.text(3, ax.get_ylim()[1] * 0.98, " actions taken\n (12 months)", fontsize=7.5, color=C["text2"], va="top", ha="center")
ax.set_ylabel("Core adaptation index"); ax.set_ylim(0)
ax.set_title("Adaptation index over the tariff episode, Q2 2025 - Q3 2026", loc="left", color=C["text"])
ax.legend(fontsize=8, ncol=3, loc="lower center")
save(fig, "fig1b_index_series_canada_provinces")

# ---------- scatter helper ----------
def scatter(x, y, labels, xlabel, ylabel, title, name, color=C["blue"]):
    fig, ax = plt.subplots(figsize=(6.4, 4.8))
    ax.scatter(x, y, s=55, color=color, edgecolor=C["surface"], linewidth=1.5, zorder=3)
    for xi, yi, lab in zip(x, y, labels):
        ax.annotate(lab, (xi, yi), xytext=(5, 4), textcoords="offset points", fontsize=9, color=C["text"])
    ok = x.notna() & y.notna()
    b, a = np.polyfit(x[ok], y[ok], 1)
    xs = np.linspace(x[ok].min(), x[ok].max(), 10)
    ax.plot(xs, a + b * xs, color=C["text2"], linewidth=1, linestyle="--", zorder=2)
    r, p = stats.pearsonr(x[ok], y[ok])
    ax.text(0.02, 0.96, f"Pearson r = {r:.2f} (p = {p:.2f}), n = {int(ok.sum())}",
            transform=ax.transAxes, va="top", fontsize=9, color=C["text2"])
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel); ax.set_title(title, loc="left", color=C["text"])
    save(fig, name)


scatter(m.exposure_neg_impact, m.index_raw, m.geo_code,
        "Businesses reporting a negative impact of US tariffs (%)", "Core adaptation index (Q3 2026)",
        "Adaptation index and reported tariff exposure", "fig2_index_vs_tariff_exposure")
scatter(m.us_share_exports_2024, m.index_raw, m.geo_code,
        "US share of provincial merchandise exports, 2024 (%)", "Core adaptation index (Q3 2026)",
        "Adaptation index and export dependence on the US", "fig3_index_vs_us_export_share", color=C["orange"])
scatter(m.CPC, m.index_raw, m.geo_code,
        "Conservative vote share, April 2025 federal election (%)", "Core adaptation index (Q3 2026)",
        "Adaptation index and 2025 election results (ecological, n = 10)",
        "fig4_index_vs_cpc_vote", color=C["aqua"])

# ---------- Figure 5: industry pillars, Canada Q3 2026 ----------
ind = pd.read_csv(P / "adaptation_index_industries_canada.csv")
i3 = ind[(ind.quarter == "2026Q3") & (ind.naics != "ALL")].copy()
i3["label"] = (i3.breakdown.str.replace(r" \[.*\]$", "", regex=True)
               .str.replace("Mining, quarrying, and oil and gas extraction", "Mining, oil and gas")
               .str.replace("Administrative and support, waste management and remediation services",
                            "Administrative and support services"))
i3 = i3.sort_values("index_raw")
fig, ax = plt.subplots(figsize=(9.5, 6))
left = np.zeros(len(i3))
stack = [("P1_core", C["blue"], "Alternative customers outside the US"),
         ("P2_supply_reconfiguration", C["orange"], "Alternative suppliers / domestic sourcing"),
         ("P3_technology_investment", C["aqua"], "Technology investment"),
         ("P4_financial_buffers", C["yellow"], "Financial tools, inventory, hiring")]
for col, colr, lab in stack:
    vals = i3[col].fillna(0).values
    ax.barh(i3.label, vals, left=left, color=colr, label=lab, height=0.7, edgecolor=C["surface"], linewidth=1)
    left += vals
ax.set_xlabel("Sum of pillar shares (% of businesses planning each action, next 12 months)")
ax.set_title("Planned responses to US tariffs by industry, Canada, Q3 2026", loc="left", color=C["text"])
ax.legend(loc="lower right", fontsize=8)
save(fig, "fig5_industry_pillars_2026Q3")

# ---------- Figure 6: exports to the US by province, change 2026 YTD ----------
t = trd.set_index("geo_code").loc[PROVS].sort_values("chg_us_exports_ytd_2026_vs_2025_pct")
fig, ax = plt.subplots(figsize=(7.5, 4.6))
vals = t.chg_us_exports_ytd_2026_vs_2025_pct
ax.barh([NAME[c] for c in t.index], vals, color=[C["blue"] if v >= 0 else C["orange"] for v in vals], height=0.65)
ax.axvline(0, color=C["text2"], linewidth=0.8)
ax.set_xlabel("Domestic exports to the United States, Jan-Sep 2026 vs Jan-Sep 2025 (%)")
ax.set_title("Provincial exports to the US during the 2025-2026 tariff episode", loc="left", color=C["text"])
save(fig, "fig6_exports_to_us_change_2026ytd")

# ---------- Figure 7: national trend of selected items ----------
ca = idx[idx.geo_code == "CA"].set_index("quarter")
fig, ax = plt.subplots(figsize=(7, 4.4))
lines = [("alt_customers", C["blue"], "Alternative customers outside the US"),
         ("domestic_source", C["orange"], "Increase domestic sourcing"),
         ("tech_invest", C["aqua"], "Invest in technology"),
         ("delay_invest", C["yellow"], "Delay investment / expansion")]
for col, colr, lab in lines:
    ax.plot(ca.index, ca[col], marker="o", markersize=6, linewidth=2, color=colr, label=lab)
ax.set_ylabel("% of businesses"); ax.set_ylim(0)
ax.set_title("Canada: tariff responses, Q1 (taken) vs Q2-Q3 (planned), 2026", loc="left", color=C["text"])
ax.legend(fontsize=8)
save(fig, "fig7_canada_items_by_quarter")

# ---------- tables ----------
cols = ["geo_code", "P1_core", "P2_supply_reconfiguration", "P3_technology_investment", "P4_financial_buffers",
        "P5_digital_readiness", "D_retrenchment", "N_passivity", "exposure_neg_impact", "exposure_us_sales",
        "index_raw", "index_norm"]
tq3 = q3[cols].sort_values("index_raw", ascending=False).round(1)
tq3.to_csv(TAB / "index_provinces_2026Q3.csv", index=False)
(TAB / "index_provinces_2026Q3.md").write_text(tq3.to_markdown(index=False), encoding="utf-8")
ti = i3.sort_values("index_raw", ascending=False)[
    ["naics", "label", "P1_core", "P2_supply_reconfiguration", "P3_technology_investment",
     "P4_financial_buffers", "P5_digital_readiness", "D_retrenchment", "exposure_neg_impact", "index_raw"]].round(1)
ti.to_csv(TAB / "index_industries_2026Q3.csv", index=False)
(TAB / "index_industries_2026Q3.md").write_text(ti.to_markdown(index=False), encoding="utf-8")
print("figures:", sorted(p.name for p in FIG.glob("*.png")))
