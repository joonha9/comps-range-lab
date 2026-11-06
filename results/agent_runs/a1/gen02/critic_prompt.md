You are an independent referee for a valuation research project. A proposer has submitted
rules that say how uncertain a comparable-company valuation is for each firm. You decide which may
be tested. You do NOT see any results, and you must not try to find any: judge only the logic.

RULE LANGUAGE
A range rule gives every target firm-year a positive UNCERTAINTY SCORE s. Only the relative
ranking of s across firms matters: the grader converts scores into ranges by calibration.

  s = BASE x exp( sum_j w_j * (pct_j - 0.5) ) x (product of `times` for every condition that holds)

  base:        one of ['constant', 'peer_iqr', 'peer_range']
               "constant" = 1; "peer_iqr" = the peers' log interquartile spread (floored at 0.05);
               "peer_range" = the peers' log max/min spread (floored at 0.10)
  terms:       up to 4 {INPUT: weight}, weight a non-zero number in [-3.0, 3.0].
               pct_j is the firm's percentile rank (0-1) on that input WITHIN its fiscal year, so
               weight +1.0 makes the top firm's score e^1 = 2.7x the bottom firm's. Missing = median.
  conditions:  up to 4 {"if": [clause, clause?], "times": t}, t in [0.25, 4.0], t != 1.
               All clauses (1 or 2) must hold. A clause is a FLAG {"var": "loss_making"} or a
               continuous input with exactly one threshold {"var": X, "below_pct": P} or
               {"var": X, "above_pct": P}, P an integer 5-95 (within-year percentile).
               A missing input makes the clause false.
  The constant band alone (base "constant", no terms, no conditions) is not a valid proposal.

INPUTS (accounting characteristics of the target, statistics of its peers, and flags; the
target's own market value, price or multiple is never available)
  - log_sales: log of sales (size)
  - log_assets: log of total assets (size)
  - sales_growth_1y: 1-year sales growth
  - sales_growth_3y: 3-year annualized sales growth (missing for FY2016-2017: not enough history)
  - gross_margin: gross profit / sales
  - ebitda_margin: EBITDA / sales
  - ebit_margin: EBIT / sales
  - net_margin: net income / sales
  - roic: EBIT x (1 - 25%) / (equity + debt - cash)
  - roe: net income / book equity
  - asset_turnover: sales / total assets
  - net_debt_to_ebitda: (debt - cash) / EBITDA
  - debt_to_assets: total debt / total assets
  - rnd_intensity: R&D / sales
  - capex_intensity: capital expenditure / sales
  - peer_iqr: log(75th / 25th percentile) of the 10 peers' multiples: how much the peers disagree
  - peer_range: log(max / min) of the peers' multiples
  - n_peers: number of peers found (10 unless the sector is thin)
  - loss_making: FLAG: net income < 0
  - negative_ebitda: FLAG: EBITDA <= 0 (only possible for EV/Sales; EV/EBITDA needs positive EBITDA)
  - no_history: FLAG: no prior-year sales in the data (recent listing or new to the sample)

HOW RANGES ARE SCORED
  Point estimate: the median EV multiple of the target's 10 nearest peers (same 2-digit SIC;
  nearest on size and EBITDA margin) times the target's EBITDA or sales. e = ln(actual EV /
  point estimate), actual EV on June 30 after the fiscal year.
  Calibration on the other years: centre c = median e; q = 80% conformal quantile of |e - c| / s.
  Range: point x exp(c - q s) to point x exp(c + q s). So every rule covers ~80% overall; a good
  rule puts wide ranges on firms that are truly hard to value and narrow ranges on easy ones.
  Interval score (lower is better) = width + 10 x distance outside the range, in logs.
  Exploration score: leave-one-year-out over FY2016-2019 (calibrate on 3 years, score the 4th).

Approve a proposal only if ALL hold:
  1. The mechanism is a specific, economically sensible reason why comps should be less (or
     more) reliable for the firms the rule singles out.
  2. The rule actually implements that mechanism (inputs, signs and conditions match it).
  3. It is not a trivial variant of a rule already tried (listed below): changing only one weight
     or one threshold slightly is trivial; a new input, condition or economic idea is not.
  4. The prediction is falsifiable.
Reject otherwise, with a one-sentence reason the proposer can learn from.

RULES ALREADY TRIED (no scores shown)
  [g01-01] EV/EBITDA | base constant | terms log_sales -1, ebitda_margin -0.8 | if loss_making x1.4
  [g01-02] EV/EBITDA | base constant | terms rnd_intensity +0.8, sales_growth_1y +0.6, log_assets -0.7 | if no_history x1.5
  [g01-03] EV/EBITDA | base constant | terms roic -0.8, log_sales -0.8 | if ebitda_margin <= p20 x1.4 | if debt_to_assets >= p80 AND ebit_margin <= p30 x1.3
  [g01-04] EV/Sales | base constant | terms ebitda_margin -1, log_sales -0.8 | if negative_ebitda x1.6 | if no_history x1.3
  [g01-05] EV/Sales | base constant | terms gross_margin +0.8, rnd_intensity +0.7, sales_growth_1y +0.7, log_assets -0.6
  [g01-06] EV/Sales | base constant | terms log_sales -1, peer_iqr +0.5, net_margin -0.6 | if loss_making AND log_sales <= p30 x1.5 | if debt_to_assets >= p80 x1.3

