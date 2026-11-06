# Diagnostic 0: do practitioner comps ranges contain the market value?

Exploration years FY2016–2019 only. ValuationLab commit `7830673`. Produced by `scripts/diagnostic_ranges.py`.

| Multiple · peer method | n | Inside peer IQR (nominal 50%) | Inside peer min–max | Median IQR width (q75/q25 − 1) | ×/÷ factor needed for 80% | Actual's quartile in peer distribution (25% each if calibrated) |
|---|---|---|---|---|---|---|
| EV/EBITDA · industry_sic3 | 8,262 | 43.2% | 85.2% | 84% | ×/÷ 2.10 | 26% / 22% / 24% / 28% |
| EV/EBITDA · size_margin_k10 | 8,261 | 40.9% | 80.6% | 68% | ×/÷ 2.10 | 26% / 18% / 27% / 29% |
| EV/EBITDA · growth_roic_k8 | 8,108 | 36.8% | 72.5% | 58% | ×/÷ 2.06 | 22% / 21% / 22% / 36% |
| EV/Sales · industry_sic3 | 10,357 | 44.2% | 87.5% | 188% | ×/÷ 3.73 | 26% / 23% / 24% / 27% |
| EV/Sales · size_margin_k10 | 10,357 | 41.1% | 81.2% | 151% | ×/÷ 3.36 | 25% / 18% / 27% / 30% |
| EV/Sales · margin_growth_k8 | 10,327 | 36.9% | 72.4% | 102% | ×/÷ 3.11 | 22% / 20% / 21% / 37% |

## IQR coverage by firm type

| Multiple · peer method | All | Loss-making | Smallest 20% | Fastest-growing 20% | Highest R&D 20% |
|---|---|---|---|---|---|
| EV/EBITDA · industry_sic3 | 43.2% | 35.2% (n=1,684) | 32.2% (n=609) | 36.2% (n=1,208) | 40.9% (n=633) |
| EV/EBITDA · size_margin_k10 | 40.9% | 36.7% (n=1,684) | 40.6% (n=609) | 34.7% (n=1,208) | 32.2% (n=633) |
| EV/EBITDA · growth_roic_k8 | 36.8% | 33.3% (n=1,636) | 28.1% (n=559) | 31.7% (n=1,170) | 32.8% (n=598) |
| EV/Sales · industry_sic3 | 44.2% | 40.8% (n=3,696) | 40.1% (n=2,064) | 45.2% (n=1,875) | 47.6% (n=2,073) |
| EV/Sales · size_margin_k10 | 41.1% | 39.0% (n=3,696) | 39.0% (n=2,064) | 36.9% (n=1,875) | 39.0% (n=2,073) |
| EV/Sales · margin_growth_k8 | 36.9% | 34.9% (n=3,685) | 31.5% (n=2,048) | 35.9% (n=1,866) | 36.6% (n=2,072) |

Factor for 80%: the f such that [point / f, point × f] around the point estimate (aggregated peer multiple × driver) would have contained 80% of actual enterprise values.
