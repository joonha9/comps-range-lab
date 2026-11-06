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

ARCHIVE: your earlier graded attempts, exploration scores only (6 graded)
  [g01-01] EV/EBITDA interval score 2.571 | coverage 79.8% | median range x/2.05
      EV/EBITDA | base constant | terms log_sales -1, ebitda_margin -0.8 | if loss_making x1.4
      by firm type: loss_making 83%, smallest_20pct 78%, fastest_growing_20pct 72%, highest_rnd_20pct 71%, fallback_or_few_peers 75%
      mechanism: When EBITDA is a small slice of sales, a given dollar shock to costs moves EBITDA by a large percentage, so the market prices the firm off normalized rather than current EBITDA and the trailing multiple is noisy. Small firms add idiosyncratic risk, illiquidity and thin analyst coverage, so peers' multiples transfer poorly; loss-making firms with positive EBITDA have earnings below the line (interest, D&A, write-offs) that the multiple ignores.
  [g01-02] EV/EBITDA interval score 2.606 | coverage 79.6% | median range x/2.01
      EV/EBITDA | base constant | terms rnd_intensity +0.8, sales_growth_1y +0.6, log_assets -0.7 | if no_history x1.5
      by firm type: loss_making 69%, smallest_20pct 77%, fastest_growing_20pct 81%, highest_rnd_20pct 83%, fallback_or_few_peers 75%
      mechanism: Firms that expense heavy R&D and grow fast have current EBITDA depressed by investment that is really capital spending, so their EV reflects growth options that trailing EBITDA cannot capture and that differ greatly from peer to peer. Recently listed or newly covered firms (no prior-year sales) have short track records, so investors disagree more about their steady-state earnings.
  [g01-03] EV/EBITDA interval score 2.661 | coverage 79.9% | median range x/2.07
      EV/EBITDA | base constant | terms roic -0.8, log_sales -0.8 | if ebitda_margin <= p20 x1.4 | if debt_to_assets >= p80 AND ebit_margin <= p30 x1.3
      by firm type: loss_making 82%, smallest_20pct 77%, fastest_growing_20pct 73%, highest_rnd_20pct 70%, fallback_or_few_peers 81%
      mechanism: Firms earning low returns on invested capital are valued closer to their asset base or liquidation and restructuring outcomes than to a going-concern multiple of EBITDA, so earnings-based comps describe them poorly. Highly levered firms with thin margins carry distress and refinancing risk, and that risk moves the debt and equity parts of EV in ways the peers do not share.
  [g01-04] EV/Sales interval score 4.447 | coverage 79.9% | median range x/2.93
      EV/Sales | base constant | terms ebitda_margin -1, log_sales -0.8 | if negative_ebitda x1.6 | if no_history x1.3
      by firm type: loss_making 88%, smallest_20pct 90%, fastest_growing_20pct 80%, highest_rnd_20pct 89%, fallback_or_few_peers 74%
      mechanism: EV/Sales is essentially a margin times an earnings multiple, so it transfers across firms only when they have similar margins; when a firm's EBITDA margin is low or negative, its value rests on the market's guess of future margins rather than current economics, and that guess varies widely. Small firms add idiosyncratic and liquidity noise on top of this.
  [g01-06] EV/Sales interval score 4.469 | coverage 79.9% | median range x/3.21
      EV/Sales | base constant | terms log_sales -1, peer_iqr +0.5, net_margin -0.6 | if loss_making AND log_sales <= p30 x1.5 | if debt_to_assets >= p80 x1.3
      by firm type: loss_making 88%, smallest_20pct 91%, fastest_growing_20pct 80%, highest_rnd_20pct 87%, fallback_or_few_peers 73%
      mechanism: Small, loss-making firms with heavy debt have option-like equity whose value depends on survival rather than on revenue, so EV/Sales drawn from healthier peers misprices them in either direction. Where peers themselves disagree strongly, the sector holds several business models, and the median multiple is a less reliable anchor; this enters as a moderate term rather than the base because a pure peer_iqr scaling overweights it.
  [g01-05] EV/Sales interval score 4.649 | coverage 79.9% | median range x/3.32
      EV/Sales | base constant | terms gross_margin +0.8, rnd_intensity +0.7, sales_growth_1y +0.7, log_assets -0.6
      by firm type: loss_making 77%, smallest_20pct 80%, fastest_growing_20pct 90%, highest_rnd_20pct 92%, fallback_or_few_peers 66%
      mechanism: High gross margin, R&D-intensive, fast-growing firms (software and biotech style) are valued on scalable future margins, so their revenue multiples spread over an order of magnitude even within a 2-digit SIC code, and a peer median is a weak anchor. Low-gross-margin, slow-growing distributors and manufacturers trade in narrow revenue-multiple bands set by their thin, stable margins.

FAILED OR REJECTED ATTEMPTS (most recent)
  (none)

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
