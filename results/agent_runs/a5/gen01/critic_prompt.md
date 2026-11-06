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
  (0) ebitda_small_innovative_losers
      rule: EV/EBITDA | base constant | terms log_sales -1, rnd_intensity +0.6, sales_growth_1y +0.4 | if loss_making x1.4
      mechanism: Small firms and R&D-heavy firms derive much of their value from intangible growth options that current EBITDA does not capture, so the peer EBITDA multiple is a poor anchor; their thin analyst coverage and illiquidity add pricing noise. Loss-making firms with positive EBITDA have earnings that are transitory or burdened by below-EBITDA charges, making the EBITDA base itself unreliable.
      prediction: Interval score below the constant band's 2.735 on EV/EBITDA, with coverage of the smallest-20% and highest-R&D-20% groups rising toward 75-80%.

  (1) ebitda_thin_margin_denominator
      rule: EV/EBITDA | base constant | terms ebitda_margin -1.2, roic -0.5, log_assets -0.7 | if net_debt_to_ebitda >= p90 x1.3
      mechanism: When EBITDA is a small fraction of sales, the EV/EBITDA multiple is a ratio with a small, volatile denominator: modest deviations in normalised profitability produce large swings in implied value, and the market prices such firms off recovery expectations rather than current EBITDA. Low-return, highly levered firms are in the same position because their EBITDA is likely cyclically depressed or distressed.
      prediction: Interval score below the constant band's 2.735 on EV/EBITDA; firms in the bottom EBITDA-margin quintile get ranges at least 1.5x wider than top-quintile firms and still reach near-80% coverage.

  (2) ebitda_growth_premium_peer_disagreement
      rule: EV/EBITDA | base constant | terms gross_margin +0.7, sales_growth_1y +0.6, peer_iqr +0.5, log_sales -0.6 | if no_history x1.3
      mechanism: High-gross-margin, fast-growing firms are valued on future rather than current EBITDA, and the market's view of their growth horizon varies widely, so the peer median multiple is a noisy anchor. Where peers themselves disagree strongly on the multiple, the sector lacks a common pricing convention, and firms without sales history have no track record against which to normalise earnings.
      prediction: Interval score below the constant band's 2.735 and below the peer_iqr-proportional band's 2.732 on EV/EBITDA; fastest-growing-20% coverage rises above 75%.

  (3) sales_profitability_gap
      rule: EV/Sales | base constant | terms ebitda_margin -1, log_sales -0.8 | if negative_ebitda x1.6 | if loss_making x1.2
      mechanism: EV/Sales implicitly assumes the target converts sales into cash flow like its peers; firms with low or negative EBITDA margins are valued on a turnaround or option value that sales alone cannot reveal, so their actual EV can sit far above or below the peer-implied level. Small firms add illiquidity and coverage noise on top.
      prediction: Interval score below the constant band's 4.233 on EV/Sales; coverage of loss-making firms rises from 72% toward 80%.

  (4) sales_intangible_growth_story
      rule: EV/Sales | base constant | terms gross_margin +0.8, rnd_intensity +0.8, sales_growth_1y +0.6, log_sales -0.6
      mechanism: For high-gross-margin, R&D-intensive, fast-growing firms (software, biotech, devices), EV/Sales is set by expectations of long-run margins and growth duration, which differ greatly across otherwise similar firms; peer sales multiples therefore scatter widely around the truth. Low-gross-margin, low-R&D businesses such as distributors and manufacturers have tightly bounded sales multiples because their margins are competed to a narrow band.
      prediction: Interval score below the constant band's 4.233 on EV/Sales; highest-R&D-20% and fastest-growing-20% coverage both rise above 77%.

  (5) sales_small_young_cash_burners
      rule: EV/Sales | base constant | terms log_assets -1.2, sales_growth_1y +0.5 | if loss_making AND log_sales <= p30 x1.5 | if no_history x1.3
      mechanism: Small, young, loss-making firms are priced largely on financing risk and the survival probability of a single product or market, idiosyncratic factors that peers matched on size and margin do not share. Firms with no sales history or very high asset turnover relative to their tiny asset base lack a stable economic footprint, so their sales are a weak anchor for enterprise value.
      prediction: Interval score below the constant band's 4.233 on EV/Sales; coverage of the smallest-20% group rises from 68% to at least 76%.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}
