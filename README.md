# Comps Range Lab

**How much should you trust a comparable-company valuation?** Practitioners report comps as a
range (for example, the 25th–75th percentile of peer multiples on a football-field chart). This
project tests whether those ranges contain market value as often as they appear to, and whether AI
agents, following the SignalLab design (Liu, Liu, Liu & Mei 2026), can write short, interpretable
rules that say when a comps valuation should be trusted and how wide its range should be.

Status: complete. Protocol frozen before the search ([`docs/protocol.md`](docs/protocol.md)); validation
(FY2020–2023) and holdout (FY2024–2025) each scored once. The holdout is now spent.

## Findings (interval score of 80% ranges, lower is better)

| Method | EV/EBITDA validation | EV/EBITDA holdout | EV/Sales validation | EV/Sales holdout |
|---|---|---|---|---|
| Peer 25th–75th percentile range, as practitioners report it (covers ~41%) | 4.004 | 4.042 | 5.458 | 5.492 |
| Constant band (one width for every firm) | 3.391 | 3.449 | 4.357 | 4.444 |
| Peer min–max range, uncalibrated (covers ~81%) | 3.265 | 3.227 | 4.298 | 4.330 |
| **AI agents' rules, mean of 5 runs** | **3.145** | **3.243** | **4.207** | **4.266** |
| Linear regression on all 33 inputs | 3.048 | 3.106 | 4.097 | 4.190 |
| Gradient-boosted trees (black box) | 2.719 | 2.818 | 3.818 | 3.954 |

- **Replicated in the holdout on both multiples.** Agent rules beat the constant band in 5 of 5 runs (T1) and
  random rules with the same budget (T2, p ≤ 0.002). They do not beat an unrestricted regression (T3) and
  capture about a third of the black box's gain (T4: G = 0.28–0.36, below the 0.75 bar).
- The five runs converged on the same short rule: wider ranges for small firms, loss-making firms, firms with
  extreme net debt (large net cash or high leverage) and low EBITDA margins.
- Practitioners' interquartile range contains market value about 41% of the time in every period.
- Calibrated on 2016–2019, every EV/EBITDA method except the black box under-covers later years (about 70–72%
  against 80%).

Reports: [`results/validate/REPORT.md`](results/validate/REPORT.md), [`results/holdout/REPORT.md`](results/holdout/REPORT.md).

## Diagnostic 0 (FY2016–2019, exploration years)

[`results/diagnostic/ranges.md`](results/diagnostic/ranges.md)

- The peer interquartile range, which nominally contains the market value half the time, contains
  it 37–44% of the time.
- Tighter, "better" peer sets (k nearest on fundamentals) make this worse (about 37%): the range
  narrows faster than accuracy improves.
- A range that contains 80% of market values must span roughly ÷2.1 to ×2.1 around the EV/EBITDA
  point estimate, and ÷3.1–3.7 to ×3.1–3.7 for EV/Sales.

## Setup

Builds on [ValuationLab](https://github.com/joonha9/Valuation_Lab), a sibling checkout (set
`VALUATION_LAB` or place it at `../valuation-lab`). Its panel, comps engine and baselines are
imported; the licensed FactSet data stays in that checkout and is never committed here. Every
result records the ValuationLab commit it ran against.

```bash
python3 scripts/diagnostic_ranges.py     # Diagnostic 0
python3 scripts/run_baselines.py         # benchmarks, exploration years (leave-one-year-out)
python3 scripts/agent_step.py --new a1   # create an agent run; then --runs a1 to advance it
python3 -m pytest -q tests
```

## Protocol

See [`docs/protocol.md`](docs/protocol.md). Same year split as ValuationLab: explore FY2016–2019, validate FY2020–2023, holdout FY2024–2025.
FY2024–2025 were opened once for ValuationLab's peer recipes (2026-11-05). This project will
freeze its own protocol before touching validation or holdout years, and will disclose that history.
