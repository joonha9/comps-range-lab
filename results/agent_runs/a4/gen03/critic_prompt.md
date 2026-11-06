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
  [g02-01] EV/EBITDA | base constant | terms log_sales -0.8, rnd_intensity +0.5, sales_growth_1y +0.4 | if loss_making x1.4
  [g02-02] EV/EBITDA | base constant | terms ebitda_margin -0.8, net_debt_to_ebitda +0.5, log_assets -0.6 | if no_history x1.3
  [g02-03] EV/EBITDA | base constant | terms log_sales -0.7, gross_margin +0.5 | if sales_growth_1y >= p85 x1.4 | if sales_growth_1y <= p10 x1.3
  [g02-04] EV/Sales | base constant | terms ebitda_margin -1, log_sales -0.6, rnd_intensity +0.5 | if negative_ebitda x1.5
  [g02-05] EV/Sales | base constant | terms gross_margin +0.8, sales_growth_1y +0.6, log_assets -0.6 | if loss_making x1.3
  [g02-06] EV/Sales | base constant | terms peer_iqr +0.4, log_sales -0.8 | if negative_ebitda x1.4 | if n_peers <= p10 x1.3 | if no_history x1.3

PROPOSALS
  (0) ebitda_debt_anchor
      rule: EV/EBITDA | base constant | terms log_assets -0.8, debt_to_assets -0.5, capex_intensity -0.3 | if loss_making x1.4 | if sales_growth_1y >= p85 x1.3
      mechanism: Enterprise value is the sum of debt and equity, and the debt piece is close to book value and moves little, so in highly levered firms most of EV is pinned down and the log error of a peer-multiple estimate is mechanically smaller. Asset-heavy, capex-intensive firms are also priced off replaceable tangible capital, which keeps their multiples close to sector norms, while small equity-funded firms, loss-makers and hypergrowers carry their value in volatile equity claims on uncertain future earnings.
      prediction: Interval score below the constant band's 2.735, and coverage of loss_making and smallest_20pct firms above the constant band's 68% and 63%.

  (1) ebitda_transitory_earnings
      rule: EV/EBITDA | base constant | terms log_sales -0.8, rnd_intensity +0.4 | if roic <= p10 x1.4 | if net_margin <= p10 x1.3 | if sales_growth_1y >= p85 x1.3
      mechanism: Investors price normalized rather than current earnings, so when a firm's returns on capital or net margins are far below normal (a cyclical trough, restructuring or write-down year), current EBITDA understates the earnings the market capitalizes and the EV/EBITDA multiple spikes unpredictably relative to peers. Small and R&D-heavy firms add intangible value not in EBITDA; firms earning normal returns trade near the peer median.
      prediction: Interval score below the constant band's 2.735 with coverage of loss_making firms near 80%; the low-roic condition alone should widen ranges where the constant band misses most.

  (2) ebitda_peer_disagreement_intangibles
      rule: EV/EBITDA | base constant | terms peer_iqr +0.5, log_sales -0.8, gross_margin +0.4 | if loss_making x1.4
      mechanism: When the ten nearest peers disagree strongly on their EBITDA multiple, the sector has no stable pricing convention and the median is a weak anchor for the target. This is compounded for small and high-gross-margin firms, whose intangible-heavy business models are valued on scalability expectations that differ widely across firms, and for loss-makers whose EBITDA is above what reaches shareholders.
      prediction: Interval score below the constant band's 2.735 and below the width-proportional-to-peer_iqr benchmark's 2.732, since peer dispersion is used as a moderate tilt rather than a full scale.

  (3) sales_preprofit_innovators
      rule: EV/Sales | base constant | terms log_sales -0.8, rnd_intensity +0.5, peer_iqr +0.4 | if negative_ebitda x1.5 | if sales_growth_1y >= p90 x1.3
      mechanism: For firms with negative EBITDA or heavy R&D spending, a dollar of sales says little about value: the market prices the probability and timing of future profitability and the success of product pipelines, which differ sharply among firms with similar sales. Hypergrowth adds further dispersion because the multiple capitalizes sales years ahead; peer disagreement signals a sector with no stable sales-to-value conversion.
      prediction: Interval score below the constant band's 4.233, with highest_rnd_20pct and fastest_growing_20pct coverage at or above 80%.

  (4) sales_debt_anchor
      rule: EV/Sales | base constant | terms log_sales -0.7, debt_to_assets -0.6, peer_iqr +0.4 | if negative_ebitda x1.5 | if no_history x1.3
      mechanism: In levered firms a large share of EV is debt carried near face value, so EV is less sensitive to swings in equity sentiment and a peer-median sales multiple misses by less in log terms. Equity-financed small firms, and especially those burning cash with negative EBITDA, have EV that is almost entirely a volatile option-like equity claim, so their sales multiple is far harder to pin down from peers.
      prediction: Interval score below the constant band's 4.233, and median range narrower than x/3.38 at about 80% coverage.

  (5) sales_going_concern_doubt
      rule: EV/Sales | base constant | terms log_sales -0.9, sales_growth_1y +0.3 | if negative_ebitda x1.6 | if net_margin <= p10 x1.3 | if no_history x1.3
      mechanism: A firm with deeply negative net margins or negative EBITDA is valued on survival odds, dilution and recovery rather than as a going concern, so its EV can be a small or large fraction of what peers' sales multiples imply. Small firms and firms new to the sample face the same doubt with less public track record, while large, profitable firms trade in a tight band of sales multiples.
      prediction: Interval score below the constant band's 4.233, with loss_making and smallest_20pct coverage above the constant band's 72% and 68%.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}
