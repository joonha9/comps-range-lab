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
  [g01-01] EV/EBITDA | base constant | terms log_sales -1, ebitda_margin -1 | if loss_making x1.5
  [g01-02] EV/EBITDA | base constant | terms rnd_intensity +0.8, sales_growth_1y +0.6, log_assets -0.8 | if gross_margin >= p70 AND sales_growth_1y >= p70 x1.3
  [g01-03] EV/EBITDA | base constant | terms net_debt_to_ebitda +0.6, capex_intensity +0.5, log_sales -0.8, peer_range +0.4 | if net_debt_to_ebitda >= p90 x1.4
  [g01-04] EV/Sales | base constant | terms log_sales -1, ebitda_margin -0.8 | if negative_ebitda x1.6 | if no_history x1.3
  [g01-05] EV/Sales | base constant | terms rnd_intensity +1, gross_margin +0.6, sales_growth_1y +0.6, log_assets -0.8
  [g01-06] EV/Sales | base constant | terms asset_turnover -0.7, log_sales -0.9, net_margin -0.5 | if loss_making AND sales_growth_1y >= p80 x1.5
  [g02-01] EV/EBITDA | base constant | terms capex_intensity +0.7, ebitda_margin -0.7 | if loss_making x1.3
  [g02-02] EV/EBITDA | base constant | terms log_assets -0.7 | if sales_growth_1y >= p80 x1.4 | if sales_growth_1y <= p10 x1.3 | if no_history x1.3
  [g02-03] EV/EBITDA | base constant | terms debt_to_assets -0.7, log_sales -0.7 | if loss_making AND debt_to_assets <= p50 x1.4
  [g02-04] EV/Sales | base constant | terms debt_to_assets -0.6, ebitda_margin -0.5 | if negative_ebitda x1.3
  [g02-05] EV/Sales | base constant | terms gross_margin +0.5 | if sales_growth_1y >= p80 x1.5 | if sales_growth_1y <= p15 x1.3 | if no_history x1.3
  [g02-06] EV/Sales | base constant | terms peer_range +0.4, n_peers -0.6, log_sales -0.5
  [g03-01] EV/EBITDA | base constant | terms net_debt_to_ebitda -0.8, log_sales -0.6 | if net_debt_to_ebitda <= p10 x1.3 | if loss_making x1.3
  [g03-02] EV/EBITDA | base constant | terms ebitda_margin -0.7, log_assets -0.6 | if sales_growth_1y >= p85 x1.3 | if sales_growth_1y <= p10 x1.3
  [g03-03] EV/EBITDA | base constant | terms gross_margin +0.5, ebitda_margin -0.6, log_sales -0.5 | if gross_margin >= p70 AND ebitda_margin <= p30 x1.3
  [g03-04] EV/Sales | base constant | terms debt_to_assets -0.6, log_sales -0.4 | if debt_to_assets <= p25 AND rnd_intensity >= p70 x1.3 | if negative_ebitda x1.3
  [g03-05] EV/Sales | base constant | terms n_peers -0.5, log_sales -0.5 | if ebitda_margin <= p10 x1.4 | if ebitda_margin >= p90 x1.2
  [g03-06] EV/Sales | base constant | terms log_sales -0.5 | if loss_making AND sales_growth_1y >= p70 x1.5 | if negative_ebitda x1.2

