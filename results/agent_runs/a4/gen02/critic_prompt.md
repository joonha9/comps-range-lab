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
  (none)

PROPOSALS
  (0) ebitda_small_innovative_loss
      rule: EV/EBITDA | base constant | terms log_sales -0.8, rnd_intensity +0.5, sales_growth_1y +0.4 | if loss_making x1.4
      mechanism: Small firms, R&D-heavy firms and fast growers carry most of their value in growth options and intangibles that current EBITDA does not capture, so the peer-median EBITDA multiple is a noisy anchor for them; loss-making firms with positive EBITDA have earnings far below normalized levels, making the EBITDA base itself unrepresentative. Large, mature, low-R&D firms trade close to sector multiples.
      prediction: Interval score below the constant band's 2.735 on EV/EBITDA, with coverage of loss-making and smallest-20% firms rising toward 80%.

  (1) ebitda_thin_margin_leverage
      rule: EV/EBITDA | base constant | terms ebitda_margin -0.8, net_debt_to_ebitda +0.5, log_assets -0.6 | if no_history x1.3
      mechanism: When EBITDA is a thin slice of sales, small changes in costs move EBITDA a lot proportionally, so EV/EBITDA for low-margin firms is unstable and depends on whether the market sees the margin as temporary. High net debt relative to EBITDA signals distress or restructuring, where EV reflects default and recovery scenarios rather than going-concern peer multiples; newly listed firms lack the track record investors use to price against peers.
      prediction: Interval score below the constant band's 2.735 on EV/EBITDA; the lowest-ebitda_margin quintile receives ranges at least 1.5x wider than the highest quintile.

  (2) ebitda_growth_extremes_intangibles
      rule: EV/EBITDA | base constant | terms log_sales -0.7, gross_margin +0.5 | if sales_growth_1y >= p85 x1.4 | if sales_growth_1y <= p10 x1.3
      mechanism: Firms at either tail of sales growth are in transition: hypergrowth firms are priced on future EBITDA far above current, and sharply shrinking firms are priced on turnaround or liquidation prospects, so both deviate from steady-state peer multiples. High gross margin indicates intangible-heavy business models whose valuations depend on scalability expectations that differ widely across firms.
      prediction: Interval score below the constant band's 2.735 on EV/EBITDA, with coverage of the fastest-growing 20% rising from 70% to at least 76%.

  (3) sales_profitability_gap
      rule: EV/Sales | base constant | terms ebitda_margin -1, log_sales -0.6, rnd_intensity +0.5 | if negative_ebitda x1.5
      mechanism: EV/Sales implicitly assumes the target converts sales to value like its peers, but value per dollar of sales scales with margins, so firms with low or negative EBITDA margins are priced on whether and when they will become profitable, a judgment the peer median cannot supply. Small and R&D-intensive firms add option-like value that sales do not reflect.
      prediction: Interval score below the constant band's 4.233 on EV/Sales, with negative-EBITDA and loss-making firms' coverage rising toward 80%.

  (4) sales_scalable_growth
      rule: EV/Sales | base constant | terms gross_margin +0.8, sales_growth_1y +0.6, log_assets -0.6 | if loss_making x1.3
      mechanism: High gross margin, fast-growing firms are valued on expected future operating leverage: each dollar of sales could become a large or small amount of future profit, so EV/Sales multiples within a sector fan out widely for them. Small firms and loss-makers add uncertainty about survival and dilution, while low-margin, slow-growth, large firms trade in a tight band of sales multiples.
      prediction: Interval score below the constant band's 4.233 on EV/Sales; the fastest-growing 20% achieve coverage of at least 77%.

  (5) sales_thin_comparables
      rule: EV/Sales | base constant | terms peer_iqr +0.4, log_sales -0.8 | if negative_ebitda x1.4 | if n_peers <= p10 x1.3 | if no_history x1.3
      mechanism: Comps are only as informative as the peer set: when peers disagree strongly on the sales multiple, or a firm's sector is thin or it lacks history, the median peer multiple says little about the target, and EV/Sales is especially sensitive because it ignores margin differences. Negative-EBITDA firms are additionally priced on survival odds, which no peer multiple encodes.
      prediction: Interval score below the constant band's 4.233 on EV/Sales, with fallback/few-peer firms' coverage rising from 71% to at least 77%.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}
