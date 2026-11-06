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

PROPOSALS
  (0) g03-01 transitory EBITDA after sales shocks
      rule: EV/EBITDA | base constant | terms ebitda_margin -0.7 | if sales_growth_1y <= p10 x1.4 | if sales_growth_1y >= p90 x1.4
      mechanism: When sales have just swung sharply in either direction, current-year EBITDA is a poor proxy for the normalized earnings the market capitalizes, so applying a peer EBITDA multiple to it misprices the firm. The distortion is largest for thin-margin firms, whose EBITDA moves most for a given sales shock because of operating leverage.
      prediction: Interval score below the constant band's 2.735, with coverage of the fastest_growing_20pct group rising from 70% to at least 78%.

  (1) g03-02 EBITDA-to-cash conversion
      rule: EV/EBITDA | base constant | terms capex_intensity +0.8, roic -0.6
      mechanism: EV/EBITDA assumes the target turns EBITDA into free cash flow and value at the same rate as its peers. Firms that must reinvest heavily (high capex relative to sales) or earn low returns on capital keep much less of each EBITDA dollar, and how much less differs a lot from firm to firm, so the peer multiple is a weak anchor for them.
      prediction: Interval score below the constant band's 2.735; firms in the top capex-intensity quintile have wider ranges and coverage near 80%.

  (2) g03-03 expensed intangible investment
      rule: EV/EBITDA | base constant | terms gross_margin +0.5, rnd_intensity +0.6 | if ebitda_margin <= p20 AND gross_margin >= p60 x1.5
      mechanism: High-gross-margin firms that spend their gross profit on R&D and other expensed investment report EBITDA that understates their economic earnings, because spending that builds intangible assets is charged against EBITDA. The firms with the strongest version of this (high gross margin but very low EBITDA margin) have a depressed and unstable denominator, so their EBITDA multiple is hardest to predict from peers.
      prediction: Interval score below the constant band's 2.735, with highest_rnd_20pct coverage rising from 66% to at least 76%.

  (3) g03-04 peer match quality at the margin tails
      rule: EV/Sales | base constant | terms n_peers -0.7 | if ebitda_margin >= p90 x1.4 | if ebitda_margin <= p10 x1.3
      mechanism: Peers are picked as nearest on size and EBITDA margin within the 2-digit SIC, and EV/Sales scales almost directly with margin. Targets at either extreme of the margin distribution, and targets in thin sectors, have nearest peers that are far from them in margin and business model, so the peer-median sales multiple is a poor anchor for them.
      prediction: Interval score below both the constant band's 4.233 and g02-06's 4.164.

  (4) g03-05 debt anchor in enterprise value
      rule: EV/Sales | base constant | terms debt_to_assets -0.8 | if loss_making AND debt_to_assets <= p30 x1.4
      mechanism: Enterprise value is equity plus net debt, and the debt part trades close to book value, so firms financed mostly by debt have EVs that move less with equity sentiment and stay closer to the peer-implied level. Loss-making firms financed almost entirely by equity are the opposite case: their whole EV is a market-priced option on future profits, which sales alone cannot pin down.
      prediction: Interval score below the constant band's 4.233, with loss_making coverage rising from 72% to at least 78%.

  (5) g03-06 capital intensity ignored by sales
      rule: EV/Sales | base constant | terms asset_turnover -0.8, capex_intensity +0.5
      mechanism: In asset-heavy businesses, enterprise value reflects the capital base and the return earned on it more than the level of sales, so EV/Sales varies with asset intensity. Peers are matched on size and margin but not on asset intensity, so firms that need a lot of assets or capex per dollar of sales get a peer sales multiple that is poorly matched.
      prediction: Interval score below the constant band's 4.233; firms in the bottom asset-turnover quintile have wider ranges than average and coverage near 80%.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}
