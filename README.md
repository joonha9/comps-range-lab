# Comps Range Lab

**How much should you trust a comparable-company valuation?** Practitioners report comps as a
range (for example, the 25th–75th percentile of peer multiples on a football-field chart). This
project tests whether those ranges contain market value as often as they appear to, and whether AI
agents, following the SignalLab design (Liu, Liu, Liu & Mei 2026), can write short, interpretable
rules that say when a comps valuation should be trusted and how wide its range should be.

Status: protocol frozen ([`docs/protocol.md`](docs/protocol.md)); agent search on exploration years next.
Validation and holdout years have not been scored.

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
