---
title: Data inventory and US-Canada crosswalk
nav_order: 2
---

# Data inventory: Canadian counterparts to the US data used by ADAPT

**Purpose.** Map every data family the US ADAPT team is likely to use (firms, trade, tariffs,
government programs, elections and polls, AI adoption) to the closest Canadian source, state
its availability, access conditions, geography and frequency, and flag the gaps that will shape
the Canadian replication. Status codes: **A** = downloaded and processed in this repository,
**B** = public, identified, not yet processed, **C** = restricted access (RDC / licence),
**D** = no Canadian equivalent found yet.

## 1. Business conditions and adaptation behaviour (the core of the index)

| Item | United States | Canada | Status | Notes / gaps |
|---|---|---|---|---|
| High-frequency business survey | **Business Trends and Outlook Survey (BTOS)**, Census Bureau. Biweekly since 2022; national, state, NAICS sector, top-25 MSAs. Flat files: `National.xlsx`, `State.xlsx`, `Sector.xlsx` at `census.gov/hfp/btos/downloads/`. Core questions on performance, revenue, employment, prices, supply delays, **AI use (Q7, Q28)**, generative AI (Q8), extreme weather. AI supplements (Sept. 2023-Feb. 2024; Nov. 2025-Feb. 2026) with 15 business functions. | **Canadian Survey on Business Conditions (CSBC)**, Statistics Canada survey 5318. Quarterly since 2020; Canada, provinces/territories, NAICS sector, employment size, business type, age, majority ownership. Public tables via the Web Data Service (`getFullTableDownloadCSV`). Tariff module since Q2 2025: impact level, actions taken/planned, US tariffs on sales, Canadian tariffs on purchases, pass-through, share of sales to / purchases from the US. AI module: use in last 12 months (Q2), planned use (Q3), changes to staffing. | **A** (18 tables, 2026 Q1-Q3) | Reference windows differ (2 weeks vs 12 months). **StatCan announced that Q3 2026 is the final iteration of the CSBC**: the Canadian high-frequency source ends exactly when the lab starts. Successor sources to monitor: Bank of Canada *Business Outlook Survey* (quarterly, ~100 firms, national), CFIB *Business Barometer* (monthly, members), Chamber of Commerce *Business Data Lab* (uses CSBC microdata). Firm-level CSBC microdata: RDC only. |
| Technology adoption / AI | BTOS AI questions; Annual Business Survey (ABS) technology module; Census *AI supplement*. | CSBC AI tables (33-10-0825, -0878, -1004, -1045, -1167, -1207 for 2024-2026); Survey of Digital Technology and Internet Use (27-10-0375: AI applications by industry and size, 2021/2023, biennial); Survey of Innovation and Business Strategy. | **A** (CSBC 2026) / **B** | Comparison table produced in `output/tables/ai_adoption_us_vs_canada_by_sector.md`. |
| Firm demography and counts | County Business Patterns (county x NAICS x size); Business Dynamics Statistics; Statistics of US Businesses. | **Canadian Business Counts** (semi-annual June/December; census subdivision x NAICS 6-digit x employment-size class; tables 33-10-0xxx, vintage-specific IDs); Business Register (restricted); LEAP / NALMF (RDC). | **B** | Business Counts are at census-subdivision level, which can be aggregated to federal electoral districts with a geographic correspondence (see §5). |
| Firm-level panel for models | LBD / LEHD (Census RDC), Compustat, Orbis, D&B. | Canadian Employer-Employee Dynamics Database (CEEDD), LEAP, NALMF, T2-LEAP, all **RDC** (CRDCN); Orbis/Compustat for listed firms. | **C** | Any firm-level replication of ADAPT models needs an RDC proposal (6-9 months lead time). Public-table replication is feasible at province x sector x size. |

## 2. Trade

| Item | United States | Canada | Status | Notes / gaps |
|---|---|---|---|---|
| Trade by sub-national unit and partner | Census *USA Trade Online* / state exports by origin of movement (state x HS x partner, monthly). | **12-10-0175-01**: international merchandise trade by province, NAPCS commodity group (14) and principal trading partner (29), monthly, customs basis, 1997-Sept. 2026. | **A** | Processed: US share of exports by province, Jan-Sept changes 2025 and 2026. Province of origin = province of production/clearance, not of the firm's head office. |
| Product-level trade (HS) | USITC DataWeb (HTS-10 x partner); Census FT-900. | **Canadian International Merchandise Trade (CIMT) web application**: HS-8 x province x partner, monthly; bulk download. | **B** | Needed to attach tariff lines (Section 232, 338, counter-tariffs) to provincial exposure. |
| Trade by firm characteristics | Census *Profile of US Importing and Exporting Companies* (annual). | **Trade in goods by exporter characteristics** (12-10-0091 to -0104, -0137, -0138): enterprise size x industry x destination x CMA, annual to 2025. | **B** | Allows an exposure measure "share of exporters / export value to the US" by industry x size x CMA, close to the firm level without RDC access. |
| By trade agreement | USITC. | **12-10-0174-01**: imports/exports by free-trade agreement and commodity, monthly. | **B** | CUSMA-covered share; links to the gravity work in Amedji & Affo (2026) on CETA / EU scenarios. |

## 3. Tariffs and trade-policy shocks

