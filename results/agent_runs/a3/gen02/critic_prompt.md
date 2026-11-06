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
  [g01-01] EV/EBITDA | base constant | terms log_sales -1, ebitda_margin -1 | if loss_making x1.4
  [g01-02] EV/EBITDA | base constant | terms rnd_intensity +0.8, sales_growth_1y +0.6, gross_margin +0.5, log_assets -0.6 | if no_history x1.3
  [g01-03] EV/EBITDA | base constant | terms net_debt_to_ebitda +0.6, log_sales -0.8 | if debt_to_assets >= p80 AND loss_making x1.5 | if peer_iqr >= p80 x1.3
  [g01-04] EV/Sales | base constant | terms log_sales -1, rnd_intensity +0.7 | if negative_ebitda x1.8 | if loss_making x1.2
  [g01-05] EV/Sales | base constant | terms gross_margin +0.8, sales_growth_1y +0.6, log_assets -0.8 | if loss_making AND rnd_intensity >= p80 x1.5
  [g01-06] EV/Sales | base constant | terms peer_range +0.6, log_sales -0.7 | if ebitda_margin <= p15 x1.6 | if no_history x1.3

PROPOSALS
  (0) ebitda_unrepresentative_year
      rule: EV/EBITDA | base constant | terms log_sales -0.9, ebitda_margin -0.7 | if sales_growth_1y <= p10 x1.35 | if sales_growth_1y >= p90 x1.35 | if loss_making x1.3
      mechanism: Reported EBITDA is a poor proxy for normalized earnings in a year when sales collapsed or surged, because operating leverage pushes EBITDA temporarily below or above its sustainable level; the market capitalizes normalized EBITDA, so applying a peer multiple to that year's EBITDA misses in either direction. This adds to the thin-margin and small-size effects, where small absolute EBITDA errors move the ratio a lot and idiosyncratic risk is high.
      prediction: Interval score below the constant band's 2.735 and at or below g01-01's 2.581, with coverage of fastest_growing_20pct rising above 75% compared with 71% under g01-01.

  (1) ebitda_to_cash_conversion
      rule: EV/EBITDA | base constant | terms ebitda_margin -0.9, capex_intensity +0.6, log_assets -0.8 | if net_margin <= p10 x1.4
      mechanism: EBITDA ignores capital expenditure, so for capital-hungry firms the share of EBITDA that becomes free cash flow differs a lot between companies, and investors value them on EBIT or FCF rather than EBITDA; a peer median EV/EBITDA therefore transfers poorly when capex intensity is high and margins are thin. Deeply unprofitable firms (very negative net margin despite positive EBITDA) have large below-the-line charges such as depreciation, interest or impairments, which signal EBITDA that will not persist.
      prediction: Interval score below the constant band's 2.735; firms in the top capex-intensity quintile get wider ranges, and those ranges still cover about 80% of them.

  (2) transitory_ebitda_plus_growth_options
      rule: EV/EBITDA | base constant | terms log_sales -0.8, ebitda_margin -0.8, rnd_intensity +0.5, sales_growth_1y +0.4 | if loss_making x1.3
      mechanism: Two separate channels make EV/EBITDA comps unreliable. First, thin EBITDA and small size make the ratio noisy and idiosyncratic. Second, R&D-heavy, fast-growing firms carry growth-option value that current EBITDA does not measure. Combining the two should rank uncertainty better than either alone, because they pick out different firms: mature low-margin small caps and young innovators.
      prediction: Interval score below 2.581 (g01-01) and below the linear-regression benchmark of 2.448 or close to it, with highest_rnd_20pct coverage above 75%.

  (3) operating_investment_gap
      rule: EV/Sales | base constant | terms gross_margin +0.6, ebitda_margin -0.6, peer_range +0.4, log_sales -0.5 | if no_history x1.3
      mechanism: A firm with high gross margin but low EBITDA margin is spending heavily on operating investment (sales, marketing, R&D), so its value depends on how much operating leverage it eventually achieves, not on current revenue economics; investors disagree widely on that, so the same sales are worth very different amounts. When the peers' sales multiples also span a wide range, the sector has no stable revenue-to-value mapping.
      prediction: Interval score below g01-06's 4.143 and below the constant band's 4.233, with smallest_20pct coverage closer to 80% than g01-06's over-wide 88%.

  (4) thin_sector_peer_mismatch
      rule: EV/Sales | base constant | terms peer_range +0.6, log_sales -0.5 | if n_peers <= p10 x1.5 | if ebitda_margin <= p15 x1.5
      mechanism: When a sector has few listed firms, the peer set is small and less similar to the target in business mix, so the median peer sales multiple is a weak anchor; every earlier rule under-covered these firms (69-73%). Firms with depressed EBITDA margins have no earnings base tying value to revenue, and wide peer dispersion means the sector itself prices sales inconsistently.
      prediction: Interval score below the constant band's 4.233, with fallback_or_few_peers coverage rising to about 78% or more compared with 71-73% before.

  (5) asset_heavy_revenue_disconnect
      rule: EV/Sales | base constant | terms asset_turnover -0.7, log_sales -0.6, sales_growth_1y +0.3 | if negative_ebitda x1.4 | if no_history x1.3
      mechanism: Sales multiples work best for firms whose value scales with revenue. For asset-heavy firms (low asset turnover) value comes from the asset base, its returns and commodity or regulatory conditions, so EV per dollar of sales varies widely, while high-turnover firms such as distributors and retailers have thin, stable margins and tightly clustered EV/Sales. Firms with non-positive EBITDA lack any operating anchor, though they get a moderate rather than extreme multiplier, since earlier rules over-covered them.
      prediction: Interval score below the constant band's 4.233; coverage of loss_making firms between 75% and 85% rather than the 88% of g01-04.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}
