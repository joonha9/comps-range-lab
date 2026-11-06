# Robustness: other ways of picking peers (exploratory)

Frozen agent rules, unchanged. Validation (FY2020–2023) and holdout (FY2024–2025) were already used once for the pre-registered tests, so this check is exploratory. Produced by `scripts/robustness_peers.py`.

**A. Re-calibrated** on FY2016–2019 errors of each peer method. Interval score, lower is better; (k/5) = agent runs below the constant band.

| Multiple | Peer method | Point error (median abs, val) | Constant val | Agents val | GBM val | Constant hold | Agents hold | GBM hold |
|---|---|---|---|---|---|---|---|---|
| EV/EBITDA | primary: SIC2, 10 nearest on size+margin | 0.426 | 3.391 | 3.145 (5/5) | 2.719 | 3.449 | 3.243 (5/5) | 2.818 |
| EV/EBITDA | SIC3 industry, all peers | 0.426 | 3.587 | 3.290 (5/5) | 2.764 | 3.563 | 3.329 (5/5) | 2.932 |
| EV/EBITDA | SIC4 industry, all peers | 0.427 | 3.580 | 3.310 (5/5) | 2.767 | 3.548 | 3.333 (5/5) | 2.833 |
| EV/EBITDA | SIC3, 5 nearest on size+margin | 0.434 | 3.510 | 3.263 (5/5) | 2.859 | 3.523 | 3.321 (5/5) | 2.902 |
| EV/EBITDA | SIC3, 8 nearest on growth+ROIC | 0.404 | 3.371 | 3.121 (5/5) | 2.706 | 3.343 | 3.136 (5/5) | 2.767 |
| EV/Sales | primary: SIC2, 10 nearest on size+margin | 0.635 | 4.357 | 4.207 (5/5) | 3.818 | 4.444 | 4.266 (5/5) | 3.954 |
| EV/Sales | SIC3 industry, all peers | 0.650 | 5.672 | 5.217 (5/5) | 4.147 | 5.564 | 5.136 (5/5) | 4.071 |
| EV/Sales | SIC4 industry, all peers | 0.653 | 5.707 | 5.260 (5/5) | 4.223 | 5.578 | 5.150 (5/5) | 4.152 |
| EV/Sales | SIC3, 5 nearest on size+margin | 0.658 | 4.673 | 4.452 (5/5) | 4.094 | 4.647 | 4.455 (5/5) | 4.107 |
| EV/Sales | SIC3, 8 nearest on growth+ROIC | 0.598 | 5.002 | 4.636 (5/5) | 3.915 | 5.044 | 4.670 (5/5) | 3.940 |

**B. Transferred:** widths calibrated on the primary peer method, applied unchanged. Target coverage 80%.

| Multiple | Peer method | Constant coverage val | Agents coverage val | Constant coverage hold | Agents coverage hold |
|---|---|---|---|---|---|
| EV/EBITDA | primary: SIC2, 10 nearest on size+margin | 72.2% | 71.8% | 71.8% | 70.3% |
| EV/EBITDA | SIC3 industry, all peers | 71.8% | 70.9% | 71.9% | 70.0% |
| EV/EBITDA | SIC4 industry, all peers | 71.6% | 71.0% | 71.9% | 69.6% |
| EV/EBITDA | SIC3, 5 nearest on size+margin | 71.0% | 70.8% | 71.3% | 69.4% |
| EV/EBITDA | SIC3, 8 nearest on growth+ROIC | 73.7% | 72.7% | 73.7% | 72.2% |
| EV/Sales | primary: SIC2, 10 nearest on size+margin | 77.6% | 78.0% | 77.3% | 77.3% |
| EV/Sales | SIC3 industry, all peers | 75.3% | 75.5% | 74.7% | 74.9% |
| EV/Sales | SIC4 industry, all peers | 74.9% | 75.1% | 74.5% | 74.8% |
| EV/Sales | SIC3, 5 nearest on size+margin | 76.3% | 76.9% | 77.1% | 76.9% |
| EV/Sales | SIC3, 8 nearest on growth+ROIC | 78.2% | 79.0% | 77.7% | 77.9% |
