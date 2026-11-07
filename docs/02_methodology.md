---
title: Index methodology (prototype)
nav_order: 3
---

# Prototype Business Adaptive Capacity Index (BACI-CA)

This is a **transparent, replaceable prototype** built only from public Statistics Canada
tables, so that the weighting and the item list can be changed in one place once the
ADAPT team's US definition is known. Every input share is kept in the output file
(`data/processed/adaptation_index.csv`) for re-weighting.

## Unit of observation

Geography (Canada, 10 provinces, 3 territories) x quarter (2025 Q2 to 2026 Q3, six waves)
 x  breakdown (all industries; 16 NAICS sectors; 4 employment-size classes; business type; age;
majority ownership). Province x industry cells exist but are often suppressed by Statistics
Canada for small provinces.

## Source questions (Canadian Survey on Business Conditions)

| Wave | Tariff-action question | Horizon | Impact scale |
|---|---|---|---|
| 2025 Q2 | Actions **taken** to mitigate tariff risks | past 3 months | high / medium / low |
| 2025 Q3 | Actions **planned** | next 12 months | major / minor negative … |
| 2025 Q4 | Actions **planned** | next 12 months | idem |
| 2026 Q1 | Actions **taken** | past 12 months | idem |
| 2026 Q2 | Actions **planned** | next 12 months | idem (expected) |
| 2026 Q3 | Actions **planned** | next 12 months | idem (expected) |

The item list of the action question is identical across waves (with wording changes
*sought/seek*, *increased/increase*); the "sell more in Canada" item appears only from 2026 Q2
and is therefore excluded from the core index.

## Pillars (shares of businesses, %)

| Pillar | Items (CSBC categories) |
|---|---|
| P1 Market diversification (core) | Seek alternative customers outside the United States |
| P2 Supply-chain reconfiguration | Seek alternative suppliers outside the US **+** increase domestic sourcing |
| P3 Technology investment | Invest in technology improvements |
| P4 Financial / operational buffers | Explore trade-related financial tools **+** increase inventory **+** hire employees |
| P5 Digital readiness (reported, not in the index) | AI used in last 12 months (Q2 waves) / AI use planned (Q3 waves) / new technologies adopted in last 3 years (2026 Q1) |
| D Retrenchment (reported) | Delay Canadian investment or expansion **+** lay off employees **+** raise prices |
| N Passivity (reported) | "None" of the actions |

**Core index** = mean(P1, P2, P3, P4), in percentage points. It is interpretable as the
average share of businesses engaging in each active-adaptation pillar. `index_norm` rescales it
to 0-100 over the provinces x waves range; `net_score` subtracts one third of retrenchment;
`intensity_given_exposure` divides the index by the share of businesses reporting a negative
tariff impact (adaptation conditional on being hit).

Exposure variables reported alongside: share with direct sales to the US, share reporting a
negative impact of US tariffs (high + medium impact in 2025 Q2), share of US-selling
businesses whose goods were tariffed.

## Known limitations

1. **Taken vs planned.** Waves alternate between realised and intended actions; the series is
   therefore a mix of behaviour and intentions. The two "taken" waves are flagged (`horizon`).
2. **Shares, not intensities.** A business that reorganises its whole supply chain counts the
   same as one that found a single new supplier.
3. **Sector composition.** Provincial scores partly reflect industry mix; the industry-level
   file allows a composition-adjusted version (shift-share) as a next step.
4. **No weighting by exposure.** The index measures the adaptation *effort*, not the share of
   exposed businesses that adapt; the `intensity_given_exposure` ratio is a first correction.
5. **Survey end.** The CSBC ends with the 2026 Q3 wave; the index cannot be extended with the
   same source after December 2026.

## Reproducing

```bash
python code/01_clean_csbc.py      # 33 CSBC tables -> data/processed/csbc_long.csv
python code/02_build_index.py     # -> adaptation_index*.csv
python code/03_elections.py       # Elections Canada tables 11-12 -> district and province files
python code/03b_pollbypoll.py     # 343 poll-by-poll files -> polling-division file
python code/04_trade.py           # StatCan 12-10-0175 -> provincial exposure to the US
python code/05_analysis.py        # figures and correlation tables
python code/06_btos_vs_csbc.py    # US (BTOS) vs Canada (CSBC) AI adoption by sector
python code/07_programs.py        # tariff-response awards linked to ridings
```
