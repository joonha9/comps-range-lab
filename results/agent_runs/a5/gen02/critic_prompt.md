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
  [g01-01] EV/EBITDA | base constant | terms log_sales -1, rnd_intensity +0.6, sales_growth_1y +0.4 | if loss_making x1.4
  [g01-02] EV/EBITDA | base constant | terms ebitda_margin -1.2, roic -0.5, log_assets -0.7 | if net_debt_to_ebitda >= p90 x1.3
  [g01-03] EV/EBITDA | base constant | terms gross_margin +0.7, sales_growth_1y +0.6, peer_iqr +0.5, log_sales -0.6 | if no_history x1.3
  [g01-04] EV/Sales | base constant | terms ebitda_margin -1, log_sales -0.8 | if negative_ebitda x1.6 | if loss_making x1.2
  [g01-05] EV/Sales | base constant | terms gross_margin +0.8, rnd_intensity +0.8, sales_growth_1y +0.6, log_sales -0.6
  [g01-06] EV/Sales | base constant | terms log_assets -1.2, sales_growth_1y +0.5 | if loss_making AND log_sales <= p30 x1.5 | if no_history x1.3

PROPOSALS
  (0) ebitda_depressed_base
      rule: EV/EBITDA | base constant | terms ebitda_margin -1, roic -0.6 | if net_debt_to_ebitda >= p90 x1.3
      mechanism: When EBITDA is temporarily depressed relative to the firm's sales and invested capital, the market prices normalized earnings rather than current EBITDA, so applying a peer EBITDA multiple to a shrunken denominator misplaces EV by a large and unpredictable factor. Low EBITDA margins, low returns on capital and very high net debt relative to EBITDA are three readings of the same thing: an EBITDA base that is small compared with what the firm's assets and capital structure are built to earn.
      prediction: Interval score below the constant band's 2.735, with coverage of loss_making firms rising toward 80% and the widest ranges concentrated in the lowest ebitda_margin quintile.

  (1) ebitda_growth_options
      rule: EV/EBITDA | base constant | terms sales_growth_1y +0.7, rnd_intensity +0.7 | if no_history x1.4
      mechanism: For fast-growing, R&D-intensive and newly listed firms, most of enterprise value comes from growth options that current EBITDA does not capture, and how the market values those options differs a lot from firm to firm; a peer-median EBITDA multiple cannot price them. Recent listings (no prior-year sales) are the purest version of this: young firms valued on their future, with little trading history to anchor price.
      prediction: Interval score below the constant band's 2.735, with coverage of the fastest_growing_20pct and highest_rnd_20pct groups near 80% instead of 66-70%.

  (2) ebitda_small_firm_information
      rule: EV/EBITDA | base constant | terms log_sales -1.2 | if loss_making AND log_sales <= p30 x1.4
      mechanism: Small firms have thin analyst coverage, illiquid shares and concentrated idiosyncratic risk, so their prices carry more noise and depart more from fundamentals that peers share. The effect is worst for small firms that also lose money, where speculative and retail trading drive the price and the gap from peer-implied value is largest.
      prediction: Interval score below the constant band's 2.735, with smallest_20pct coverage rising from 63% to about 80% and narrower ranges for large firms.

  (3) sales_margin_duration
      rule: EV/Sales | base constant | terms gross_margin +0.6, rnd_intensity +0.6, sales_growth_1y +0.4
      mechanism: EV/Sales assumes the target will turn sales into cash flow the way its peers do. For high-gross-margin, R&D-heavy, fast-growing businesses, the eventual operating margin is far off and highly uncertain, so sales multiples range widely even among close peers. Low-gross-margin, low-R&D, slow-growing firms have predictable conversion of sales to cash, and their sales multiples cluster tightly.
      prediction: Interval score below the constant band's 4.233, with highest_rnd_20pct and fastest_growing_20pct coverage near 80% and no over-widening of loss_making firms beyond about 85% coverage.

  (4) sales_small_firm_information
      rule: EV/Sales | base constant | terms log_sales -1 | if loss_making AND log_sales <= p30 x1.3
      mechanism: Small firms have thin analyst coverage and illiquid shares, so their market values carry more pricing noise than peer sales multiples can predict. The noise is largest for small firms that also lose money, where speculative trading rather than fundamentals sets the price.
      prediction: Interval score below the constant band's 4.233, with smallest_20pct coverage rising from 68% to about 80% and median range narrower than x/3.38.

  (5) sales_peer_comparability
      rule: EV/Sales | base constant | terms n_peers -1, peer_range +0.5
      mechanism: Sales multiples are only informative when peers share the target's business model and margin structure. When the 2-digit SIC sector is thin (few peers found) or the peers' multiples span a very wide range, the peer set mixes unlike businesses, so its median is a weak anchor for the target's value.
      prediction: Interval score below the constant band's 4.233, with fallback_or_few_peers coverage rising from 71% to about 80%.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}
