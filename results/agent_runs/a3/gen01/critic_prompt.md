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
  (0) ebitda_thin_margin_small_firm
      rule: EV/EBITDA | base constant | terms log_sales -1, ebitda_margin -1 | if loss_making x1.4
      mechanism: When EBITDA is a thin slice of sales, small absolute errors or transitory swings in EBITDA move the EV/EBITDA ratio a lot, and the market prices such firms on normalized rather than reported EBITDA, so peer medians transfer poorly. Small firms add idiosyncratic business risk, illiquidity and sparse analyst coverage, so their values deviate more from sector medians; loss-making firms have reported EBITDA that is unlikely to persist.
      prediction: EV/EBITDA interval score below the constant band's 2.735, with coverage of loss_making and smallest_20pct firms rising toward 80% while median range width falls below x/2.10.

  (1) ebitda_intangible_growth_option_value
      rule: EV/EBITDA | base constant | terms rnd_intensity +0.8, sales_growth_1y +0.6, gross_margin +0.5, log_assets -0.6 | if no_history x1.3
      mechanism: Firms with heavy R&D, high gross margins and fast sales growth derive much of their value from growth options and intangible assets that current EBITDA does not capture, so investors' valuations of them diverge widely from the peer median multiple. Firms with no sales history (recent listings) have the least information for the market and the analyst to anchor on.
      prediction: EV/EBITDA interval score below the constant band's 2.735, with highest_rnd_20pct and fastest_growing_20pct coverage closer to 80% than the constant band's 66% and 70%.

  (2) ebitda_leverage_distress
      rule: EV/EBITDA | base constant | terms net_debt_to_ebitda +0.6, log_sales -0.8 | if debt_to_assets >= p80 AND loss_making x1.5 | if peer_iqr >= p80 x1.3
      mechanism: For highly levered, distressed firms the enterprise value is driven by the option-like value of equity and by debt trading below book, so EV relative to EBITDA departs from healthy peers' multiples in either direction. Where the peers themselves disagree strongly on the multiple, the sector has no single valuation anchor and the median estimate is less reliable.
      prediction: EV/EBITDA interval score below the constant band's 2.735, and wider ranges (above median width) for firms in the top quintile of net_debt_to_ebitda.

  (3) sales_unprofitable_option_value
      rule: EV/Sales | base constant | terms log_sales -1, rnd_intensity +0.7 | if negative_ebitda x1.8 | if loss_making x1.2
      mechanism: Firms with non-positive EBITDA are valued on the hope of future profits rather than on current sales economics, so the same revenue can be worth very different amounts and a peer EV/Sales median is a weak anchor. Small size and heavy R&D compound this, since value then rests on unproven products and a few idiosyncratic outcomes.
      prediction: EV/Sales interval score below the constant band's 4.233, with coverage of loss_making firms above the constant band's 72% and of smallest_20pct above 68%.

  (4) sales_margin_scalability
      rule: EV/Sales | base constant | terms gross_margin +0.8, sales_growth_1y +0.6, log_assets -0.8 | if loss_making AND rnd_intensity >= p80 x1.5
      mechanism: EV/Sales implicitly assumes the target converts sales to cash like its peers; high-gross-margin, fast-growing firms have scalable economics whose eventual profitability is uncertain, so their sales multiples spread out much more than those of low-margin, mature firms where sales map tightly to value. Small asset bases mean little tangible value to anchor EV.
      prediction: EV/Sales interval score below the constant band's 4.233, with median range narrower than x/3.38 because mature low-gross-margin firms get tight ranges.

  (5) sales_peer_disagreement_weak_anchor
      rule: EV/Sales | base constant | terms peer_range +0.6, log_sales -0.7 | if ebitda_margin <= p15 x1.6 | if no_history x1.3
      mechanism: When the peers' EV/Sales multiples span a wide range the sector contains firms with very different margin structures, so the median peer is a weak anchor; using peer spread as a moderating term rather than the full base avoids letting noisy peer statistics dominate. Firms with depressed EBITDA margins or no sales history lack a stable earnings base that would tie their value to their revenue.
      prediction: EV/Sales interval score below both the constant band's 4.233 and the peer_iqr-proportional band's 4.340.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}
