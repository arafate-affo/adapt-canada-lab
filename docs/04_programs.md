---
title: Government programs
nav_order: 5
---

# Federal tariff-response programs: inventory and award-level data

## 1. Program inventory (status as of early November 2026)

Source: Department of Finance Canada, *Support for Canadian workers and businesses affected by
U.S. tariffs* (August 2026 package, $7.5 B), and earlier announcements (March 2025, May 2026).

| Program | Delivered by | Envelope | Target | Award-level data? |
|---|---|---|---|---|
| Regional Tariff Response Initiative (RTRI) | 7 Regional Development Agencies (CED-Quebec, ACOA, FedDev, FedNor, PrairiesCan, PacifiCan, CanNor) | launched 2025; +$500 M (May 2026); +$1.5 B from Sept. 2026 | SMEs facing tariff pressure (diversification, productivity, working capital) | **Yes**: proactive disclosure of grants and contributions (recipient, city, postal code, value, dates; riding number for some RDAs) |
| Canada Strong Diversification Fund (new stream of the Strategic Response Fund) | SRF, intake by RDAs | $2 B | Tariff-affected firms with shovel-ready capital/maintenance projects, incl. medium-sized | Yes (SRF contributions are disclosed) |
| BDC *Pivot to Grow* liquidity stream; steel, aluminium, forestry programs; eligibility lowered to $1 M revenue | Business Development Bank of Canada | $500 M (liquidity stream); $1 B (steel/aluminium/copper, May 2026) | SMEs; loans $250 K-$5 M, interest-only 36 months | **No** (Crown corporation lending; aggregate reporting only) |
| Large Enterprise Tariff Loan (LETL) facility | Canada Enterprise Emergency Funding Corporation | $10 B | Large enterprises | Partial (facility-level disclosure) |
| Workforce Retention and Retraining Program (replaces EI Work-Sharing special measures and the Worker Retention Grant) | ESDC | part of $3.5 B worker/employer suite; up to $1,000 per participant | Employers retaining workers | Aggregate only (ESDC EI statistics) |
| EI measures: waiting-period waiver, separation payments, +20 weeks for long-tenured workers, voluntary leavers | ESDC / Service Canada | part of $3.5 B | Workers | Aggregate (14-10-0005 and EI monitoring) |
| Export Development Canada *Trade Impact Program* | EDC | $5 B (March 2025) | Exporters | No |
| Counter-tariff remission framework | Finance / CBSA | n/a | Importers of tariffed US goods | Remission orders published in the Canada Gazette |

Provincial measures (Québec *Frontière* loans and Investissement Québec; Ontario *Protecting
Ontario Account* and *Ontario Together Trade Fund*; others) are to be added in the next pass.

## 2. Award-level extract built in this repository

`data/raw/programs/grants_tariff_filtered.csv` keeps the rows of the national proactive-
disclosure file (2.4 GB, ~1 M agreements) that mention tariffs or a tariff program; the
2.4 GB file is streamed and parsed with a CSV reader (multi-line quoted fields), not stored.
`code/07_programs.py` then keeps agreements whose program name, title, description or purpose
contains "tariff" (dropping French "tarification" hits from the Museums Assistance Program).

Result: **750 agreements, $1.06 B**, of which 652 are RTRI contributions (CED-Quebec 305,
FedDev Ontario 209, ACOA 146, FedNor 47), 7 are Strategic Response Fund "tariff-affected sector
support" contributions, 54 are REGI contributions whose description cites tariffs and 12 are
IRAP (NRC) contributions. Disclosure lags: PrairiesCan (3) and PacifiCan (1) RTRI awards have
barely appeared (disclosure is quarterly, with a one-quarter lag), so the extract is a lower bound
and under-covers the Western provinces for now. By province of the recipient's riding: Ontario
$377 M, Quebec $293 M, New Brunswick $26 M, Nova Scotia $24 M, Newfoundland $14 M, PEI $12 M,
Alberta $4 M, British Columbia $1 M, Saskatchewan $0.

## 3. Linking awards to ridings

* FedNor, FedDev, CanNor and ESDC populate `federal_riding_number` (2023 Representation Order).
* CED-Quebec, ACOA and AAFC do not; `code/08_geocode_ridings.py` resolves their recipients'
  postal codes to a 2023 riding with the open Represent API (postal-code centroid, so rural
  codes spanning two ridings are approximate). The official alternative is the licensed
  Postal Code Conversion File (PCCF) available through the university's DLI subscription.
* Result: 286 agreements carry a disclosed riding number, 461 were geocoded from the postal code,
  3 have no usable postal code. 211 of the 343 ridings have at least one award.
* Output: `data/processed/programs_tariff_by_riding.csv` (awards, dollars, dollars per 1,000
  electors, joined to the 2025 winner, margin and turnout of the riding) and
  `programs_tariff_by_province.csv`. A first descriptive cut by party of the elected MP is in
  `output/tables/programs_by_winner_party.md` (Liberal-held ridings: 63 % with an award; Conservative:
  45 %; Bloc: 95 %, reflecting CED-Quebec's early disclosure rather than any allocation effect).

## 4. Next steps

1. Re-run the extraction after each quarterly disclosure update (next: late December 2026).
2. Add the SRF / Canada Strong Diversification Fund stream once agreements are disclosed.
3. Request aggregate BDC and EDC program statistics by province and sector (not disclosed at
   award level) through the lab's partners.
4. Build the US counterpart from USAspending.gov (CFDA programs for trade adjustment and
   manufacturing support) with county to congressional district crosswalks.
