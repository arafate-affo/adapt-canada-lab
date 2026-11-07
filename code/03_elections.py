"""
03_elections.py
Parse the Elections Canada official results of the 45th general election (28 April 2025)
into tidy district-level files.

Input : data/raw/elections/table11E.html  (voting results by electoral district)
        data/raw/elections/table12E.html  (candidates and individual results)
Output: data/processed/elections_2025_districts.csv   (one row per electoral district)
        data/processed/elections_2025_candidates.csv  (one row per candidate)
        data/processed/elections_2025_province.csv    (party vote shares by province)

Source: https://www.elections.ca/res/rep/off/ovrGE45/home.html (tables 11 and 12)
"""
from pathlib import Path
import re
import pandas as pd
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "elections"
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

PROV = {
    "Newfoundland and Labrador": "NL", "Prince Edward Island": "PE", "Nova Scotia": "NS",
    "New Brunswick": "NB", "Quebec": "QC", "Ontario": "ON", "Manitoba": "MB",
    "Saskatchewan": "SK", "Alberta": "AB", "British Columbia": "BC", "Yukon": "YT",
    "Northwest Territories": "NT", "Nunavut": "NU",
}
PARTY_MAP = {
    "Liberal": "LIB", "Conservative": "CPC", "NDP-New Democratic Party": "NDP",
    "Bloc Québécois": "BQ", "Green Party": "GRN", "People's Party - PPC": "PPC",
}


def num(s):
    s = s.replace(",", "").replace("\xa0", "").strip()
    return float(s) if re.match(r"^-?\d+(\.\d+)?$", s) else None


def parse_table11():
    soup = BeautifulSoup((RAW / "table11E.html").read_text(encoding="utf-8"), "lxml")
    rows, prov = [], None
    for tr in soup.select("table tbody tr"):
        th = tr.find("th")
        if th is None:
            continue
        if "ProvinceHeading" in th.get("class", []):
            prov = th.get_text(strip=True)
            continue
        tds = tr.find_all("td")
        if len(tds) < 10 or th.get_text(strip=True).lower() in ("totals", "grand total"):
            continue  # skip provincial and national total rows
        elected = tds[9].get_text("|", strip=True).split("|")
        rows.append({
            "province": prov, "prov_code": PROV.get(prov), "district": th.get_text(strip=True),
            "population": num(tds[0].text), "electors": num(tds[1].text), "polls": num(tds[2].text),
            "valid_ballots": num(tds[3].text), "rejected_ballots": num(tds[5].text),
            "total_ballots": num(tds[7].text), "turnout_pct": num(tds[8].text),
            "elected_name": elected[0], "elected_party": elected[-1] if len(elected) > 1 else None,
        })
    return pd.DataFrame(rows)


def parse_table12():
    soup = BeautifulSoup((RAW / "table12E.html").read_text(encoding="utf-8"), "lxml")
    rows, prov, district = [], None, None
    for tr in soup.select("table tbody tr"):
        th = tr.find("th")
        if th is None:
            continue
        if "ProvinceHeading" in th.get("class", []):
            prov = th.get_text(strip=True)
            continue
        name = th.get_text(strip=True)
        if name and name != "\xa0":
            district = name
        tds = tr.find_all("td")
        if len(tds) < 6:
            continue
        cand = tds[0].get_text("|", strip=True).split("|")
        rows.append({
            "province": prov, "prov_code": PROV.get(prov), "district": district,
            "candidate": cand[0], "party": cand[-1] if len(cand) > 1 else None,
            "elected": tds[0].find("strong") is not None,
            "votes": num(tds[3].text), "vote_pct": num(tds[4].text),
            "majority": num(tds[5].text), "majority_pct": num(tds[6].text) if len(tds) > 6 else None,
        })
    return pd.DataFrame(rows)


d11 = parse_table11()
d12 = parse_table12()
d12["party_code"] = d12["party"].map(PARTY_MAP).fillna("OTH")

# Wide party shares by district (main parties), merged on the district table
wide = (d12.pivot_table(index=["prov_code", "district"], columns="party_code", values="vote_pct", aggfunc="sum")
        .reset_index())
districts = d11.merge(wide, on=["prov_code", "district"], how="left")
districts["elected_party_code"] = districts["elected_party"].map(PARTY_MAP).fillna("OTH")
# winning margin in points (first minus second)
top2 = d12.sort_values("vote_pct", ascending=False).groupby(["prov_code", "district"])["vote_pct"].apply(
    lambda s: s.iloc[0] - s.iloc[1] if len(s) > 1 else s.iloc[0]).rename("margin_pts").reset_index()
districts = districts.merge(top2, on=["prov_code", "district"], how="left")

# Province aggregates: vote shares weighted by votes
prov = (d12.groupby(["prov_code", "party_code"])["votes"].sum().unstack(fill_value=0))
prov = prov.div(prov.sum(axis=1), axis=0).mul(100).round(2).reset_index()
seats = districts.groupby(["prov_code", "elected_party_code"]).size().unstack(fill_value=0).add_prefix("seats_").reset_index()
prov = prov.merge(seats, on="prov_code", how="left")
turn = districts.groupby("prov_code").apply(lambda g: 100 * g.total_ballots.sum() / g.electors.sum()).rename("turnout_pct").reset_index()
prov = prov.merge(turn, on="prov_code")

districts.to_csv(OUT / "elections_2025_districts.csv", index=False)
d12.to_csv(OUT / "elections_2025_candidates.csv", index=False)
prov.to_csv(OUT / "elections_2025_province.csv", index=False)
print("districts:", len(districts), "| candidates:", len(d12))
print(districts.elected_party_code.value_counts().to_dict())
print(prov.to_string(index=False))
