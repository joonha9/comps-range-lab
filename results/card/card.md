# Comps confidence card

Built from what the five frozen agent finalists share, after the pre-registered tests. Cut-offs come from exploration years. Out-of-sample scores are exploratory. Produced by `scripts/card.py`.

## EV/EBITDA

Warning flags: sales below $400M; net loss; net cash above 2x EBITDA; EBITDA margin below 8%.

| Confidence | Flags | Share of firms | 80% range (published, FY2016–2025) |
|---|---|---|---|
| high | 0 | 53% | point × 0.53 to × 1.99 (×/÷ 1.94) |
| medium | 1 | 29% | point × 0.42 to × 2.48 (×/÷ 2.42) |
| low | 2 or more | 18% | point × 0.20 to × 5.19 (×/÷ 5.05) |

Point estimate = median peer multiple × the target's driver. The centre (× 1.03) corrects the average gap between market value and the peer median.

Out-of-sample check (widths fitted on FY2016–2019):

| Period | Card interval score | Card coverage | Coverage high / medium / low | Agent rules (mean of 5) | Constant band | Constant coverage |
|---|---|---|---|---|---|---|
| validate | 3.179 | 71.7% | 72% / 70% / 74% | 3.145 | 3.391 | 72.2% |
| holdout | 3.287 | 69.6% | 69% / 70% / 72% | 3.243 | 3.449 | 71.8% |

## EV/Sales

Warning flags: sales below $150M; negative EBITDA; peer multiples span more than 30x; fewer than 10 peers.

| Confidence | Flags | Share of firms | 80% range (published, FY2016–2025) |
|---|---|---|---|
| high | 0 | 55% | point × 0.36 to × 3.09 (×/÷ 2.93) |
| medium | 1 | 24% | point × 0.28 to × 4.01 (×/÷ 3.80) |
| low | 2 or more | 21% | point × 0.16 to × 6.88 (×/÷ 6.51) |

Point estimate = median peer multiple × the target's driver. The centre (× 1.06) corrects the average gap between market value and the peer median.

Out-of-sample check (widths fitted on FY2016–2019):

| Period | Card interval score | Card coverage | Coverage high / medium / low | Agent rules (mean of 5) | Constant band | Constant coverage |
|---|---|---|---|---|---|---|
| validate | 4.235 | 79.1% | 78% / 79% / 81% | 4.207 | 4.357 | 77.6% |
| holdout | 4.295 | 78.4% | 79% / 77% / 78% | 4.266 | 4.444 | 77.3% |
