You are a valuation researcher. Comparable-company valuations ("comps") are reported as ranges,
and practitioners' ranges are badly calibrated. Your job is to discover short, interpretable rules
that say HOW UNCERTAIN a comps valuation is for each US non-financial firm, so its range can be
wide where comps are unreliable and narrow where they are reliable.

TASK
Propose exactly 6 NEW range rules (generation 2): 3 for EV/EBITDA and 3 for EV/Sales.
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

ARCHIVE: your earlier graded attempts, exploration scores only (4 graded)
  [g01-01] EV/EBITDA interval score 2.590 | coverage 79.6% | median range x/2.03
      EV/EBITDA | base constant | terms log_sales -1, ebitda_margin -1 | if loss_making x1.5
      by firm type: loss_making 86%, smallest_20pct 78%, fastest_growing_20pct 71%, highest_rnd_20pct 71%, fallback_or_few_peers 76%
      mechanism: When a firm is small and its EBITDA margin is thin, current EBITDA is a noisy, partly transitory proxy for normalized cash earnings: a small absolute change in costs swings EBITDA by a large percentage, so EV/EBITDA applied to it misprices value. Small firms also carry more idiosyncratic risk (liquidity, key-customer, survival) that peers' multiples do not reflect, and net losses signal that below-EBITDA items are eroding equity value.
  [g01-02] EV/EBITDA interval score 2.636 | coverage 79.6% | median range x/2.00
      EV/EBITDA | base constant | terms rnd_intensity +0.8, sales_growth_1y +0.6, log_assets -0.8 | if gross_margin >= p70 AND sales_growth_1y >= p70 x1.3
      by firm type: loss_making 68%, smallest_20pct 77%, fastest_growing_20pct 85%, highest_rnd_20pct 85%, fallback_or_few_peers 75%
      mechanism: For R&D-intensive, fast-growing firms much of enterprise value is a claim on future growth options rather than on current EBITDA, and the market prices those options very differently across firms in the same SIC code. Current EBITDA is also depressed by expensed R&D, so a peer-median multiple on it is a weak anchor; large asset bases indicate mature, tangible businesses whose EBITDA capitalizes reliably.
  [g01-04] EV/Sales interval score 4.452 | coverage 80.0% | median range x/2.96
      EV/Sales | base constant | terms log_sales -1, ebitda_margin -0.8 | if negative_ebitda x1.6 | if no_history x1.3
      by firm type: loss_making 88%, smallest_20pct 92%, fastest_growing_20pct 81%, highest_rnd_20pct 89%, fallback_or_few_peers 75%
      mechanism: EV/Sales implicitly assumes the target will convert sales to cash like its peers; for small firms with low or negative EBITDA margins that conversion is highly uncertain, so the market's valuation hinges on a turnaround or growth story that peers' multiples cannot capture. Firms with no sales history are new listings or entrants whose business model the market is still pricing with little track record.
  [g01-05] EV/Sales interval score 4.706 | coverage 80.0% | median range x/3.24
      EV/Sales | base constant | terms rnd_intensity +1, gross_margin +0.6, sales_growth_1y +0.6, log_assets -0.8
      by firm type: loss_making 79%, smallest_20pct 83%, fastest_growing_20pct 89%, highest_rnd_20pct 94%, fallback_or_few_peers 65%
      mechanism: High gross margin, R&D-intensive, fast-growing firms (software, biotech, devices) are valued on the expected scale and durability of future margins, so revenue multiples within the same SIC code span an order of magnitude depending on market beliefs about each firm's franchise. Mature, asset-heavy firms with low gross margins have revenue that maps to value through a narrow, competitive margin band, making EV/Sales reliable for them.

FAILED OR REJECTED ATTEMPTS (most recent)
  [g01-03] rejected: critic: It bundles three loosely related ideas (leverage, capex/D&A gap, peer disagreement) and adds a large log_sales -0.8 term that the mechanism never motivates, so a result could not be attributed to any stated mecha
  [g01-06] rejected: critic: The mechanism says thin, competitive margins give a tight EV/Sales band, but net_margin -0.5 widens ranges for thin-margin firms, and the large log_sales -0.9 term is not motivated at all; make every sign follow 

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
