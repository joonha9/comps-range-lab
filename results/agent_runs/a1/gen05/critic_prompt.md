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
  [g04-01] EV/EBITDA | base constant | terms log_sales -0.8, ebitda_margin -0.7, gross_margin +0.5, debt_to_assets -0.3 | if sales_growth_1y >= p85 x1.25 | if sales_growth_1y <= p10 x1.25 | if loss_making x1.25 | if no_history x1.2
  [g04-02] EV/EBITDA | base constant | terms log_sales -0.8, ebitda_margin -0.6, net_debt_to_ebitda -0.5, rnd_intensity +0.3 | if loss_making x1.25 | if sales_growth_1y >= p85 x1.25 | if sales_growth_1y <= p10 x1.25
  [g04-03] EV/EBITDA | base constant | terms log_sales -0.8, ebitda_margin -0.5, debt_to_assets -0.3 | if rnd_intensity >= p75 AND ebitda_margin <= p35 x1.35 | if sales_growth_1y >= p85 x1.25 | if sales_growth_1y <= p10 x1.2 | if loss_making x1.25
  [g04-04] EV/Sales | base constant | terms n_peers -0.5, debt_to_assets -0.4, peer_range +0.3, log_assets -0.2 | if net_debt_to_ebitda <= p15 AND ebitda_margin >= p30 x1.3 | if sales_growth_1y >= p85 x1.3 | if sales_growth_1y <= p10 x1.25 | if negative_ebitda x1.25
  [g04-05] EV/Sales | base constant | terms n_peers -0.6, peer_range +0.3, log_assets -0.3 | if gross_margin >= p70 AND ebitda_margin <= p30 x1.4 | if sales_growth_1y >= p85 x1.3 | if sales_growth_1y <= p10 x1.3 | if no_history x1.2
  [g04-06] EV/Sales | base constant | terms debt_to_assets -0.5, n_peers -0.5, log_sales -0.3 | if rnd_intensity >= p75 AND sales_growth_1y >= p70 x1.4 | if sales_growth_1y <= p10 x1.3 | if negative_ebitda x1.25 | if no_history x1.2

