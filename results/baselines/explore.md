# Benchmarks on exploration years (leave-one-year-out, FY2016–2019)

ValuationLab commit `7830673`. Interval score at 80% in logs (lower is better). Practice ranges are scored as reported, without calibration.

| Multiple | Method | Interval score | Coverage | Median range (×/÷) | Coverage: loss_making | Coverage: smallest_20pct | Coverage: fastest_growing_20pct | Coverage: highest_rnd_20pct | Coverage: fallback_or_few_peers |
|---|---|---|---|---|---|---|---|---|---|
| EV/EBITDA | practice_iqr | 3.258 | 40.9% | 1.29 | 37% | 40% | 35% | 39% | 37% |
| EV/EBITDA | practice_minmax | 2.684 | 80.6% | 2.26 | 78% | 77% | 75% | 79% | 68% |
| EV/EBITDA | constant | 2.735 | 79.6% | 2.10 | 68% | 63% | 70% | 66% | 83% |
| EV/EBITDA | peer_iqr_scaled | 2.732 | 80.0% | 2.11 | 75% | 77% | 75% | 77% | 72% |
| EV/EBITDA | linear_all | 2.448 | 79.9% | 1.94 | 81% | 79% | 76% | 81% | 78% |
| EV/EBITDA | gbm | 2.219 | 79.9% | 1.90 | 80% | 78% | 80% | 80% | 81% |
| EV/EBITDA | hand_rule | 2.979 | 80.1% | 2.11 | 83% | 89% | 79% | 86% | 70% |
| EV/Sales | practice_iqr | 5.226 | 41.1% | 1.59 | 39% | 39% | 37% | 39% | 38% |
| EV/Sales | practice_minmax | 4.108 | 81.2% | 3.63 | 79% | 79% | 77% | 79% | 67% |
| EV/Sales | constant | 4.233 | 80.0% | 3.38 | 72% | 68% | 75% | 72% | 71% |
| EV/Sales | peer_iqr_scaled | 4.340 | 80.0% | 3.56 | 76% | 75% | 77% | 79% | 74% |
| EV/Sales | linear_all | 3.970 | 80.0% | 3.23 | 80% | 80% | 78% | 80% | 78% |
| EV/Sales | gbm | 3.483 | 80.1% | 2.86 | 79% | 78% | 80% | 79% | 79% |
| EV/Sales | hand_rule | 4.829 | 80.0% | 3.60 | 88% | 89% | 83% | 92% | 69% |
