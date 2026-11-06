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
  [g03-01] EV/EBITDA | base constant | terms log_assets -0.8, debt_to_assets -0.5, capex_intensity -0.3 | if loss_making x1.4 | if sales_growth_1y >= p85 x1.3
  [g03-02] EV/EBITDA | base constant | terms log_sales -0.8, rnd_intensity +0.4 | if roic <= p10 x1.4 | if net_margin <= p10 x1.3 | if sales_growth_1y >= p85 x1.3
  [g03-03] EV/EBITDA | base constant | terms peer_iqr +0.5, log_sales -0.8, gross_margin +0.4 | if loss_making x1.4
  [g03-04] EV/Sales | base constant | terms log_sales -0.8, rnd_intensity +0.5, peer_iqr +0.4 | if negative_ebitda x1.5 | if sales_growth_1y >= p90 x1.3
  [g03-05] EV/Sales | base constant | terms log_sales -0.7, debt_to_assets -0.6, peer_iqr +0.4 | if negative_ebitda x1.5 | if no_history x1.3
  [g03-06] EV/Sales | base constant | terms log_sales -0.9, sales_growth_1y +0.3 | if negative_ebitda x1.6 | if net_margin <= p10 x1.3 | if no_history x1.3

PROPOSALS
  (0) ebitda_operating_leverage_residual
      rule: EV/EBITDA | base constant | terms gross_margin +0.6, ebitda_margin -0.6, log_sales -0.7 | if rnd_intensity >= p80 x1.2
      mechanism: EBITDA is what is left of gross profit after a largely fixed operating cost base, so a firm with a high gross margin but a low EBITDA margin has EBITDA that is a thin residual of gross profit: a small change in revenue or opex moves it a lot, and the market prices the gross-profit franchise rather than the depressed residual. Its EV/EBITDA multiple therefore floats far from peers, while firms whose EBITDA captures most of gross profit (low gross, high EBITDA margin) have a stable earnings base that trades near sector norms.
      prediction: Interval score below the constant band's (2.735) and below g02-02's 2.704, with coverage of highest_rnd_20pct firms above 72%.

  (1) ebitda_growth_profit_mismatch
      rule: EV/EBITDA | base constant | terms log_sales -0.8, gross_margin +0.3 | if sales_growth_1y >= p80 AND ebit_margin <= p30 x1.5 | if sales_growth_1y <= p15 AND ebit_margin <= p30 x1.3 | if loss_making x1.2
      mechanism: A fast-growing firm with a thin operating margin is expensing its growth (sales force, onboarding, R&D), so current EBITDA is a temporarily depressed base and the market capitalizes a much larger future EBITDA whose size peers cannot reveal; the multiple is extreme and unpredictable. A shrinking firm with thin margins is the mirror case, priced on restructuring or liquidation value rather than going-concern EBITDA. Only the combination of growth extremes with weak margins should widen the range; profitable fast growers already show the earnings the market is paying for.
      prediction: Interval score below the constant band's (2.735) and fastest_growing_20pct coverage of at least 78%, with the two interaction conditions each covering under 15% of firms.

  (2) ebitda_return_on_capital_tails
      rule: EV/EBITDA | base constant | terms log_assets -0.8, asset_turnover +0.3 | if roic <= p10 x1.4 | if roic >= p90 x1.3 | if roe >= p95 x1.2
      mechanism: Return on invested capital is U-shaped in its link to comps error: at very low ROIC, current EBITDA is far below the normalized earnings the market capitalizes, and at very high ROIC the firm's value rests on unmeasured intangible capital (brands, software, network effects) whose durability the market judges firm by firm, so in both tails the multiple departs from the sector median. Firms earning ordinary returns on a measured capital base are priced like their peers.
      prediction: Interval score below g03-02's 2.557 is not required, but below the constant band's 2.735; the roic above p90 condition should raise coverage of the highest-ROIC decile to near 80% rather than above it.

  (3) sales_margin_tail_matching
      rule: EV/Sales | base constant | terms log_sales -0.8 | if ebitda_margin <= p10 x1.5 | if ebitda_margin >= p90 x1.3 | if gross_margin >= p85 x1.2 | if n_peers <= p10 x1.2
      mechanism: EV/Sales equals EBITDA margin times an EBITDA multiple, so the peer median sales multiple is only valid if peers share the target's margin; nearest-neighbour peer matching works well in the middle of the margin distribution but at its tails the closest peers are still far away, so the sales multiple is extrapolated. Firms with very low margins are priced on whether margins recover, and firms with very high margins on how durable they are, so both tails should get wide ranges, unlike a monotone margin term that wrongly narrows the high-margin tail.
      prediction: Interval score below the constant band's (4.233) and below g02-04's 4.518, with coverage of loss_making and highest_rnd_20pct firms between 76% and 86%.

  (4) sales_pipeline_value_firms
      rule: EV/Sales | base constant | terms log_sales -0.8, gross_margin +0.3 | if rnd_intensity >= p80 AND loss_making x1.6 | if sales_growth_1y >= p85 AND negative_ebitda x1.4 | if no_history x1.3
      mechanism: For R&D-intensive firms that are still losing money, and for hypergrowth firms with negative EBITDA, current sales are not the value driver: the market prices a product pipeline or a future scale whose payoff is binary, so revenue is close to irrelevant and any sales multiple taken from peers is arbitrary. Outside these pipeline-type firms, sales relate to value through ordinary margins and the peer median anchors well.
      prediction: Interval score below the constant band's (4.233), with the interaction firms making up under 15% of the sample but receiving ranges at least 1.5x the median width.

  (5) sales_steady_state_compounders
      rule: EV/Sales | base constant | terms log_sales -0.7, peer_iqr +0.3 | if roic >= p50 AND sales_growth_1y <= p60 x0.7 | if loss_making x1.4
      mechanism: A profitable firm earning above-median returns with modest growth is close to steady state, where a growing-perpetuity valuation ties its sales multiple tightly to margin and cost of capital, quantities that peers in the same industry share, so comps should be unusually accurate and the range can be narrowed. Loss-makers and firms whose peers disagree have no such anchor and need wider ranges.
      prediction: Interval score below the constant band's (4.233), with the steady-state group's median range at least 20% narrower than the overall median while its coverage stays above 75%.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}
