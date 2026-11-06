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
  (0) ebitda_small_thin_margin
      rule: EV/EBITDA | base constant | terms log_sales -1, ebitda_margin -1 | if loss_making x1.5
      mechanism: When a firm is small and its EBITDA margin is thin, current EBITDA is a noisy, partly transitory proxy for normalized cash earnings: a small absolute change in costs swings EBITDA by a large percentage, so EV/EBITDA applied to it misprices value. Small firms also carry more idiosyncratic risk (liquidity, key-customer, survival) that peers' multiples do not reflect, and net losses signal that below-EBITDA items are eroding equity value.
      prediction: Interval score below the constant band's 2.735 on EV/EBITDA, with coverage of the smallest-20% and loss-making groups rising toward 80%.

  (1) ebitda_growth_options
      rule: EV/EBITDA | base constant | terms rnd_intensity +0.8, sales_growth_1y +0.6, log_assets -0.8 | if gross_margin >= p70 AND sales_growth_1y >= p70 x1.3
      mechanism: For R&D-intensive, fast-growing firms much of enterprise value is a claim on future growth options rather than on current EBITDA, and the market prices those options very differently across firms in the same SIC code. Current EBITDA is also depressed by expensed R&D, so a peer-median multiple on it is a weak anchor; large asset bases indicate mature, tangible businesses whose EBITDA capitalizes reliably.
      prediction: Interval score below the constant band's 2.735 on EV/EBITDA, with coverage of the highest-R&D-20% and fastest-growing-20% groups closer to 80% than the constant band's 66% and 70%.

  (2) ebitda_leverage_and_da_gap
      rule: EV/EBITDA | base constant | terms net_debt_to_ebitda +0.6, capex_intensity +0.5, log_sales -0.8, peer_range +0.4 | if net_debt_to_ebitda >= p90 x1.4
      mechanism: Highly levered firms have enterprise values whose equity slice behaves like an option on asset value, so small differences in perceived distress risk move EV far from peer-implied levels; capital-intensive firms have a large gap between EBITDA and cash earnings (heavy D&A and maintenance capex) that the market treats differently across firms. Peer disagreement (peer range) adds the remaining information that the industry itself has no stable valuation anchor.
      prediction: Interval score below the constant band's 2.735 and below the peer_iqr-proportional benchmark's 2.732 on EV/EBITDA.

  (3) sales_unprofitable_small
      rule: EV/Sales | base constant | terms log_sales -1, ebitda_margin -0.8 | if negative_ebitda x1.6 | if no_history x1.3
      mechanism: EV/Sales implicitly assumes the target will convert sales to cash like its peers; for small firms with low or negative EBITDA margins that conversion is highly uncertain, so the market's valuation hinges on a turnaround or growth story that peers' multiples cannot capture. Firms with no sales history are new listings or entrants whose business model the market is still pricing with little track record.
      prediction: Interval score below the constant band's 4.233 on EV/Sales, with the loss-making and smallest-20% groups' coverage rising toward 80%.

  (4) sales_intangible_growth
      rule: EV/Sales | base constant | terms rnd_intensity +1, gross_margin +0.6, sales_growth_1y +0.6, log_assets -0.8
      mechanism: High gross margin, R&D-intensive, fast-growing firms (software, biotech, devices) are valued on the expected scale and durability of future margins, so revenue multiples within the same SIC code span an order of magnitude depending on market beliefs about each firm's franchise. Mature, asset-heavy firms with low gross margins have revenue that maps to value through a narrow, competitive margin band, making EV/Sales reliable for them.
      prediction: Interval score below the constant band's 4.233 on EV/Sales, and narrower median range for low-gross-margin firms than for high-gross-margin firms.

  (5) sales_asset_light_story_stocks
      rule: EV/Sales | base constant | terms asset_turnover -0.7, log_sales -0.9, net_margin -0.5 | if loss_making AND sales_growth_1y >= p80 x1.5
      mechanism: Low asset turnover means each dollar of sales is backed by heavy (often intangible or long-lived) assets, so value depends on asset returns that differ widely across firms with similar revenue; high-turnover firms such as distributors and retailers trade in a tight EV/Sales band set by thin, competitive margins. Loss-making firms that are also growing fast are priced on narratives about future profitability, the case where a sales multiple is least informative.
      prediction: Interval score below the constant band's 4.233 on EV/Sales, with coverage of the fastest-growing-20% group near 80%.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}
