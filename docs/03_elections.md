---
title: Electoral and political data
nav_order: 4
---

# Electoral and political data prepared for linkage

## 45th general election (28 April 2025), official results

Source: Elections Canada, *Official Voting Results* (tables 11 and 12, and the raw poll-by-poll
CSV files, format 1). Downloaded on 7 November 2026.

| File | Unit | Rows | Content |
|---|---|---|---|
| `elections_2025_districts.csv` | electoral district | 343 | population, electors, polls, valid/rejected/total ballots, turnout, elected candidate and party, vote share of LIB / CPC / NDP / BQ / GRN / PPC / other, winning margin in points |
| `elections_2025_candidates.csv` | candidate | 1,959 | party, residence, occupation, votes, share, majority |
| `elections_2025_province.csv` | province | 13 | vote shares, seats by party, turnout |
| `fed_codes_2025.csv` | district | 343 | 5-digit FED code (2023 Representation Order), district name, province |
| `elections_2025_polling_divisions.csv` | polling division | 74,317 | electors, total votes, rejected, party shares and winner in the division, turnout |
| `elections_2025_pollbypoll_long.csv.gz` | division x candidate | 476,685 | votes by candidate, with party code |

Checks: 343 districts and 1,959 candidates match the Elections Canada totals; seat counts
(LIB 169, CPC 144, BQ 22, NDP 7, GRN 1) match the official result.

## Why polling divisions matter

Polling divisions (~75,000, a few hundred electors each) are the finest public electoral
geography in Canada. Elections Canada publishes their boundaries (shapefiles, 2023
Representation Order), which allows aggregation of firm or program locations to any
intermediate geography (census subdivision, census tract) and a direct spatial join with
Business Counts and program awards.

## Previous elections

2021 (44th) and 2019 (43rd) results exist in the same formats on the Elections Canada site,
but on the 2013 Representation Order boundaries. Elections Canada's *transposition of votes*
report gives 2021 results re-computed on the 2023 boundaries, which is the right baseline for
swing measures in 2025.

## Polls and surveys

* **Canadian Election Study 2025** (web and phone): questions on trade, tariffs, attitudes
  toward the United States and economic anxiety; riding identifiers in the restricted file.
  Access via Borealis / Harvard Dataverse.
* Commercial polls with provincial cross-tabs: Abacus, Léger, Angus Reid, Nanos; weekly
  aggregates by 338Canada.
* Statistics Canada *Canadian Social Survey* has a quarterly module on economic concerns.

## Next steps

1. Download the 2023-order polling-division and FED shapefiles and build the FED to census
   subdivision correspondence (area weights).
2. Add the transposed 2021 results to compute 2021-2025 swings by riding.
3. Build a riding-level dataset: swing, margin, turnout, tariff-program awards per 1,000
   electors, Business Counts by sector, export exposure of the local industry mix.
