"""
01_clean_csbc.py
Stack the Canadian Survey on Business Conditions (CSBC) tables downloaded from the
Statistics Canada Web Data Service into one tidy long file.

Input : data/raw/csbc/<productId>.csv (StatCan "full table" CSV format)
Output: data/processed/csbc_long.csv
        data/processed/csbc_tables_inventory.csv

Each StatCan table has one survey question; the question text is the name of the
5th column. We standardise column names, tag the quarter (Q1, Q2, Q3 2026) and the
type of breakdown (industry, employment size, business type, age, ownership...).
"""
from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "csbc"
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

# Table id -> (quarter of 2026, short question label)
TABLES = {
    # 2025 (tariff module introduced in Q2 2025)
    "33100990": ("2025Q2", "us_sales_share"),
    "33100992": ("2025Q2", "tariff_impact_level"),      # high/medium/low scale (changes in Q3 2025)
    "33100993": ("2025Q2", "tariff_actions_taken"),     # last 3 months, "to mitigate risks"
    "33101004": ("2025Q2", "ai_use_last12m"),
    "33101026": ("2025Q3", "us_sales_share"),
    "33101028": ("2025Q3", "tariff_impact_level"),
    "33101029": ("2025Q3", "tariff_actions_planned"),
    "33101031": ("2025Q3", "us_tariffs_on_sales"),      # last 3 months
    "33101036": ("2025Q3", "tariff_cost_passthrough"),  # last 6 months
    "33101045": ("2025Q3", "ai_use_next12m"),
    "33101067": ("2025Q4", "us_sales_share"),
    "33101069": ("2025Q4", "tariff_impact_level"),
    "33101070": ("2025Q4", "tariff_actions_planned"),
    "33101071": ("2025Q4", "us_tariffs_on_sales"),      # last 3 months
    "33101080": ("2025Q4", "changed_suppliers"),        # last 3 months
    # 2026
    "33101107": ("2026Q1", "us_sales_share"),
    "33101109": ("2026Q1", "tariff_impact_level"),
    "33101110": ("2026Q1", "tariff_actions_taken"),
    "33101111": ("2026Q1", "us_tariffs_on_sales"),
    "33101113": ("2026Q1", "tariff_cost_passthrough"),
    "33101129": ("2026Q1", "tech_adoption_training"),
    "33101146": ("2026Q2", "us_sales_share"),
    "33101148": ("2026Q2", "tariff_impact_level"),
    "33101149": ("2026Q2", "tariff_actions_planned"),
    "33101150": ("2026Q2", "us_tariffs_on_sales"),
    "33101152": ("2026Q2", "tariff_cost_passthrough"),
    "33101167": ("2026Q2", "ai_use_last12m"),
    "33101186": ("2026Q3", "us_sales_share"),
    "33101188": ("2026Q3", "tariff_impact_level"),
    "33101189": ("2026Q3", "tariff_actions_planned"),
    "33101190": ("2026Q3", "us_tariffs_on_sales"),
    "33101192": ("2026Q3", "tariff_cost_passthrough"),
    "33101207": ("2026Q3", "ai_use_next12m"),
}

PROVINCE_CODES = {
    "Canada": "CA", "Newfoundland and Labrador": "NL", "Prince Edward Island": "PE",
    "Nova Scotia": "NS", "New Brunswick": "NB", "Quebec": "QC", "Ontario": "ON",
    "Manitoba": "MB", "Saskatchewan": "SK", "Alberta": "AB", "British Columbia": "BC",
    "Yukon": "YT", "Northwest Territories": "NT", "Nunavut": "NU",
}


def breakdown_type(bc: str) -> str:
    """Classify the 'Business characteristics' dimension."""
    if bc.startswith("North American Industry") or re.search(r"\[\d{2}(-\d{2})?\]$", bc):
        return "industry"
    if "employment size" in bc or re.match(r"^\d+ (to \d+|or more) employees$", bc):
        return "size"
    if bc.startswith("Business or organization type") or bc in (
        "Government agencies", "Private sector businesses", "Non-profit organizations",
        "Non-profit organizations serving households or individuals",
        "Non-profit organizations serving businesses"):
        return "type"
    if bc.startswith("Age of business") or bc.startswith("More than"):
        return "age"
    if "owned" in bc or "ownership" in bc.lower() or "majority" in bc.lower():
        return "ownership"
    return "other"


def naics_code(bc: str) -> str:
    m = re.search(r"\[(\d{2}(?:-\d{2})?)\]$", bc)
    if m:
        return m.group(1)
    return "ALL" if bc.startswith("North American Industry") else ""


frames, inventory = [], []
for pid, (quarter, label) in TABLES.items():
    f = RAW / f"{pid}.csv"
    d = pd.read_csv(f, low_memory=False)
    qcol = d.columns[4]  # the question is the 5th column of the StatCan file
    d[qcol] = d[qcol].str.strip()  # some categories carry trailing spaces across vintages
    d = d.rename(columns={qcol: "category", "Business characteristics": "breakdown",
                          "GEO": "geo", "VALUE": "value", "STATUS": "status", "REF_DATE": "ref_date"})
    # Tables with two question dimensions (e.g. impact level x type of barrier)
    extra = [c for c in d.columns[5:] if c not in ("UOM", "UOM_ID", "SCALAR_FACTOR", "SCALAR_ID", "VECTOR",
                                                    "COORDINATE", "value", "status", "SYMBOL", "TERMINATED", "DECIMALS")]
    d["category2"] = d[extra[0]].str.strip() if extra else ""
    d["table_id"] = pid
    d["quarter"] = quarter
    d["question"] = label
    d["question_text"] = qcol.strip()
    d["geo_code"] = d["geo"].map(PROVINCE_CODES)
    d["breakdown_type"] = d["breakdown"].map(breakdown_type)
    d["naics"] = d["breakdown"].map(naics_code)
    keep = ["table_id", "quarter", "question", "question_text", "ref_date", "geo", "geo_code",
            "breakdown", "breakdown_type", "naics", "category", "category2", "value", "status", "UOM"]
    frames.append(d[keep])
    inventory.append({"table_id": pid, "quarter": quarter, "question": label, "question_text": qcol.strip(),
                      "n_rows": len(d), "n_categories": d["category"].nunique(),
                      "share_suppressed": round(d["value"].isna().mean(), 3)})

long = pd.concat(frames, ignore_index=True)
long.to_csv(OUT / "csbc_long.csv", index=False)
pd.DataFrame(inventory).to_csv(OUT / "csbc_tables_inventory.csv", index=False)
print(long.shape)
print(pd.DataFrame(inventory).to_string(index=False))
print(long.breakdown_type.value_counts())
