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
      rule: EV/EBITDA | base constant | terms log_sales -1, ebitda_margin -0.8 | if loss_making x1.4
      mechanism: When EBITDA is a small slice of sales, a given dollar shock to costs moves EBITDA by a large percentage, so the market prices the firm off normalized rather than current EBITDA and the trailing multiple is noisy. Small firms add idiosyncratic risk, illiquidity and thin analyst coverage, so peers' multiples transfer poorly; loss-making firms with positive EBITDA have earnings below the line (interest, D&A, write-offs) that the multiple ignores.
      prediction: EV/EBITDA interval score below the constant band's 2.735, with coverage of the smallest-20% and loss-making groups rising toward 80%.

  (1) ebitda_intangible_growth_option
      rule: EV/EBITDA | base constant | terms rnd_intensity +0.8, sales_growth_1y +0.6, log_assets -0.7 | if no_history x1.5
      mechanism: Firms that expense heavy R&D and grow fast have current EBITDA depressed by investment that is really capital spending, so their EV reflects growth options that trailing EBITDA cannot capture and that differ greatly from peer to peer. Recently listed or newly covered firms (no prior-year sales) have short track records, so investors disagree more about their steady-state earnings.
      prediction: EV/EBITDA interval score below the constant band's 2.735, with coverage of the highest-R&D and fastest-growing 20% groups improving from 66% and 70% toward 80%.

  (2) ebitda_low_return_distress
      rule: EV/EBITDA | base constant | terms roic -0.8, log_sales -0.8 | if ebitda_margin <= p20 x1.4 | if debt_to_assets >= p80 AND ebit_margin <= p30 x1.3
      mechanism: Firms earning low returns on invested capital are valued closer to their asset base or liquidation and restructuring outcomes than to a going-concern multiple of EBITDA, so earnings-based comps describe them poorly. Highly levered firms with thin margins carry distress and refinancing risk, and that risk moves the debt and equity parts of EV in ways the peers do not share.
      prediction: EV/EBITDA interval score below the constant band's 2.735; the low-ROIC firms flagged by the rule should account for a disproportionate share of the largest absolute log errors.

  (3) sales_unanchored_profitability
      rule: EV/Sales | base constant | terms ebitda_margin -1, log_sales -0.8 | if negative_ebitda x1.6 | if no_history x1.3
      mechanism: EV/Sales is essentially a margin times an earnings multiple, so it transfers across firms only when they have similar margins; when a firm's EBITDA margin is low or negative, its value rests on the market's guess of future margins rather than current economics, and that guess varies widely. Small firms add idiosyncratic and liquidity noise on top of this.
      prediction: EV/Sales interval score below the constant band's 4.233, with coverage of the loss-making and smallest-20% groups rising toward 80%.

  (4) sales_scalable_growth_option
      rule: EV/Sales | base constant | terms gross_margin +0.8, rnd_intensity +0.7, sales_growth_1y +0.7, log_assets -0.6
      mechanism: High gross margin, R&D-intensive, fast-growing firms (software and biotech style) are valued on scalable future margins, so their revenue multiples spread over an order of magnitude even within a 2-digit SIC code, and a peer median is a weak anchor. Low-gross-margin, slow-growing distributors and manufacturers trade in narrow revenue-multiple bands set by their thin, stable margins.
      prediction: EV/Sales interval score below the constant band's 4.233, with coverage of the highest-R&D and fastest-growing 20% groups improving from 72% and 75% toward 80%.

  (5) sales_small_distressed_peer_disagreement
      rule: EV/Sales | base constant | terms log_sales -1, peer_iqr +0.5, net_margin -0.6 | if loss_making AND log_sales <= p30 x1.5 | if debt_to_assets >= p80 x1.3
      mechanism: Small, loss-making firms with heavy debt have option-like equity whose value depends on survival rather than on revenue, so EV/Sales drawn from healthier peers misprices them in either direction. Where peers themselves disagree strongly, the sector holds several business models, and the median multiple is a less reliable anchor; this enters as a moderate term rather than the base because a pure peer_iqr scaling overweights it.
      prediction: EV/Sales interval score below the constant band's 4.233 and below the width-proportional-to-peer_iqr benchmark's 4.340.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}