PROPOSALS
  (0) g05-01_ebitda_net_cash_tail
      rule: EV/EBITDA | base constant | terms log_sales -0.8, ebitda_margin -0.6, debt_to_assets -0.3, rnd_intensity +0.3 | if net_debt_to_ebitda <= p15 x1.35 | if sales_growth_1y >= p85 x1.25 | if sales_growth_1y <= p10 x1.25 | if loss_making x1.25
      mechanism: EV is market capitalization minus net cash, so when a firm holds net cash that is large relative to EBITDA, EV is a small residual and the same percentage uncertainty in equity value becomes a much larger percentage error in EV. The market also disagrees about how much idle or trapped cash is worth. This effect is concentrated in the net-cash tail and is not linear across leverage, so it enters as a condition. Debt-heavy firms get the opposite, a mild linear damping, because near-face-value debt makes up most of their EV. Size, thin margins, R&D expensing, losses and transitions in either growth tail remain as separate channels.
      prediction: EV/EBITDA interval score below 2.505 (g04-02, linear net_debt_to_ebitda term); coverage of the net-cash tail (net_debt_to_ebitda <= p15) within 75-85%, with no firm type below 75%.

  (1) g05-02_ebitda_below_the_line_gap
      rule: EV/EBITDA | base constant | terms log_sales -0.8, ebitda_margin -0.5, net_debt_to_ebitda -0.4, rnd_intensity +0.3 | if ebitda_margin >= p40 AND net_margin <= p20 x1.35 | if sales_growth_1y >= p85 x1.25 | if sales_growth_1y <= p10 x1.25 | if loss_making x1.2
      mechanism: When EBITDA margin is healthy but net margin is thin, large charges sit between EBITDA and the bottom line: amortization of acquired intangibles, heavy depreciation, impairments or restructuring. Investors disagree about whether these are real recurring economic costs or accounting noise, so firms with the same EBITDA get very different EVs. A firm whose EBITDA and net income tell the same story has no such ambiguity. This is a joint property of the two margins, so it enters as a two-clause condition rather than as a linear net-margin term.
      prediction: EV/EBITDA interval score below 2.52; firms meeting the gap condition (ebitda_margin >= p40 and net_margin <= p20) are covered at roughly 80% instead of below 75% under the constant band.

  (2) g05-03_ebitda_small_and_thin_compounding
      rule: EV/EBITDA | base constant | terms log_sales -0.5, ebitda_margin -0.4, net_debt_to_ebitda -0.5, rnd_intensity +0.3 | if log_sales <= p25 AND ebitda_margin <= p30 x1.4 | if sales_growth_1y >= p85 x1.25 | if sales_growth_1y <= p10 x1.25 | if loss_making x1.2
      mechanism: Thin EBITDA margins and small size compound each other rather than simply adding up. In a small firm with a thin margin, a cost shock can wipe out a large share of EBITDA, and illiquidity and thin analyst coverage leave the market's normalized-earnings guess poorly anchored. Distress and survival outcomes then dominate EV in a way that peers do not share. Large thin-margin firms, such as distributors, and small high-margin niche firms are each priced close to their peers. So the joint tail gets its own condition, and the linear size and margin terms are lighter.
      prediction: EV/EBITDA interval score below 2.52; coverage of the smallest 20% between 77% and 83% without over-covering large firms, and median range no wider than x/2.00.

  (3) g05-04_sales_margin_tail_mismatch
      rule: EV/Sales | base constant | terms n_peers -0.6, peer_range +0.3, log_assets -0.3 | if ebitda_margin >= p90 x1.3 | if ebitda_margin <= p10 x1.3 | if sales_growth_1y >= p85 x1.3 | if sales_growth_1y <= p10 x1.3
      mechanism: EV/Sales is roughly the EBITDA margin times an earnings multiple, and the point estimate takes peers that are nearest on margin within the 2-digit SIC. At the extremes of the margin distribution there are few genuinely comparable peers, so the nearest peers are less extreme than the target. Because the multiple scales with margin, the peer median is systematically off for very high-margin firms (royalty-like, software, pipelines) and for near-zero or negative-margin firms. This U-shape in margin cannot be expressed by a linear margin term, so each tail gets its own condition, alongside the weak-anchor channel (thin or dispersed sector) and the run-rate channel in the growth tails.
      prediction: EV/Sales interval score below 4.052 (g03-04); firms in the top and bottom margin deciles are covered at 76-84%, versus under 75% under the constant band.

  (4) g05-05_sales_precommercial_rnd
      rule: EV/Sales | base constant | terms n_peers -0.5, debt_to_assets -0.4, log_assets -0.3 | if rnd_intensity >= p80 AND negative_ebitda x1.5 | if sales_growth_1y >= p85 x1.3 | if sales_growth_1y <= p10 x1.3 | if no_history x1.2
      mechanism: In R&D-heavy firms with negative EBITDA (pre-commercial biotech, early-stage tech), reported revenue is mostly collaboration, milestone or pilot income. That income has little to do with the pipeline value that drives EV, so sales are a noisy denominator, and EV/Sales can differ from peers by an order of magnitude in either direction. R&D-heavy firms that are already profitable, and loss-makers without heavy R&D, have revenue that is a genuine run-rate. The channel is therefore the joint condition, while debt-heavy EVs are damped by near-face-value debt and thin sectors weaken the anchor.
      prediction: EV/Sales interval score below 4.10; the highest-R&D 20% covered at 78-84% (not about 87% as with linear R&D terms), and loss-making firms covered at least 78%.

  (5) g05-06_sales_assets_not_yet_earning
      rule: EV/Sales | base constant | terms n_peers -0.6, peer_range +0.3, log_sales -0.3 | if asset_turnover <= p10 x1.35 | if sales_growth_1y >= p85 x1.3 | if sales_growth_1y <= p10 x1.3 | if no_history x1.2
      mechanism: When sales are very small relative to total assets, the firm's value sits in assets that do not yet produce, or no longer produce, proportional revenue. Examples are projects under construction, ramping plants, mines and fields before production, and businesses holding large cash or investment balances. EV then tracks the market's valuation of those assets, not current revenue, so a revenue multiple drawn from operating peers transfers poorly. This is a tail effect of very low asset turnover, so it enters as a condition, on top of the weak-anchor channel (thin or dispersed sector) and the run-rate channel (growth tails and new listings).
      prediction: EV/Sales interval score below 4.052 (g03-04); firms with asset_turnover <= p10 covered at 76-84%, and fallback_or_few_peers coverage stays at least 78%.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}
