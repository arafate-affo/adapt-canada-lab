# ADAPT Canada data-lab starter kit (prototype)

**Infrastructure de données et premières analyses pour le Laboratoire sur l'adaptation aux chocs
économiques (Maison des affaires publiques et internationales, Université de Montréal).**
Dépôt préparé par Arafate Affo, novembre 2026, comme démonstration opérationnelle des tâches de
l'offre d'auxiliaire de recherche (science des données). Tout est reproductible à partir de
sources publiques ; rien n'est définitif : l'indice est un prototype à remplacer par la
définition convenue avec l'équipe ADAPT aux États-Unis.

*English follows.*

| Tâche de l'offre | Ce que contient le dépôt |
|---|---|
| Dépôt GitHub et site GitHub Pages | ce dépôt ; `docs/` est un site *just-the-docs* prêt pour Pages, avec un **tableau de bord interactif** (`docs/dashboard.html`) |
| Repérer les données canadiennes correspondant aux données américaines, évaluer disponibilité et qualité, documenter les écarts | `docs/01_data_inventory.md` : crosswalk États-Unis / Canada (entreprises, commerce, tarifs, programmes, élections, IA) avec statut d'accès et écarts |
| Données électorales et politiques reliables aux entreprises et programmes | résultats officiels 2025 par circonscription (343) et **par section de vote (74 317)**, codes de circonscription 2023, parts de vote et marges ; `docs/03_elections.md` |
| Collecter, nettoyer, organiser données entreprises, commerce, tarifs, programmes | 33 tableaux de l'Enquête canadienne sur la situation des entreprises (T2 2025 - T3 2026) ; commerce provincial avec les États-Unis (12-10-0175) ; **750 ententes de programmes de réponse aux tarifs** (divulgation proactive, 2,4 Go filtrés en flux) reliées aux circonscriptions |
| Reproduire les premiers modèles américains avec des données canadiennes | fichiers BTOS du Census Bureau téléchargés ; comparaison **adoption de l'IA par secteur, États-Unis vs Canada** (`output/tables/ai_adoption_us_vs_canada_by_sector.md`) |
| Premières analyses quantitatives et indice | **indice prototype de capacité d'adaptation** par province x trimestre x industrie x taille ; corrélations avec exposition tarifaire, dépendance aux exportations vers les États-Unis et résultats électoraux ; 9 figures |

## Results at a glance (prototype, public tables only)

* **Adaptation effort peaked in Q3 2025 and has eased since.** The core index for Canada
  (mean share of businesses per active-adaptation pillar) went from 9.5 (Q2 2025, actions taken
  in the previous 3 months) to 11.6 (Q3 2025, planned actions) and 7.7 in Q3 2026. Ontario led
  the 2025 peak (14.0); Quebec is consistently lowest (6.3-7.9) despite similar exposure.
* **Supply-chain reconfiguration dominates, market diversification stays rare.** In Q3 2026,
  19.5 % of Canadian businesses plan to find non-US suppliers or source domestically, against
  4.4 % seeking customers outside the US and 2.5 % investing in technology because of tariffs.
  Manufacturing (36 % supply reconfiguration, 16 % new customers) and wholesale trade are the
  most active sectors.
* **Exposure explains part of the provincial pattern.** Across the 10 provinces, the Q3 2026
  index correlates at r = 0.52 (rho = 0.60, p = 0.07) with the share of businesses reporting a
  negative impact of US tariffs; it does not correlate with the 2025 Conservative or Liberal
  vote shares (r between 0.1 and 0.2, n = 10), an ecological non-result to be revisited at riding level.
* **AI adoption gap.** 30 % of US businesses used AI in the previous two weeks (BTOS, 2026
  average) against 19 % of Canadian businesses in the previous 12 months (CSBC Q2 2026); the gap
  is concentrated in wholesale, administrative services, real estate and professional services,
  while Canadian finance and health care report higher use.
* **Trade.** Exports to the US fell in 2025 (Jan-Sep, −3.9 %) and recovered in 2026 (+3.4 %)
  nationally, with large divergences (Newfoundland +29 %, New Brunswick +15 %, Manitoba −8 %).
* **Programs.** Disclosed tariff-response agreements so far total $1.06 B in 750 agreements
  (652 Regional Tariff Response Initiative contributions, plus SRF, REGI and IRAP agreements that
  cite tariffs), concentrated in Ontario ($377 M) and Quebec ($293 M); PrairiesCan and PacifiCan
  have disclosed almost nothing yet, so Western ridings are under-covered until the December 2026
  release. 61 % of the agreements were geocoded to a riding from the recipient's postal code.

Figures are in `output/figures/`, tables in `output/tables/`, all processed data in
`data/processed/` (CSV). The interactive version is `docs/dashboard.html`.

## Important finding on data availability

Statistics Canada has announced that the **Canadian Survey on Business Conditions ends with the
Q3 2026 wave** (released 31 August 2026). It is the only Canadian high-frequency source with
tariff-response and AI questions comparable to the US BTOS. The lab should decide early on a
replacement strategy (Bank of Canada Business Outlook Survey microdata, CFIB, a custom panel);
see `docs/01_data_inventory.md` §7.

## Repository layout

```
code/      00_download.sh, 01_clean_csbc.py ... 09_dashboard.py (run in order; run_all.py)
data/raw/  downloaded inputs (large trade file git-ignored; re-download with 00_download.sh)
data/processed/  tidy CSVs: csbc_long, adaptation_index*, elections_2025_*, trade_*, programs_*
output/    figures (PNG/SVG) and tables (CSV/Markdown)
docs/      GitHub Pages site: inventory, methodology, elections, programs, dashboard
```

## Reproduce

```bash
pip install -r requirements.txt
bash code/00_download.sh        # streams the 2.4 GB grants file without storing it
python code/run_all.py
python code/08_geocode_ridings.py   # optional, Represent API
python code/09_dashboard.py
```

Python 3.12; no Stata or R required (the index logic is 120 lines of pandas and can be ported).

## English summary

A reproducible Canadian data infrastructure for studying how businesses adapt to the 2025-2026
US tariff shock and to AI: 33 CSBC tables (2025 Q2-2026 Q3), provincial trade with the US,
2025 federal election results down to polling divisions, award-level tariff-response programs
linked to ridings, and US BTOS files for cross-country replication. It ships a transparent
prototype adaptation index, a US-Canada AI-adoption comparison, first exploratory correlations
and an interactive dashboard. Methodology and limits: `docs/02_methodology.md`.

## Sources

Statistics Canada (CSBC tables 33-10-0990 to 33-10-1207; table 12-10-0175-01), Elections
Canada (Official Voting Results, 45th general election), Government of Canada (Proactive
Disclosure of Grants and Contributions; Department of Finance, August 2026 tariff package),
US Census Bureau (Business Trends and Outlook Survey), Open North (Represent API).
