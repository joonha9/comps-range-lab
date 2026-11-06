You are a valuation researcher. Comparable-company valuations ("comps") are reported as ranges,
and practitioners' ranges are badly calibrated. Your job is to discover short, interpretable rules
that say HOW UNCERTAIN a comps valuation is for each US non-financial firm, so its range can be
wide where comps are unreliable and narrow where they are reliable.

TASK
Propose exactly 6 NEW range rules (generation 3): 3 for EV/EBITDA and 3 for EV/Sales.
Rules are scored only on exploration years FY2016-2019. The best rule per multiple will later be
tested ONCE on later years you will never see, so prefer rules with a clear economic reason over
fragile tweaks. A practitioner should be able to read your rule and apply it by hand.

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

BENCHMARKS (exploration years)
  EV/EBITDA:
    peer 25-75% range as practitioners report it (not calibrated): interval score 3.258, coverage 40.9%, median range x/1.29
    constant band (same width for every firm): interval score 2.735, coverage 79.6%, median range x/2.10
    width proportional to peer_iqr: interval score 2.732, coverage 80.0%, median range x/2.11
    linear regression on ALL inputs (no limit on terms): interval score 2.448, coverage 79.9%, median range x/1.94
    gradient-boosted trees on all inputs (black box): interval score 2.219, coverage 79.9%, median range x/1.90
    coverage of the constant band by firm type: loss_making 68%, smallest_20pct 63%, fastest_growing_20pct 70%, highest_rnd_20pct 66%, fallback_or_few_peers 83%
  EV/Sales:
    peer 25-75% range as practitioners report it (not calibrated): interval score 5.226, coverage 41.1%, median range x/1.59
    constant band (same width for every firm): interval score 4.233, coverage 80.0%, median range x/3.38
    width proportional to peer_iqr: interval score 4.340, coverage 80.0%, median range x/3.56
    linear regression on ALL inputs (no limit on terms): interval score 3.970, coverage 80.0%, median range x/3.23
    gradient-boosted trees on all inputs (black box): interval score 3.483, coverage 80.1%, median range x/2.86
    coverage of the constant band by firm type: loss_making 72%, smallest_20pct 68%, fastest_growing_20pct 75%, highest_rnd_20pct 72%, fallback_or_few_peers 71%

