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

PROPOSALS
  (0) ebitda_to_net_income_wedge
      rule: EV/EBITDA | base constant | terms net_margin -1, ebitda_margin +0.5, capex_intensity +0.4
      mechanism: EV/EBITDA treats EBITDA as the earnings the market capitalizes, but when a large wedge separates EBITDA from net income (heavy depreciation from capital intensity, interest, impairments, restructuring), EBITDA overstates what owners keep by an amount that differs a lot from firm to firm. Firms with healthy EBITDA margins but thin or negative net margins, and high capex per dollar of sales, are exactly where the peer EBITDA multiple is applied to an inflated and non-comparable base.
      prediction: Interval score below the constant band's 2.735 for EV/EBITDA, with coverage of loss_making firms rising from 68% toward 75% or more.

  (1) firm_noise_plus_anchor_noise
      rule: EV/EBITDA | base constant | terms log_sales -1, peer_iqr +0.5 | if n_peers <= p10 x1.3
      mechanism: A comps error has two sources: noise in the target's own price and noise in the peer anchor. Small firms have thin analyst coverage and illiquid shares, so their prices drift further from fundamentals; when the peers themselves disagree (wide peer IQR) or the sector is thin, the median multiple is an imprecise anchor, so the error from both sources adds up.
      prediction: Interval score below the constant band's 2.735 and below a size-only rule, with smallest_20pct coverage near 80% and fallback_or_few_peers coverage not falling below 78%.

  (2) equity_share_of_ev_times_equity_noise
      rule: EV/EBITDA | base constant | terms log_sales -0.9, debt_to_assets -0.6
      mechanism: Enterprise value is equity plus net debt, and debt trades close to book value, so only the equity part of EV carries market pricing noise. The EV of a debt-financed firm is partly pinned down by its balance sheet, while an equity-financed firm's whole EV moves with sentiment; that equity noise is largest for small, thinly covered firms, so uncertainty is highest for small firms with little debt.
      prediction: Interval score below the constant band's 2.735 for EV/EBITDA; low-debt small firms get the widest ranges and high-leverage large firms the narrowest, with coverage near 80% for both groups.

  (3) gross_margin_peer_mismatch
      rule: EV/Sales | base constant | terms gross_margin +0.6, ebitda_margin -0.4, n_peers -0.6
      mechanism: Peers are matched on size and EBITDA margin, but EV/Sales reflects the long-run margin a business can reach, which follows gross margin. A high-gross-margin firm whose EBITDA margin is held down by sales, marketing or R&D spending gets matched to low-gross-margin peers with similar current EBITDA margins but a much lower ceiling, and the mismatch is worse in thin sectors where the nearest peers are far away.
      prediction: Interval score below the constant band's 4.233 for EV/Sales, and highest_rnd_20pct coverage rising above 72%.

  (4) growth_mismatch_extremes
      rule: EV/Sales | base constant | terms sales_growth_3y +0.4 | if sales_growth_1y >= p85 x1.4 | if sales_growth_1y <= p10 x1.3 | if no_history x1.3
      mechanism: An EV/Sales multiple largely capitalizes expected sales growth, but peers are matched on size and margin, not growth. Firms whose growth is far from typical, in either direction (very fast growers, sharply shrinking firms, or newly listed firms with no growth record), get a peer multiple built for a different growth path, so their actual EV can sit far from the peer-implied value.
      prediction: Interval score below the constant band's 4.233 for EV/Sales, with fastest_growing_20pct coverage near 80%.

  (5) small_intangible_option_value
      rule: EV/Sales | base constant | terms log_sales -0.7, rnd_intensity +0.5 | if no_history x1.3
      mechanism: Small, R&D-intensive firms are valued mostly on unproven intangible assets and growth options, which current sales do not reveal, and their thin analyst coverage and illiquid shares mean little public information pins those options down. Recent listings, which have no trading or reporting history, are the extreme case, so the peer sales multiple is the weakest anchor for this group.
      prediction: Interval score below the constant band's 4.233 for EV/Sales, with smallest_20pct coverage rising from 68% to near 80% without over-covering (staying below 88%).

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}
