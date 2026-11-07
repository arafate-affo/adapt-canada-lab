"""
03b_pollbypoll.py
Stack the 343 poll-by-poll result files of the 45th general election (Elections Canada
"format 1": pollbypoll_bureauparbureau<FED>.csv, one column per candidate) into one long
file: one row per electoral district x polling division x candidate.

Input : data/raw/elections/pollbypoll/*.csv
Output: data/processed/elections_2025_pollbypoll_long.csv.gz
        data/processed/elections_2025_polling_divisions.csv  (one row per polling division:
        electors, total votes, rejected, winner in the division, party shares of the 4 main parties)
Candidate -> party is recovered from the candidates table (elections_2025_candidates.csv).
"""
from pathlib import Path
import re
import unicodedata
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "elections" / "pollbypoll"
P = ROOT / "data" / "processed"


def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z]", "", s.lower())


cand = pd.read_csv(P / "elections_2025_candidates.csv")
codes = pd.read_csv(P / "fed_codes_2025.csv", dtype={"fed_code": str})
cand = cand.merge(codes.assign(key=codes.district.map(norm))[["prov_code", "key", "fed_code"]],
                  left_on=["prov_code", cand.district.map(norm)], right_on=["prov_code", "key"], how="left")
cand["cand_key"] = cand.candidate.map(norm)
party_lookup = {(r.fed_code, r.cand_key): r.party_code for r in cand.itertuples()}
# fallback on the family name (last token) when it is unique within the district
cand["last_key"] = cand.candidate.str.replace(r"\s*\*+\s*$", "", regex=True).str.split().str[-1].map(norm)
uniq = cand.groupby(["fed_code", "last_key"]).party_code.agg(lambda s: s.iloc[0] if len(s) == 1 else None).dropna()
last_lookup = uniq.to_dict()


def party_of(fed, name):
    key = norm(name)
    if (fed, key) in party_lookup:
        return party_lookup[(fed, key)]
    last = norm(str(name).split()[-1]) if str(name).split() else ""
    return last_lookup.get((fed, last), "UNMATCHED")

frames = []
for f in sorted(RAW.glob("pollbypoll_bureauparbureau*.csv")):
    d = pd.read_csv(f, encoding="utf-8-sig", dtype=str)
    fixed = ["Electoral District Number/Numéro de circonscription", "Electoral District Name/Nom de circonscription",
             "Polling Division Number/Numéro de section de vote", "Polling Division Name/Nom de section de vote",
             "Rejected Ballots/Bulletins rejetés", "Total Votes/Total des votes", "Electors/Électeurs"]
    cands = [c for c in d.columns if c not in fixed]
    d = d.rename(columns={fixed[0]: "fed_code", fixed[1]: "district", fixed[2]: "pd_number", fixed[3]: "pd_name",
                          fixed[4]: "rejected", fixed[5]: "total_votes", fixed[6]: "electors"})
    d["no_poll"] = d[cands[0]].astype(str).str.contains("No poll", na=False)
    long = d.melt(id_vars=["fed_code", "district", "pd_number", "pd_name", "rejected", "total_votes", "electors", "no_poll"],
                  value_vars=cands, var_name="candidate", value_name="votes")
    frames.append(long)

pbp = pd.concat(frames, ignore_index=True)
pbp["fed_code"] = pbp.fed_code.str.strip()
pbp["pd_number"] = pbp.pd_number.str.strip()
for c in ["votes", "rejected", "total_votes", "electors"]:
    pbp[c] = pd.to_numeric(pbp[c], errors="coerce")
# candidate names in poll files are "First Last" while table 12 uses "First Last" too, but with
# accents/dashes variants -> normalised key; fall back to OTH when unmatched
pbp["party_code"] = [party_of(f, c) for f, c in zip(pbp.fed_code, pbp.candidate)]
pbp.to_csv(P / "elections_2025_pollbypoll_long.csv.gz", index=False, compression="gzip")

# polling-division summary (excluding merged / no-poll rows)
valid = pbp[~pbp.no_poll & pbp.votes.notna()]
tot = valid.groupby(["fed_code", "pd_number"]).agg(district=("district", "first"), pd_name=("pd_name", "first"),
                                                    electors=("electors", "first"), total_votes=("total_votes", "first"),
                                                    rejected=("rejected", "first")).reset_index()
shares = (valid.groupby(["fed_code", "pd_number", "party_code"]).votes.sum().unstack(fill_value=0))
shares = shares.div(shares.sum(axis=1), axis=0).mul(100).round(2)
shares.columns = [f"share_{c}" for c in shares.columns]
win = valid.sort_values("votes", ascending=False).groupby(["fed_code", "pd_number"]).party_code.first().rename("winner_pd")
pdv = tot.merge(shares, on=["fed_code", "pd_number"]).merge(win, on=["fed_code", "pd_number"])
pdv["turnout_pct"] = (100 * pdv.total_votes / pdv.electors).round(1)
pdv.to_csv(P / "elections_2025_polling_divisions.csv", index=False)
matched = (pbp.party_code != "UNMATCHED").mean()
print("districts:", pbp.fed_code.nunique(), "| polling divisions:", len(pdv), "| candidate rows:", len(pbp),
      f"| share of candidate rows matched to a candidate of table 12: {100 * matched:.1f}%")
print(pdv.winner_pd.value_counts().to_dict())
