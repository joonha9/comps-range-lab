# Holdout report: FY2024–2025

Produced by `scripts/evaluate.py` under [`docs/protocol.md`](../../docs/protocol.md). Fitted and calibrated on FY2016–2019. Runs: a1, a2, a3, a4, a5. ValuationLab commit `7830673`.

## EV/EBITDA

| Method | Interval score | Coverage | Median range (×/÷) | Segment coverage MAD from 80% | Rolling recalibration IS |
|---|---|---|---|---|---|
| Agent finalist a1 (g04-02) | 3.209 | 70.3% | 1.99 | 0.128 | 3.146 |
| Agent finalist a2 (g03-01) | 3.267 | 70.4% | 1.95 | 0.150 | 3.203 |
| Agent finalist a3 (g05-01) | 3.216 | 70.3% | 1.96 | 0.139 | 3.159 |
| Agent finalist a4 (g05-03) | 3.241 | 70.0% | 2.00 | 0.139 | 3.162 |
| Agent finalist a5 (g05-01) | 3.282 | 70.4% | 2.01 | 0.147 | 3.210 |
| practice_iqr | 4.042 | 40.2% | 1.40 | 0.435 | — |
| practice_minmax | 3.227 | 80.3% | 2.68 | 0.053 | — |
| constant | 3.449 | 71.8% | 2.10 | 0.191 | 3.388 |
| peer_iqr_scaled | 3.370 | 81.2% | 2.59 | 0.053 | 3.361 |
| linear_all | 3.106 | 70.4% | 1.93 | 0.108 | 3.044 |
| gbm | 2.818 | 74.6% | 2.02 | 0.062 | 2.734 |
| hand_rule | 3.598 | 81.4% | 2.60 | 0.058 | 3.566 |

- Agents' mean interval score: **3.243**
- T1 vs constant band (3.449): 5/5 runs below → **pass**
- T2 vs random search, same budget (median 3.326): p = 0.0008, Holm 0.0016 → **pass**
- T3 vs linear_all (3.106): **fail**
- T4 share of the black-box gain (gbm 2.818): G = 0.33 → not close to the black box

Finalist rules:

- a1: `EV/EBITDA | base constant | terms log_sales -0.8, ebitda_margin -0.6, net_debt_to_ebitda -0.5, rnd_intensity +0.3 | if loss_making x1.25 | if sales_growth_1y >= p85 x1.25 | if sales_growth_1y <= p10 x1.25`
- a2: `EV/EBITDA | base constant | terms net_debt_to_ebitda -0.8, log_sales -0.6 | if net_debt_to_ebitda <= p10 x1.3 | if loss_making x1.3`
- a3: `EV/EBITDA | base constant | terms log_sales -0.8, ebitda_margin -0.7, net_debt_to_ebitda -0.6 | if net_debt_to_ebitda <= p10 x1.3 | if loss_making x1.3`
- a4: `EV/EBITDA | base constant | terms log_sales -0.8, net_debt_to_ebitda -0.4 | if net_debt_to_ebitda <= p10 x1.3 | if net_debt_to_ebitda >= p95 x1.3 | if loss_making x1.3`
- a5: `EV/EBITDA | base constant | terms log_sales -0.8, ebitda_margin -0.6 | if loss_making x1.3`

## EV/Sales

| Method | Interval score | Coverage | Median range (×/÷) | Segment coverage MAD from 80% | Rolling recalibration IS |
|---|---|---|---|---|---|
| Agent finalist a1 (g03-04) | 4.237 | 77.2% | 3.10 | 0.041 | 4.228 |
| Agent finalist a2 (g02-04) | 4.254 | 77.4% | 3.15 | 0.054 | 4.247 |
| Agent finalist a3 (g05-06) | 4.239 | 77.2% | 3.14 | 0.038 | 4.233 |
| Agent finalist a4 (g02-06) | 4.282 | 77.6% | 3.14 | 0.025 | 4.281 |
| Agent finalist a5 (g05-04) | 4.316 | 77.0% | 3.28 | 0.077 | 4.303 |
| practice_iqr | 5.492 | 40.8% | 1.65 | 0.429 | — |
| practice_minmax | 4.330 | 81.0% | 4.01 | 0.040 | — |
| constant | 4.444 | 77.3% | 3.38 | 0.115 | 4.434 |
| peer_iqr_scaled | 4.554 | 79.5% | 3.94 | 0.050 | 4.548 |
| linear_all | 4.190 | 77.0% | 3.23 | 0.045 | 4.175 |
| gbm | 3.954 | 77.6% | 3.06 | 0.061 | 3.858 |
| hand_rule | 5.106 | 80.1% | 4.17 | 0.080 | 5.086 |

- Agents' mean interval score: **4.266**
- T1 vs constant band (4.444): 5/5 runs below → **pass**
- T2 vs random search, same budget (median 4.481): p = 0.0000, Holm 0.0000 → **pass**
- T3 vs linear_all (4.190): **fail**
- T4 share of the black-box gain (gbm 3.954): G = 0.36 → not close to the black box

Finalist rules:

- a1: `EV/Sales | base constant | terms n_peers -0.6, peer_range +0.3, log_assets -0.3 | if sales_growth_1y >= p85 x1.3 | if sales_growth_1y <= p10 x1.3 | if no_history x1.2 | if negative_ebitda x1.25`
- a2: `EV/Sales | base constant | terms debt_to_assets -0.6, ebitda_margin -0.5 | if negative_ebitda x1.3`
- a3: `EV/Sales | base constant | terms peer_range +0.5, log_sales -0.6 | if gross_margin <= p15 x1.4 | if ebitda_margin <= p15 x1.4 | if n_peers <= p10 x1.4`
- a4: `EV/Sales | base constant | terms peer_iqr +0.4, log_sales -0.8 | if negative_ebitda x1.4 | if n_peers <= p10 x1.3 | if no_history x1.3`
- a5: `EV/Sales | base constant | terms log_sales -0.5, n_peers -0.7, peer_range +0.4`
