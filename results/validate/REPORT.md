# Validate report: FY2020–2023

Produced by `scripts/evaluate.py` under [`docs/protocol.md`](../../docs/protocol.md). Fitted and calibrated on FY2016–2019. Runs: a1, a2, a3, a4, a5. ValuationLab commit `7830673`.

## EV/EBITDA

| Method | Interval score | Coverage | Median range (×/÷) | Segment coverage MAD from 80% | Rolling recalibration IS |
|---|---|---|---|---|---|
| Agent finalist a1 (g04-02) | 3.114 | 72.0% | 2.00 | 0.118 | 3.089 |
| Agent finalist a2 (g03-01) | 3.165 | 71.6% | 1.97 | 0.136 | 3.140 |
| Agent finalist a3 (g05-01) | 3.117 | 71.8% | 1.97 | 0.124 | 3.097 |
| Agent finalist a4 (g05-03) | 3.138 | 71.6% | 2.00 | 0.129 | 3.106 |
| Agent finalist a5 (g05-01) | 3.194 | 71.8% | 2.03 | 0.134 | 3.163 |
| practice_iqr | 4.004 | 41.1% | 1.39 | 0.416 | — |
| practice_minmax | 3.265 | 80.7% | 2.70 | 0.038 | — |
| constant | 3.391 | 72.2% | 2.10 | 0.186 | 3.362 |
| peer_iqr_scaled | 3.356 | 80.5% | 2.53 | 0.046 | 3.351 |
| linear_all | 3.048 | 71.5% | 1.95 | 0.089 | 3.016 |
| gbm | 2.719 | 76.4% | 2.06 | 0.041 | 2.686 |
| hand_rule | 3.640 | 81.2% | 2.58 | 0.058 | 3.621 |

- Agents' mean interval score: **3.145**
- T1 vs constant band (3.391): 5/5 runs below → **pass**
- T2 vs random search, same budget (median 3.307): p = 0.0000, Holm 0.0000 → **pass**
- T3 vs linear_all (3.048): **fail**
- T4 share of the black-box gain (gbm 2.719): G = 0.36 → not close to the black box

Finalist rules:

- a1: `EV/EBITDA | base constant | terms log_sales -0.8, ebitda_margin -0.6, net_debt_to_ebitda -0.5, rnd_intensity +0.3 | if loss_making x1.25 | if sales_growth_1y >= p85 x1.25 | if sales_growth_1y <= p10 x1.25`
- a2: `EV/EBITDA | base constant | terms net_debt_to_ebitda -0.8, log_sales -0.6 | if net_debt_to_ebitda <= p10 x1.3 | if loss_making x1.3`
- a3: `EV/EBITDA | base constant | terms log_sales -0.8, ebitda_margin -0.7, net_debt_to_ebitda -0.6 | if net_debt_to_ebitda <= p10 x1.3 | if loss_making x1.3`
- a4: `EV/EBITDA | base constant | terms log_sales -0.8, net_debt_to_ebitda -0.4 | if net_debt_to_ebitda <= p10 x1.3 | if net_debt_to_ebitda >= p95 x1.3 | if loss_making x1.3`
- a5: `EV/EBITDA | base constant | terms log_sales -0.8, ebitda_margin -0.6 | if loss_making x1.3`

## EV/Sales

| Method | Interval score | Coverage | Median range (×/÷) | Segment coverage MAD from 80% | Rolling recalibration IS |
|---|---|---|---|---|---|
| Agent finalist a1 (g03-04) | 4.180 | 78.1% | 3.20 | 0.023 | 4.177 |
| Agent finalist a2 (g02-04) | 4.206 | 78.2% | 3.19 | 0.040 | 4.207 |
| Agent finalist a3 (g05-06) | 4.171 | 77.4% | 3.16 | 0.029 | 4.173 |
| Agent finalist a4 (g02-06) | 4.258 | 79.0% | 3.21 | 0.042 | 4.260 |
| Agent finalist a5 (g05-04) | 4.222 | 77.1% | 3.33 | 0.058 | 4.217 |
| practice_iqr | 5.458 | 41.0% | 1.65 | 0.417 | — |
| practice_minmax | 4.298 | 81.4% | 4.02 | 0.029 | — |
| constant | 4.357 | 77.6% | 3.38 | 0.095 | 4.353 |
| peer_iqr_scaled | 4.526 | 80.5% | 3.97 | 0.030 | 4.520 |
| linear_all | 4.097 | 78.4% | 3.33 | 0.025 | 4.090 |
| gbm | 3.818 | 77.4% | 3.07 | 0.052 | 3.792 |
| hand_rule | 5.184 | 80.6% | 4.15 | 0.093 | 5.166 |

- Agents' mean interval score: **4.207**
- T1 vs constant band (4.357): 5/5 runs below → **pass**
- T2 vs random search, same budget (median 4.422): p = 0.0000, Holm 0.0000 → **pass**
- T3 vs linear_all (4.097): **fail**
- T4 share of the black-box gain (gbm 3.818): G = 0.28 → not close to the black box

Finalist rules:

- a1: `EV/Sales | base constant | terms n_peers -0.6, peer_range +0.3, log_assets -0.3 | if sales_growth_1y >= p85 x1.3 | if sales_growth_1y <= p10 x1.3 | if no_history x1.2 | if negative_ebitda x1.25`
- a2: `EV/Sales | base constant | terms debt_to_assets -0.6, ebitda_margin -0.5 | if negative_ebitda x1.3`
- a3: `EV/Sales | base constant | terms peer_range +0.5, log_sales -0.6 | if gross_margin <= p15 x1.4 | if ebitda_margin <= p15 x1.4 | if n_peers <= p10 x1.4`
- a4: `EV/Sales | base constant | terms peer_iqr +0.4, log_sales -0.8 | if negative_ebitda x1.4 | if n_peers <= p10 x1.3 | if no_history x1.3`
- a5: `EV/Sales | base constant | terms log_sales -0.5, n_peers -0.7, peer_range +0.4`