ARCHIVE: your earlier graded attempts, exploration scores only (5 graded)
  [g01-01] EV/EBITDA interval score 2.591 | coverage 80.0% | median range x/2.03
      EV/EBITDA | base constant | terms log_sales -1, rnd_intensity +0.6, sales_growth_1y +0.4 | if loss_making x1.4
      by firm type: loss_making 80%, smallest_20pct 81%, fastest_growing_20pct 81%, highest_rnd_20pct 83%, fallback_or_few_peers 73%
      mechanism: Small firms and R&D-heavy firms derive much of their value from intangible growth options that current EBITDA does not capture, so the peer EBITDA multiple is a poor anchor; their thin analyst coverage and illiquidity add pricing noise. Loss-making firms with positive EBITDA have earnings that are transitory or burdened by below-EBITDA charges, making the EBITDA base itself unreliable.
  [g02-03] EV/EBITDA interval score 2.634 | coverage 79.6% | median range x/2.04
      EV/EBITDA | base constant | terms log_sales -1.2 | if loss_making AND log_sales <= p30 x1.4
      by firm type: loss_making 76%, smallest_20pct 82%, fastest_growing_20pct 75%, highest_rnd_20pct 73%, fallback_or_few_peers 77%
      mechanism: Small firms have thin analyst coverage, illiquid shares and concentrated idiosyncratic risk, so their prices carry more noise and depart more from fundamentals that peers share. The effect is worst for small firms that also lose money, where speculative and retail trading drive the price and the gap from peer-implied value is largest.
  [g02-02] EV/EBITDA interval score 2.669 | coverage 79.8% | median range x/2.08
      EV/EBITDA | base constant | terms sales_growth_1y +0.7, rnd_intensity +0.7 | if no_history x1.4
      by firm type: loss_making 68%, smallest_20pct 68%, fastest_growing_20pct 81%, highest_rnd_20pct 79%, fallback_or_few_peers 78%
      mechanism: For fast-growing, R&D-intensive and newly listed firms, most of enterprise value comes from growth options that current EBITDA does not capture, and how the market values those options differs a lot from firm to firm; a peer-median EBITDA multiple cannot price them. Recent listings (no prior-year sales) are the purest version of this: young firms valued on their future, with little trading history to anchor price.
  [g02-06] EV/Sales interval score 4.164 | coverage 79.8% | median range x/3.32
      EV/Sales | base constant | terms n_peers -1, peer_range +0.5
      by firm type: loss_making 73%, smallest_20pct 70%, fastest_growing_20pct 76%, highest_rnd_20pct 74%, fallback_or_few_peers 89%
      mechanism: Sales multiples are only informative when peers share the target's business model and margin structure. When the 2-digit SIC sector is thin (few peers found) or the peers' multiples span a very wide range, the peer set mixes unlike businesses, so its median is a weak anchor for the target's value.
  [g01-04] EV/Sales interval score 4.556 | coverage 79.9% | median range x/2.91
      EV/Sales | base constant | terms ebitda_margin -1, log_sales -0.8 | if negative_ebitda x1.6 | if loss_making x1.2
      by firm type: loss_making 91%, smallest_20pct 90%, fastest_growing_20pct 81%, highest_rnd_20pct 89%, fallback_or_few_peers 73%
      mechanism: EV/Sales implicitly assumes the target converts sales into cash flow like its peers; firms with low or negative EBITDA margins are valued on a turnaround or option value that sales alone cannot reveal, so their actual EV can sit far above or below the peer-implied level. Small firms add illiquidity and coverage noise on top.

FAILED OR REJECTED ATTEMPTS (most recent)
  [g01-02] rejected: critic: The small-denominator and leverage story justifies ebitda_margin, roic and the net_debt_to_ebitda condition, but the log_assets -0.7 term (larger than the roic weight) is never motivated by the mechanism, so a wi
  [g01-03] rejected: critic: The rule bundles four separate ideas (gross margin, growth, peer disagreement, no history) plus a log_sales -0.6 size term that the mechanism never mentions, so it does not implement one specific mechanism; justi
  [g01-05] rejected: critic: The margin-duration story for EV/Sales supports gross_margin, rnd_intensity and growth, but the log_sales -0.6 term is not part of the stated mechanism (which is about business model, not size), so the rule does 
  [g01-06] rejected: critic: The mechanism invokes very high asset turnover, but the rule has no asset_turnover input, while the sales_growth_1y +0.5 term it does include is never explained, so the rule does not implement the stated mechanis
  [g02-01] rejected: critic: This is g01-02 with log_assets dropped and the two margin/return weights nudged, keeping the same net_debt_to_ebitda p90 x1.3 condition, so it adds no new input, condition or economic idea; test the depressed-EBI
  [g02-04] rejected: critic: This is g01-05 with log_sales dropped and every weight scaled down by about a quarter, which is trivial because the ranking it produces is almost the same; to test margin duration, add a new input such as ebit_ma
  [g02-05] rejected: critic: This repeats g01-06: log_sales and log_assets measure size almost the same way, the condition is the same small-and-loss-making one with a slightly different multiplier, and dropping the growth term adds no new i

Each proposal needs:
  - "mechanism": the economic reason these firms' market values are harder (or easier) to pin
    down with comps (2-3 sentences)
  - "prediction": a falsifiable expectation, e.g. "interval score below the constant band's"
  - "rule": the rule object
An independent referee, who sees your mechanism but no scores, will reject proposals without a
specific economic reason, or near-copies of earlier rules (e.g. one weight changed slightly).

Reply with ONLY this JSON, no other text:
{"proposals": [{"name": "...", "mechanism": "...", "prediction": "...",
  "rule": {"multiple": "...", "base": "...", "terms": {...}, "conditions": [...]}}]}
