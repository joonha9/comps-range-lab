# Comps Range Lab: pre-registered protocol

Frozen before any agent search and before any validation-year range score was computed. Changes
after freezing are listed under Amendments, each dated and made before the results it could affect.

## Question

Comparable-company valuations are reported as ranges. Diagnostic 0 (exploration years only) shows
that the peer interquartile range, nominally a 50% range, contains market value 37–44% of the time.
Can AI agents, using the SignalLab design (proposer, blind critic, archive, deterministic grader),
write short, interpretable rules that make an 80% comps range honest: wide where comps are
unreliable, narrow where they are reliable? How close do they come to a black-box model?

## Fixed pipeline

- **Data.** ValuationLab FactSet panel (US non-financial firms, market value ≥ $100M, since-delisted
  firms kept), ValuationLab commit `7830673`. Statements for fiscal year *t*, market value on June 30
  of *t*+1.
- **Point estimate.** Per multiple (EV/EBITDA, EV/Sales): median multiple of the 10 nearest peers in
  the same 2-digit SIC sector on size (log sales) and EBITDA margin, times the target's driver
  (`rangelab/base.py`, `POINT_METHODS`). The target is never its own peer.
- **Error.** e = ln(actual EV / point estimate).
- **Rules.** The language in `rangelab/rules.py`: an uncertainty score from a base (constant, peer
  interquartile spread or peer range), at most 4 percentile-rank terms and at most 4 conditions.
  Inputs are the target's accounting characteristics, its peers' statistics and three flags; never
  the target's own market value.
- **Calibration** (`rangelab/grader.py`). On the fit years: centre c = median e, scale q = conformal
  80% quantile of |e − c| / s. Range = point × exp(c ± q·s). Learned benchmarks are cross-fitted so
  that calibration never uses in-sample predictions.
- **Score.** Interval score at α = 0.2 in logs (width + 10 × distance outside), averaged within each
  year, then across years. Lower is better.

## Periods

| Period | Years | Use |
|---|---|---|
| Exploration | FY2016–2019 | Agents' feedback: leave-one-year-out (calibrate on 3 years, score the 4th) |
| Validation | FY2020–2023 | Finalists scored once: rules and benchmarks fitted and calibrated on FY2016–2019 only |
| Holdout | FY2024–2025 | Opened once, after the validation report is committed, with the same tests |

Disclosure: FY2024–2025 were opened once on 2026-11-05 for ValuationLab's peer-recipe accuracy (a
different quantity, from different peer methods). No range score, interval score or coverage has been
computed on those years. FY2020–2023 were used for ValuationLab's validation; no range score has been
computed on them either.

## Methods compared

- **Practice (uncalibrated):** peer 25th–75th percentile range; peer min–max range.
- **Calibrated benchmarks** (same calibration as the rules): constant band; width proportional to peer
  interquartile spread; `linear_all` (regression of ln|e − c| on all inputs, no limit on terms);
  `gbm` (gradient-boosted trees on all inputs; settings fixed in `rangelab/baselines.py`);
  `hand_rule` (written by the author before any score was seen).
- **AI agents:** 5 independent runs (a1–a5). Each run: 5 generations × 6 proposals (3 per multiple),
  proposer sees exploration scores of its own archive, an independent critic sees no scores and
  approves or rejects each proposal. Agents are Claude Code subagents (no paid API); prompts,
  replies and every attempt (including invalid, duplicate and rejected ones) are archived.
- **Random search:** each run also grades 200 random rules per multiple drawn from the same language
  (seeded, no economic knowledge).

## Selection rule (fixed before the search)

Per run and multiple, the finalist is the graded rule with the lowest exploration interval score.

## Tests (validation years, each multiple separately)

Let A = mean validation interval score of the 5 runs' finalists.

- **T1, agents vs constant band (primary).** Pass if A is below the constant band's score **and** at
  least 4 of 5 finalists are below it.
- **T2, agents vs random search with the same budget.** For each run, draw as many random rules as
  that run graded for the multiple (without replacement from all 1,000 random rules for that multiple),
  select by the same rule, and average over 5 such runs; 20,000 simulations. One-sided p = share of
  simulated means ≤ A. Holm correction across the two multiples; pass at 0.05.
- **T3, agents vs `linear_all`.** Pass if A ≤ the `linear_all` score (four terms and four conditions
  match a regression on every input).
- **T4, share of the black-box gain captured.** G = (constant − A) / (constant − gbm). Rules are
  called "close to the black box" only if G ≥ 0.75. Reported in any case.

Secondary (reported, not tested): coverage by firm type (loss-making, smallest 20%, fastest-growing
20%, highest R&D 20%, fewer than 10 peers) as mean absolute deviation from 80%; coverage by year;
rolling recalibration (calibrate each validation year on all earlier years); the practice ranges'
coverage; the finalists' rules in full.

## Holdout

After the validation report is committed and pushed, FY2024–2025 base tables are built once and T1–T4
are repeated with rules and benchmarks fitted and calibrated on FY2016–2019 (primary) and on
FY2016–2023 (secondary). The holdout is then spent.

## Amendments

(none)