PROPOSALS
  (0) ebitda_roic_extremes_debt_anchor
      rule: EV/EBITDA | base constant | terms net_debt_to_ebitda -0.7 | if roic >= p85 x1.3 | if roic <= p15 x1.4
      mechanism: By the value-driver identity, EV/NOPAT = (1 - g/ROIC)/(WACC - g), so the multiple's sensitivity to growth beliefs rises steeply with return on capital: for very high-ROIC firms the multiple depends on how long that franchise lasts, which the market judges firm by firm and peers cannot reveal. Very low-ROIC firms earn little on their capital, so their EV is anchored to asset or restructuring value rather than to EBITDA, and a capitalized-EBITDA estimate misses it. Net debt, read off the balance sheet near book, is the known part of EV, so more of it relative to EBITDA leaves less to estimate.
      prediction: EV/EBITDA interval score below the constant band's 2.735, with coverage of the top and bottom ROIC deciles under the constant band below 80% and closer to 80% under this rule.

  (1) ebitda_tangible_asset_anchor
      rule: EV/EBITDA | base constant | terms asset_turnover +0.6, debt_to_assets -0.5 | if gross_margin >= p70 AND asset_turnover >= p70 x1.3
      mechanism: When EBITDA comes from a large base of tangible assets (low sales-to-assets), EV is held close to the replacement cost of those assets and much of it is funded by collateralized debt priced near book, so peers in the same industry trade in a tight multiple band. Asset-light firms with high gross margins earn EBITDA on unrecorded intangibles (brands, software, customer relationships) whose durability the market prices very differently across firms, so their EV/EBITDA strays furthest from the peer median.
      prediction: EV/EBITDA interval score below the constant band's 2.735; the asset-light high-gross-margin group should get ranges wider than the median range while low-turnover, debt-funded firms get narrower ones.

  (2) ebitda_residual_claim_magnification
      rule: EV/EBITDA | base constant | terms ebit_margin -0.6 | if net_debt_to_ebitda <= p15 AND log_sales <= p40 x1.6 | if net_debt_to_ebitda >= p75 x0.75
      mechanism: Comps errors are largest when EV is a small leftover of two large quantities. A small firm holding a lot of net cash has EV = equity minus cash, a difference that turns a modest equity mispricing into a large percentage EV error. A thin EBIT margin is the same thing for operations: value is a small leftover of revenue minus costs, so small differences in cost beliefs move value a lot. A firm with heavy net debt works the opposite way, because most of its EV is a book-valued claim.
      prediction: EV/EBITDA interval score below the constant band's 2.735, with the small net-cash group's coverage under the constant band below 70% and close to 80% under this rule.

  (3) sales_gross_vs_ebitda_margin_mismatch
      rule: EV/Sales | base constant | terms gross_margin +0.6, ebitda_margin -0.5 | if gross_margin >= p70 AND ebitda_margin <= p30 x1.3 | if negative_ebitda x1.3
      mechanism: A revenue multiple prices the long-run margin a firm's sales will reach, and gross margin caps that margin: a high-gross-margin firm whose EBITDA margin is low because it spends heavily on sales and R&D could earn far more at maturity. Peers are matched on current EBITDA margin rather than gross margin, so such a target is paired with low-gross-margin firms that have similar current EBITDA but much lower potential margins, a systematically mismatched EV/Sales anchor. Negative EBITDA is the extreme case where value rests entirely on future margins.
      prediction: EV/Sales interval score below the constant band's 4.233; the high-gross/low-EBITDA-margin group should get ranges wider than the median range and coverage near 80%.

  (4) sales_balance_sheet_anchor_turnover
      rule: EV/Sales | base constant | terms debt_to_assets -0.5 | if asset_turnover <= p15 x1.4 | if asset_turnover >= p85 x1.25
      mechanism: In logs, EV/Sales = EV/Assets minus Sales/Assets, and EV relative to the asset base is the more stable quantity because assets set replacement cost and debt is priced near book. Peers are matched on size and EBITDA margin but not on capital intensity, so a target whose asset turnover is extreme (very asset-heavy or very asset-light) is paired with peers of ordinary turnover, and the peer revenue multiple is biased by the turnover gap. Debt-heavy firms have more of their EV in a book-valued claim, which damps the error.
      prediction: EV/Sales interval score below the constant band's 4.233, with the bottom-15% and top-15% asset-turnover groups' constant-band coverage below 80% and closer to 80% under this rule.

  (5) sales_growth_times_returns
      rule: EV/Sales | base constant | terms sales_growth_1y +0.4 | if sales_growth_1y >= p70 AND roic >= p70 x1.4 | if roic <= p10 x1.3
      mechanism: By the value-driver identity, EV/Sales = NOPAT margin x (1 - g/ROIC)/(WACC - g), so growth adds value only when ROIC exceeds the cost of capital, and then the multiple becomes very sensitive to beliefs about how long the growth lasts. Peers are matched on EBITDA margin but not on growth or returns, so a fast-growing high-ROIC target's revenue multiple can be far from the peer median in a firm-specific way. Firms with very low ROIC destroy value as they grow, so their EV rests on restructuring or liquidation value that revenue multiples do not track.
      prediction: EV/Sales interval score below the constant band's 4.233, and below g02-05 (4.250), which used growth alone, showing that growth matters mainly through its interaction with returns.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}
