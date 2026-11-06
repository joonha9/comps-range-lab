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

PROPOSALS
  (0) netdebt_known_share_of_multiple
      rule: EV/EBITDA | base constant | terms net_debt_to_ebitda -0.8, log_sales -0.6 | if net_debt_to_ebitda <= p10 x1.3 | if loss_making x1.3
      mechanism: An EV/EBITDA multiple splits exactly into net debt/EBITDA plus market cap/EBITDA, and the first piece is read off the balance sheet at close to book value. So the larger net debt is relative to EBITDA, the more of the target's multiple is already known, and the log error of the comps estimate gets smaller. Firms holding a lot of net cash work the other way: their EV is equity minus cash, a difference that magnifies any equity mispricing. Small firms and loss-making firms carry the most idiosyncratic, story-driven equity value.
      prediction: Interval score below the constant band's 2.735 and at or below the best archived EV/EBITDA rule (2.585), with loss_making coverage at least 75% and smallest_20pct coverage at least 75%.

  (1) transitory_trailing_ebitda
      rule: EV/EBITDA | base constant | terms ebitda_margin -0.7, log_assets -0.6 | if sales_growth_1y >= p85 x1.3 | if sales_growth_1y <= p10 x1.3
      mechanism: The market capitalizes normalized forward EBITDA, and trailing EBITDA is a poor proxy for it in two cases. One is thin margins, where operating leverage turns small cost or price changes into large percentage swings in EBITDA. The other is sales moving sharply up or down, where the current year is not a steady state. Firms with small asset bases have the most volatile year-to-year EBITDA, so a peer multiple on their trailing figure fits least.
      prediction: Interval score below the constant band's 2.735 and below both single-idea rules it unifies (g01-01 2.590, g02-02 2.593), with fastest_growing_20pct coverage at least 75%.

  (2) expensed_investment_gap
      rule: EV/EBITDA | base constant | terms gross_margin +0.5, ebitda_margin -0.6, log_sales -0.5 | if gross_margin >= p70 AND ebitda_margin <= p30 x1.3
      mechanism: A high gross margin alongside a low EBITDA margin means large operating expenses, mainly selling, marketing and R&D, sit between gross profit and EBITDA. Much of that spending is investment in customers and products. The market values the profit the business could earn before that investment, but how much of the gap is discretionary investment and how much is a permanent cost differs from firm to firm, so EBITDA understates the earning base by an amount peers cannot reveal. Smaller firms spend a larger share of opex on growth, which widens the gap.
      prediction: Interval score below the constant band's 2.735, with highest_rnd_20pct coverage at least 75% and the high-gross-margin, low-EBITDA-margin subgroup closer to 80% coverage than under the constant band.

  (3) debt_anchor_and_cash_amplification
      rule: EV/Sales | base constant | terms debt_to_assets -0.6, log_sales -0.4 | if debt_to_assets <= p25 AND rnd_intensity >= p70 x1.3 | if negative_ebitda x1.3
      mechanism: Enterprise value is debt, priced near book, plus equity minus cash, and only the equity piece carries the market's diverging views on how sales will become profit. A heavily debt-financed firm's EV is mostly the stable debt claim, so its EV/Sales error is damped. R&D-intensive firms with almost no debt usually hold large cash balances, so their EV is equity minus cash, a difference that magnifies equity mispricing in percentage terms. Negative EBITDA leaves value resting entirely on future profitability.
      prediction: Interval score below the constant band's 4.233 and at or below the best archived EV/Sales rule (4.091), with highest_rnd_20pct coverage at least 78%.

  (4) peer_match_quality_at_edges
      rule: EV/Sales | base constant | terms n_peers -0.5, log_sales -0.5 | if ebitda_margin <= p10 x1.4 | if ebitda_margin >= p90 x1.2
      mechanism: Peers are chosen as nearest neighbours on size and EBITDA margin within the same 2-digit SIC code. A target at the edge of those distributions (very small, extreme low or high margin, or in a thin sector with few peers) is necessarily matched with firms that are systematically unlike it. Because EV/Sales rises steeply with margin, a peer median from firms with clearly different margins is a biased anchor for the target's revenue multiple, so the error is large and unpredictable in direction.
      prediction: Interval score below the constant band's 4.233, with fallback_or_few_peers coverage at least 78% (vs 71% for the constant band) and smallest_20pct coverage at least 76%.

  (5) unprofitable_growth_options
      rule: EV/Sales | base constant | terms log_sales -0.5 | if loss_making AND sales_growth_1y >= p70 x1.5 | if negative_ebitda x1.2
      mechanism: A firm that is losing money but growing sales fast has an equity that behaves like a call option on reaching profitable scale. Option value is very sensitive to beliefs about the distant future, and those beliefs differ widely across firms within an industry, so trailing revenue multiples from peers pin its EV down poorly. Small firms are the most option-like, and negative EBITDA means no part of today's operations anchors the value.
      prediction: Interval score below the constant band's 4.233, with loss_making coverage at least 78% and fastest_growing_20pct coverage at least 78%.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}
