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
  [g01-01] EV/EBITDA | base constant | terms log_sales -1, ebitda_margin -0.8 | if loss_making x1.4
  [g01-02] EV/EBITDA | base constant | terms rnd_intensity +0.8, sales_growth_1y +0.6, log_assets -0.7 | if no_history x1.5
  [g01-03] EV/EBITDA | base constant | terms roic -0.8, log_sales -0.8 | if ebitda_margin <= p20 x1.4 | if debt_to_assets >= p80 AND ebit_margin <= p30 x1.3
  [g01-04] EV/Sales | base constant | terms ebitda_margin -1, log_sales -0.8 | if negative_ebitda x1.6 | if no_history x1.3
  [g01-05] EV/Sales | base constant | terms gross_margin +0.8, rnd_intensity +0.7, sales_growth_1y +0.7, log_assets -0.6
  [g01-06] EV/Sales | base constant | terms log_sales -1, peer_iqr +0.5, net_margin -0.6 | if loss_making AND log_sales <= p30 x1.5 | if debt_to_assets >= p80 x1.3
  [g02-01] EV/EBITDA | base constant | terms log_sales -0.8, ebitda_margin -0.6, rnd_intensity +0.5, sales_growth_1y +0.4 | if loss_making x1.3
  [g02-02] EV/EBITDA | base constant | terms capex_intensity +0.5, ebit_margin -0.7, log_sales -0.7 | if net_debt_to_ebitda >= p85 x1.25
  [g02-03] EV/EBITDA | base constant | terms log_sales -0.8, net_margin -0.5 | if sales_growth_1y >= p85 x1.3 | if sales_growth_1y <= p10 x1.3
  [g02-04] EV/Sales | base constant | terms n_peers -0.6, log_sales -0.4, peer_range +0.3 | if negative_ebitda x1.3
  [g02-05] EV/Sales | base constant | terms gross_margin +0.6, ebitda_margin -0.6, log_sales -0.3
  [g02-06] EV/Sales | base constant | terms log_assets -0.3 | if sales_growth_1y >= p85 x1.35 | if sales_growth_1y <= p10 x1.3 | if no_history x1.25
  [g03-01] EV/EBITDA | base constant | terms log_sales -0.7, ebitda_margin -0.6, rnd_intensity +0.5, capex_intensity +0.4 | if loss_making x1.3
  [g03-02] EV/EBITDA | base constant | terms gross_margin +0.6, ebitda_margin -0.7, log_sales -0.8, debt_to_assets -0.3 | if loss_making x1.3
  [g03-03] EV/EBITDA | base constant | terms log_sales -0.8, ebitda_margin -0.6, rnd_intensity +0.4 | if sales_growth_1y >= p85 x1.3 | if sales_growth_1y <= p10 x1.3 | if loss_making x1.25 | if no_history x1.2
  [g03-04] EV/Sales | base constant | terms n_peers -0.6, peer_range +0.3, log_assets -0.3 | if sales_growth_1y >= p85 x1.3 | if sales_growth_1y <= p10 x1.3 | if no_history x1.2 | if negative_ebitda x1.25
  [g03-05] EV/Sales | base constant | terms gross_margin +0.5, ebitda_margin -0.4, n_peers -0.5, log_sales -0.3 | if negative_ebitda x1.25
  [g03-06] EV/Sales | base constant | terms debt_to_assets -0.5, rnd_intensity +0.4, n_peers -0.5, log_sales -0.3 | if negative_ebitda x1.3

