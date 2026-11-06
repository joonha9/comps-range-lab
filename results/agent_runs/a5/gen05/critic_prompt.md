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
  [g02-01] EV/EBITDA | base constant | terms ebitda_margin -1, roic -0.6 | if net_debt_to_ebitda >= p90 x1.3
  [g02-02] EV/EBITDA | base constant | terms sales_growth_1y +0.7, rnd_intensity +0.7 | if no_history x1.4
  [g02-03] EV/EBITDA | base constant | terms log_sales -1.2 | if loss_making AND log_sales <= p30 x1.4
  [g02-04] EV/Sales | base constant | terms gross_margin +0.6, rnd_intensity +0.6, sales_growth_1y +0.4
  [g02-05] EV/Sales | base constant | terms log_sales -1 | if loss_making AND log_sales <= p30 x1.3
  [g02-06] EV/Sales | base constant | terms n_peers -1, peer_range +0.5
  [g03-01] EV/EBITDA | base constant | terms ebitda_margin -0.7 | if sales_growth_1y <= p10 x1.4 | if sales_growth_1y >= p90 x1.4
  [g03-02] EV/EBITDA | base constant | terms capex_intensity +0.8, roic -0.6
  [g03-03] EV/EBITDA | base constant | terms gross_margin +0.5, rnd_intensity +0.6 | if ebitda_margin <= p20 AND gross_margin >= p60 x1.5
  [g03-04] EV/Sales | base constant | terms n_peers -0.7 | if ebitda_margin >= p90 x1.4 | if ebitda_margin <= p10 x1.3
  [g03-05] EV/Sales | base constant | terms debt_to_assets -0.8 | if loss_making AND debt_to_assets <= p30 x1.4
  [g03-06] EV/Sales | base constant | terms asset_turnover -0.8, capex_intensity +0.5
  [g04-01] EV/EBITDA | base constant | terms net_margin -1, ebitda_margin +0.5, capex_intensity +0.4
  [g04-02] EV/EBITDA | base constant | terms log_sales -1, peer_iqr +0.5 | if n_peers <= p10 x1.3
  [g04-03] EV/EBITDA | base constant | terms log_sales -0.9, debt_to_assets -0.6
  [g04-04] EV/Sales | base constant | terms gross_margin +0.6, ebitda_margin -0.4, n_peers -0.6
  [g04-05] EV/Sales | base constant | terms sales_growth_3y +0.4 | if sales_growth_1y >= p85 x1.4 | if sales_growth_1y <= p10 x1.3 | if no_history x1.3
  [g04-06] EV/Sales | base constant | terms log_sales -0.7, rnd_intensity +0.5 | if no_history x1.3

PROPOSALS
  (0) g05-01 small dollar EBITDA base
      rule: EV/EBITDA | base constant | terms log_sales -0.8, ebitda_margin -0.6 | if loss_making x1.3
      mechanism: The peer multiple is applied to a dollar amount of EBITDA, and the smaller that amount (a small firm with a thin margin), the larger the share of it made up of transitory items, one-off costs and fixed-cost swings, so the percentage error in the capitalized base is largest. Firms that lose money below EBITDA show that the EBITDA base overstates sustainable earnings, which makes the base less reliable still.
      prediction: Interval score below the constant band's (2.735) and below g03-01 (2.677), with loss_making and smallest_20pct coverage near 80%.

  (1) g05-02 value-driver mismatch
      rule: EV/EBITDA | base constant | terms log_sales -0.9 | if roic >= p90 x1.25 | if roic <= p10 x1.3 | if sales_growth_1y >= p90 x1.3
      mechanism: The justified EV/EBITDA multiple depends on three value drivers: growth, return on invested capital and risk (the discount rate). Peers are matched on size and EBITDA margin but not on growth or ROIC, so targets at the extremes of ROIC or growth are paired with peers whose value drivers differ, while small size stands in for risk: the discount rates of small firms vary much more from firm to firm.
      prediction: Interval score below the constant band's (2.735), with fastest_growing_20pct coverage rising toward 80% and smallest_20pct coverage near 80%.

  (2) g05-03 EV identity with distressed debt
      rule: EV/EBITDA | base constant | terms log_sales -0.8, debt_to_assets -0.5 | if loss_making AND net_debt_to_ebitda >= p80 x1.5
      mechanism: EV is market equity plus net debt measured at book value. Equity is the noisy, sentiment-driven part, so firms financed mostly by equity (especially small, thinly covered ones) have the noisiest EV. But for distressed firms (loss-making with very high net debt to EBITDA), book debt overstates the market value of the debt and the equity behaves like an option, so the EV measured with book debt drifts away from the peer-implied level.
      prediction: Interval score below the constant band's (2.735) and no worse than g04-03 (2.606), with loss_making coverage above g04-03's 71%.

  (3) g05-04 price noise plus anchor noise (sales)
      rule: EV/Sales | base constant | terms log_sales -0.5, n_peers -0.7, peer_range +0.4
      mechanism: A sales-comps error has two independent sources: noise in the target's own price and noise in the peer anchor. Small firms have thin analyst coverage and illiquid shares, so their prices drift further from fundamentals, while a thin sector (few peers) or peers whose multiples span a wide range make the median sales multiple an imprecise anchor; the two error sources add up.
      prediction: Interval score below g02-06 (4.164), with smallest_20pct coverage rising from 70% toward 78% while fallback_or_few_peers coverage stays above 80%.

  (4) g05-05 pre-commercial option value
      rule: EV/Sales | base constant | terms rnd_intensity +0.4 | if negative_ebitda AND log_sales <= p20 x1.6
      mechanism: For firms with tiny sales and negative EBITDA (typically R&D-driven pre-commercial companies), enterprise value is an option on a pipeline or technology, not a multiple of current sales, so the sales multiple is almost arbitrary and their actual EV can land far above or below the peer-implied level. R&D intensity measures how much of value rests on such unproven investment.
      prediction: Interval score below the constant band's (4.233), with highest_rnd_20pct and smallest_20pct coverage near 80% but not overcovered the way g01-04 was (about 90%).

  (5) g05-06 abnormal sales level times contribution margin
      rule: EV/Sales | base constant | terms gross_margin +0.5 | if sales_growth_1y <= p10 x1.4 | if sales_growth_1y >= p90 x1.3
      mechanism: EV/Sales assumes current sales is the normal level the market capitalizes, but after a sharp collapse or surge, current sales misstates the normalized level, so the peer multiple lands on the wrong base. In high-gross-margin (high contribution margin) businesses, each dollar of sales that is abnormal turns into more profit and value, so the same sales distortion produces a bigger valuation error.
      prediction: Interval score below the constant band's (4.233), with fastest_growing_20pct coverage near 80%.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}
