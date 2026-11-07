"""
07_programs.py
Federal tariff-response program awards (Proactive Disclosure - Grants and Contributions,
open.canada.ca) linked to federal electoral districts and provinces.

Input : data/raw/programs/grants_tariff_filtered.csv  (rows of the 2.4 GB national file that
        mention tariffs / tariff programs; streamed and filtered with a CSV parser)
        data/processed/elections_2025_districts.csv + fed_codes_2025.csv
Output: data/processed/programs_tariff_awards.csv          (one row per agreement, cleaned)
        data/processed/programs_tariff_by_riding.csv       (awards and $ by riding, with 2025 winner)
        data/processed/programs_tariff_by_province.csv
        output/tables/programs_tariff_by_province.md, programs_by_winner_party.md

The disclosure dataset has a `federal_riding_number` field (5-digit FED code of the 2023
Representation Order), which makes the riding link direct. Only agreements whose program name
or description refers to tariffs are kept (the raw filter also caught French "tarification").
"""
from pathlib import Path
import re
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "programs" / "grants_tariff_filtered.csv"
P = ROOT / "data" / "processed"
TAB = ROOT / "output" / "tables"

d = pd.read_csv(RAW, low_memory=False, dtype={"federal_riding_number": str, "recipient_postal_code": str})
txt = (d.prog_name_en.fillna("") + " | " + d.agreement_title_en.fillna("") + " | " + d.description_en.fillna("")
       + " | " + d.prog_purpose_en.fillna(""))
is_tariff = txt.str.contains(r"tariff", case=False, regex=True)
d = d[is_tariff].copy()
d["agreement_value"] = pd.to_numeric(d.agreement_value, errors="coerce")
d["start"] = pd.to_datetime(d.agreement_start_date, errors="coerce")
d["year"] = d.start.dt.year
d["program"] = d.prog_name_en.str.replace(r"^REGI-[A-Z]+ ?- ?", "", regex=True).str.replace(r"^REGI-", "", regex=True)
d["is_rtri"] = d.program.str.contains("Regional Tariff Response", case=False)
d["fed_code"] = d.federal_riding_number.str.extract(r"(\d{5})")[0]
d["fed_match"] = np.where(d.fed_code.notna(), "disclosed", None)
# fill missing riding codes from the postal-code geocoding cache (code/08_geocode_ridings.py)
cache_f = P / "postal_to_fed_2023.csv"
if cache_f.exists():
    cache = pd.read_csv(cache_f, dtype=str).dropna(subset=["fed_code"]).drop_duplicates("postal_code")
    pc = d.recipient_postal_code.fillna("").str.replace(r"\s+", "", regex=True).str.upper()
    filled = pc.map(cache.set_index("postal_code").fed_code)
    use = d.fed_code.isna() & filled.notna()
    d.loc[use, "fed_code"] = filled[use]
    d.loc[use, "fed_match"] = "postal_centroid"
keep = ["ref_number", "owner_org", "owner_org_title", "program", "is_rtri", "agreement_type", "recipient_legal_name",
        "recipient_city", "recipient_province", "recipient_postal_code", "fed_code", "fed_match", "federal_riding_name_en",
        "agreement_value", "agreement_start_date", "agreement_end_date", "naics_identifier", "description_en"]
awards = d[keep].sort_values("agreement_start_date")
awards.to_csv(P / "programs_tariff_awards.csv", index=False)

# ---- by riding, joined to the 2025 election outcome
import unicodedata


def norm(s):
    """Normalise riding names across sources (accents, dashes, apostrophes, spaces)."""
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", s.lower())


codes = pd.read_csv(P / "fed_codes_2025.csv", dtype={"fed_code": str}).assign(key=lambda x: x.district.map(norm))
ele = pd.read_csv(P / "elections_2025_districts.csv").assign(key=lambda x: x.district.map(norm))
ele = ele.merge(codes[["prov_code", "key", "fed_code"]], on=["prov_code", "key"], how="left").drop(columns="key")
byr = (awards.groupby("fed_code").agg(n_awards=("ref_number", "count"), value_cad=("agreement_value", "sum"),
                                      n_rtri=("is_rtri", "sum")).reset_index())
riding = ele.merge(byr, on="fed_code", how="left").fillna({"n_awards": 0, "value_cad": 0, "n_rtri": 0})
riding["value_per_1000_electors"] = 1000 * riding.value_cad / riding.electors
riding.to_csv(P / "programs_tariff_by_riding.csv", index=False)

# ---- by province and by winning party
byp = (riding.groupby("prov_code").agg(ridings=("district", "count"), n_awards=("n_awards", "sum"),
                                       value_mcad=("value_cad", lambda s: round(s.sum() / 1e6, 2)),
                                       ridings_with_award=("n_awards", lambda s: int((s > 0).sum())))
       .sort_values("value_mcad", ascending=False).reset_index())
byp.to_csv(P / "programs_tariff_by_province.csv", index=False)
(TAB / "programs_tariff_by_province.md").write_text(
    "Tariff-response grants and contributions disclosed on open.canada.ca (agreements mentioning tariffs, "
    "mostly the Regional Tariff Response Initiative), by province of the recipient's riding\n\n"
    + byp.to_markdown(index=False), encoding="utf-8")
byw = (riding.groupby("elected_party_code").agg(ridings=("district", "count"), n_awards=("n_awards", "sum"),
                                                value_mcad=("value_cad", lambda s: round(s.sum() / 1e6, 2)),
                                                share_ridings_with_award=("n_awards", lambda s: round(100 * (s > 0).mean(), 1)),
                                                mean_value_per_1000_electors=("value_per_1000_electors", lambda s: round(s.mean(), 0)))
       .sort_values("value_mcad", ascending=False).reset_index())
(TAB / "programs_by_winner_party.md").write_text(
    "Tariff-response awards by party of the MP elected in April 2025 (descriptive; awards are concentrated "
    "in Quebec and Atlantic RDAs' disclosures, see docs/04_programs.md)\n\n" + byw.to_markdown(index=False), encoding="utf-8")
print("awards kept:", len(awards), "| value M$:", round(awards.agreement_value.sum() / 1e6, 1))
print(awards.program.value_counts().head(8).to_string())
print(awards.owner_org.value_counts().to_string())
print(byp.to_string(index=False))
print(byw.to_string(index=False))
print("ridings unmatched to FED code:", riding.fed_code.isna().sum())
print(awards.fed_match.value_counts(dropna=False).to_dict())