PROPOSALS
  (0) g04-E1 opex headroom plus run-rate transition
      rule: EV/EBITDA | base constant | terms log_sales -0.8, ebitda_margin -0.7, gross_margin +0.5, debt_to_assets -0.3 | if sales_growth_1y >= p85 x1.25 | if sales_growth_1y <= p10 x1.25 | if loss_making x1.25 | if no_history x1.2
      mechanism: Two independent reasons make trailing EBITDA a poor value anchor. First, a high gross margin with a thin EBITDA margin means EBITDA is depressed by discretionary opex the market may expect to scale down, so EV rests on a disputed normalized margin, while thin-gross-margin firms have no such headroom. Second, after an acquisition, ramp, collapse or divestiture (both growth tails) or a new listing, trailing EBITDA is not the run-rate the market prices. Debt carried near face value dampens log EV errors in heavily indebted firms.
      prediction: Interval score below 2.52 (better than g03-02 and g03-03 individually), with fastest_growing_20pct coverage at or above 76% and highest_rnd_20pct coverage near 78-80%.

  (1) g04-E2 net cash amplifies equity uncertainty in EV
      rule: EV/EBITDA | base constant | terms log_sales -0.8, ebitda_margin -0.6, net_debt_to_ebitda -0.5, rnd_intensity +0.3 | if loss_making x1.25 | if sales_growth_1y >= p85 x1.25 | if sales_growth_1y <= p10 x1.25
      mechanism: EV equals equity plus debt minus cash. In firms holding large net cash relative to EBITDA, EV is smaller than market capitalization, so a given percentage uncertainty in the equity value becomes a larger percentage error in EV, and the market additionally disagrees on how much trapped or idle cash is worth. In heavily indebted firms the reverse holds: near-face-value debt dominates EV and damps log errors, which also explains why widening for high net debt (g02-02) scored worse. A single linear net_debt_to_ebitda term captures this whole capital-structure gradient on top of the size and thin-margin channels.
      prediction: Interval score below 2.54 (g02-01) and below the constant band's 2.735; firms in the lowest net_debt_to_ebitda quintile get ranges at least 1.3x wider than the top quintile without falling below 78% coverage.

  (2) g04-E3 expensed R&D only matters when it crushes EBITDA
      rule: EV/EBITDA | base constant | terms log_sales -0.8, ebitda_margin -0.5, debt_to_assets -0.3 | if rnd_intensity >= p75 AND ebitda_margin <= p35 x1.35 | if sales_growth_1y >= p85 x1.25 | if sales_growth_1y <= p10 x1.2 | if loss_making x1.25
      mechanism: Expensing R&D understates the earnings base only when R&D is large relative to what is left over: a mature pharma or semiconductor firm with heavy R&D but a fat EBITDA margin is valued on stable EBITDA, while an R&D-heavy firm with thin EBITDA is valued on pipeline and growth options that trailing EBITDA cannot measure. This is an interaction, so it enters as a joint condition rather than a linear R&D term that also widens profitable R&D firms. Size, thin margins, losses and growth-tail transitions remain separate channels; debt share of EV damps errors.
      prediction: Interval score below 2.53, with highest_rnd_20pct coverage between 76% and 82% (no over-coverage of profitable R&D firms) and loss_making coverage near 80%.

  (3) g04-S1 capital structure maps equity noise into EV
      rule: EV/Sales | base constant | terms n_peers -0.5, debt_to_assets -0.4, peer_range +0.3, log_assets -0.2 | if net_debt_to_ebitda <= p15 AND ebitda_margin >= p30 x1.3 | if sales_growth_1y >= p85 x1.3 | if sales_growth_1y <= p10 x1.25 | if negative_ebitda x1.25
      mechanism: An EV/Sales comp effectively prices equity plus net debt; debt is nearly a fixed claim, so in debt-heavy firms the uncertain equity is a small share of EV and log errors shrink, while profitable firms sitting on large net cash have EV below market capitalization, so equity uncertainty is amplified in EV. The peer anchor is also weak in thin or dispersed sectors, and trailing sales misstate the run-rate in both growth tails and for firms with negative EBITDA whose value depends on future margins.
      prediction: Interval score below 4.05 (g03-04), with fallback_or_few_peers coverage near 80% and cash-rich profitable firms (net_debt_to_ebitda below p15 with ebitda_margin above p30) covered at or above 77%.

  (4) g04-S2 unrealized operating leverage as a joint condition
      rule: EV/Sales | base constant | terms n_peers -0.6, peer_range +0.3, log_assets -0.3 | if gross_margin >= p70 AND ebitda_margin <= p30 x1.4 | if sales_growth_1y >= p85 x1.3 | if sales_growth_1y <= p10 x1.3 | if no_history x1.2
      mechanism: A revenue multiple is a margin times an earnings multiple, so it is hardest to pin down when the eventual margin is genuinely open: firms with a high gross margin but a low EBITDA margin could become very profitable if selling, marketing and R&D scale down, and the market's guess of that terminal margin varies widely. This headroom is a joint property of the two margins, so it is a two-clause condition rather than separate linear margin terms (which over-covered high-R&D firms). Thin sectors, peer disagreement, growth-tail transitions and new listings weaken the anchor independently.
      prediction: Interval score below 4.05 and below g02-05's 4.153, with highest_rnd_20pct coverage between 77% and 83% and fallback_or_few_peers coverage at or above 79%.

  (5) g04-S3 growth options priced on revenue
      rule: EV/Sales | base constant | terms debt_to_assets -0.5, n_peers -0.5, log_sales -0.3 | if rnd_intensity >= p75 AND sales_growth_1y >= p70 x1.4 | if sales_growth_1y <= p10 x1.3 | if negative_ebitda x1.25 | if no_history x1.2
      mechanism: Firms that both spend heavily on R&D and are growing fast are priced on growth options whose value depends on future scale, so their revenue multiples spread widely even among close peers; R&D-heavy firms that are not growing, or fast growers without R&D, are priced closer to their peers. Earlier linear R&D and growth terms over-covered both groups (about 90%), so the channel enters only as their joint condition. Debt-heavy EVs are damped by near-face-value debt, thin sectors weaken the anchor, and collapsing sales, negative EBITDA and new listings break the run-rate assumption.
      prediction: Interval score below the constant band's 4.233 and below g03-06's 4.171, with fastest_growing_20pct and highest_rnd_20pct coverage both between 77% and 84%.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}