| Item | United States | Canada | Status | Notes / gaps |
|---|---|---|---|---|
| Tariff schedules and actions | Federal Register proclamations (IEEPA 2025, Section 232 steel/aluminium/autos/copper/lumber, Section 338 of July 2026); USITC HTS; CBP CSMS messages. | **Department of Finance** counter-tariff lists (HS-8 lines, 25 % from March 2025; 15/25/50 % lists effective 8 Sept. 2026); **CBSA Customs Notices**; Canada Tariff Finder; Global Affairs *Canada-US trade* page. | **B** | Build a product-level event calendar (date x HS x rate x legal basis) for both directions; this is the "tariff" input of the index. |
| Effective tariff rates | USITC/USAFacts collected-duty ratios; Penn Wharton CUSMA-compliance shares. | CBSA duty collections (monthly, Public Accounts); StatCan *import duties* in 12-10-0011 (customs basis). | **B** | Statutory vs effective rates diverge sharply because of CUSMA preferences (compliance about 84 % in mid-2026). |
| Business-reported tariff exposure | BTOS has no tariff question as of 2026 (verified in the question list). | CSBC: US tariffs imposed on goods sold (33-10-1111/1150/1190), Canadian tariffs on purchases, impact level, pass-through, share of sales to the US. | **A** | Canada has **richer** survey-based tariff exposure than the US; this is an asset for the Canadian side of ADAPT. |

## 4. Government programs

| Item | United States | Canada | Status | Notes / gaps |
|---|---|---|---|---|
| Award-level program data | USAspending.gov (awards with recipient, county, NAICS, CFDA program). | **Proactive Disclosure - Grants and Contributions** (open.canada.ca, 2.4 GB CSV, one row per agreement: department, program, recipient, city, province, postal code, value, dates). Filtered extract of tariff-related agreements in `data/raw/programs/`. | **A** (filtered) | Covers RDAs' *Regional Tariff Response Initiative*, *Strategic Response Fund* streams; **does not cover** BDC and EDC loans (Crown corporations, no award-level disclosure) nor EI Work-Sharing (ESDC aggregate statistics only). |
| Program inventory | n/a | Finance Canada package of Aug. 2026 ($7.5 B): RTRI +$1.5 B (RDAs), BDC *Pivot to Grow* liquidity stream $500 M, *Canada Strong Diversification Fund* $2 B (SRF), LETL facility $10 B (CEEFC), *Workforce Retention and Retraining Program* (replaces Work-Sharing + Worker Retention Grant), EI measures. See `docs/04_programs.md`. | **A** (documented) | Provincial programs (e.g., Québec's *Frontière* / Investissement Québec, Ontario's *Protecting Ontario Account*) to add. |

## 5. Elections, political geography and polls

| Item | United States | Canada | Status | Notes / gaps |
|---|---|---|---|---|
| Election results | MIT Election Data + Science Lab (county/precinct); Daily Kos district results. | **Elections Canada official voting results, 45th general election (28 April 2025)**: results by electoral district (table 11), candidates (table 12), and **poll-by-poll CSV files** (one file per district). 2021 and 2019 results available in the same format. | **A** (district level) / **B** (poll level) | Processed: 343 districts, 1,959 candidates, party shares, margins, turnout; province aggregates. |
| Political geography | Congressional districts shapefiles; county-district crosswalks. | **Federal Electoral Districts 2023 Representation Order** boundary files (Elections Canada open data / StatCan); 2021 Census profiles by 2023 FED. | **B** | Needed to aggregate Business Counts (census subdivisions) and postal-code-level program awards to ridings. The *Postal Codes by Federal Ridings File* was discontinued in 2017; use the PCCF (licensed via the university DLI) or the Elections Canada polling-division geographies. |
| Polls and surveys | ANES, CES (Cooperative Election Study), state polls. | **Canadian Election Study 2025** (web + phone, Borealis/Dataverse), Angus Reid, Abacus, Léger, Nanos; 338Canada aggregates. CES includes riding identifiers in restricted versions. | **B** | Questions on trade, tariffs and attitudes toward the US are present in the 2025 CES. |

## 6. Macro and labour-market context

| Item | Canada source | Status |
|---|---|---|
| Employment by industry and province | Labour Force Survey (14-10-0023), SEPH (14-10-0201) | **B** |
| EI claims and Work-Sharing | ESDC monthly EI statistics (14-10-0005), Work-Sharing agreements (ESDC open data) | **B** |
| Business insolvencies | OSB monthly insolvency statistics by province and NAICS | **B** |
| Investment intentions | Capital and repair expenditure survey (34-10-0035) | **B** |

## 7. Gaps that matter most

1. **End of the CSBC after Q3 2026.** The lab's main Canadian adaptation signal stops; a plan B
   (Bank of Canada BOS microdata request, CFIB partnership, or a custom panel) is needed early.
2. **No public firm-level data.** US models estimated on firm microdata can only be replicated at
   province x industry x size on public tables; a CRDCN proposal is the path to firm-level work.
3. **Riding-level linkage.** Business and program data are not published by electoral district;
   a geographic correspondence (census subdivision or postal code to FED 2023) must be built.
4. **BDC/EDC lending** is invisible in award-level disclosure; aggregate program reports only.
5. **Concept drift across quarters.** CSBC tariff questions alternate between actions *taken* and
   actions *planned*, and the AI question changes wording; the index keeps the items that are
   comparable and reports the others separately.