PROPOSALS
  (0) g02-ebitda-denominator-and-expensed-investment
      rule: EV/EBITDA | base constant | terms log_sales -0.8, ebitda_margin -0.6, rnd_intensity +0.5, sales_growth_1y +0.4 | if loss_making x1.3
      mechanism: Two separate things make trailing EV/EBITDA unreliable. First, when EBITDA is a thin slice of sales, small cost shocks swing it by large percentages, so the market prices normalized rather than current EBITDA (made worse in small and loss-making firms). Second, R&D-heavy and fast-growing firms expense investment that is economically capex, so current EBITDA understates the earnings base on which EV is set. A rule with only one channel leaves the other group under-covered.
      prediction: Interval score below 2.571 (best earlier rule) and below the constant band's 2.735, with coverage of fastest_growing_20pct and highest_rnd_20pct both rising above 74% while loss_making and smallest_20pct stay at 75% or more.

  (1) g02-ebitda-da-wedge-and-leverage
      rule: EV/EBITDA | base constant | terms capex_intensity +0.5, ebit_margin -0.7, log_sales -0.7 | if net_debt_to_ebitda >= p85 x1.25
      mechanism: EBITDA comes before depreciation and capex. In capital-intensive firms where D&A and reinvestment eat most of EBITDA, the earnings investors actually value (EBIT, free cash flow) are a small, volatile residual, so the same EBITDA supports very different EVs across peers. When net debt is large relative to EBITDA, equity is a thin levered claim whose value depends on refinancing and covenant risk, which adds dispersion that peers with ordinary leverage do not share.
      prediction: Interval score below the constant band's 2.735, and lower than a size-only rule, because capex_intensity and a low EBIT margin add information beyond log_sales.

  (2) g02-ebitda-cyclical-peak-trough
      rule: EV/EBITDA | base constant | terms log_sales -0.8, net_margin -0.5 | if sales_growth_1y >= p85 x1.3 | if sales_growth_1y <= p10 x1.3
      mechanism: A firm whose sales just jumped or collapsed is likely at a cyclical or event-driven peak or trough (acquisition, divestiture, lost contract), so trailing EBITDA is a poor proxy for the run-rate the market values. Investors look through it and the multiple swings far from peers in either direction. The relationship is U-shaped in growth, which a single linear growth term cannot capture, so both tails get their own condition, on top of size and net-margin scaling.
      prediction: Interval score below the constant band's 2.735, with coverage of fastest_growing_20pct at 76% or more and a clear improvement over the constant band for firms in the bottom decile of sales growth.

  (3) g02-sales-thin-sector-moderate-size
      rule: EV/Sales | base constant | terms n_peers -0.6, log_sales -0.4, peer_range +0.3 | if negative_ebitda x1.3
      mechanism: When a 2-digit SIC sector is thin, the 'nearest' peers are forced from businesses that differ in model and margin structure, so the peer median EV/Sales is a weak anchor. These fallback firms are the only group the constant band under-covers that earlier rules never fixed. Size adds idiosyncratic and liquidity noise but only mildly: earlier rules that weighted size and margin heavily over-covered small and loss-making firms (about 90%) and scored worse than the constant band, so this rule keeps those weights low and adds peer dispersion only as a moderate term.
      prediction: Interval score below the constant band's 4.233, with fallback_or_few_peers coverage rising above 76% and smallest_20pct coverage staying between 72% and 85% (no over-coverage).

  (4) g02-sales-opex-headroom
      rule: EV/Sales | base constant | terms gross_margin +0.6, ebitda_margin -0.6, log_sales -0.3
      mechanism: A firm with a high gross margin but a low EBITDA margin spends heavily on discretionary opex (selling, marketing, R&D) that could in principle be cut. Its EV depends on whether the market thinks that spending will scale down into high mature margins, a judgment that varies widely across firms with similar current economics. A firm whose low gross margin limits its EBITDA has no such headroom, and its revenue multiple is pinned by structurally thin margins.
      prediction: Interval score below the constant band's 4.233 and below g01-04 (4.447), because the gross-margin-minus-EBITDA-margin contrast identifies margin optionality better than low EBITDA margin alone.

  (5) g02-sales-revenue-run-rate-break
      rule: EV/Sales | base constant | terms log_assets -0.3 | if sales_growth_1y >= p85 x1.35 | if sales_growth_1y <= p10 x1.3 | if no_history x1.25
      mechanism: EV/Sales assumes trailing sales represent the firm's revenue run-rate. After a big acquisition, a divestiture, a collapse in demand or an explosive ramp, they do not: the market values forward revenue that is far above or below trailing sales, so the multiple departs from peers in both directions. Newly listed firms with no prior-year sales are often in exactly this kind of transition. This is a U-shaped growth effect plus a history flag, not a size or margin effect.
      prediction: Interval score below the constant band's 4.233, with fastest_growing_20pct coverage at 78% or more and loss_making and smallest_20pct coverage staying below 85%.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}
