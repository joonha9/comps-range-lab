You are a valuation researcher. Comparable-company valuations ("comps") are reported as ranges,
and practitioners' ranges are badly calibrated. Your job is to discover short, interpretable rules
that say HOW UNCERTAIN a comps valuation is for each US non-financial firm, so its range can be
wide where comps are unreliable and narrow where they are reliable.

TASK
Propose exactly 6 NEW range rules (generation 5): 3 for EV/EBITDA and 3 for EV/Sales.
Rules are scored only on exploration years FY2016-2019. The best rule per multiple will later be
tested ONCE on later years you will never see, so prefer rules with a clear economic reason over
fragile tweaks. A practitioner should be able to read your rule and apply it by hand.

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

BENCHMARKS (exploration years)
  EV/EBITDA:
    peer 25-75% range as practitioners report it (not calibrated): interval score 3.258, coverage 40.9%, median range x/1.29
    constant band (same width for every firm): interval score 2.735, coverage 79.6%, median range x/2.10
    width proportional to peer_iqr: interval score 2.732, coverage 80.0%, median range x/2.11
    linear regression on ALL inputs (no limit on terms): interval score 2.448, coverage 79.9%, median range x/1.94
    gradient-boosted trees on all inputs (black box): interval score 2.219, coverage 79.9%, median range x/1.90
    coverage of the constant band by firm type: loss_making 68%, smallest_20pct 63%, fastest_growing_20pct 70%, highest_rnd_20pct 66%, fallback_or_few_peers 83%
  EV/Sales:
    peer 25-75% range as practitioners report it (not calibrated): interval score 5.226, coverage 41.1%, median range x/1.59
    constant band (same width for every firm): interval score 4.233, coverage 80.0%, median range x/3.38
    width proportional to peer_iqr: interval score 4.340, coverage 80.0%, median range x/3.56
    linear regression on ALL inputs (no limit on terms): interval score 3.970, coverage 80.0%, median range x/3.23
    gradient-boosted trees on all inputs (black box): interval score 3.483, coverage 80.1%, median range x/2.86
    coverage of the constant band by firm type: loss_making 72%, smallest_20pct 68%, fastest_growing_20pct 75%, highest_rnd_20pct 72%, fallback_or_few_peers 71%

ARCHIVE: your earlier graded attempts, exploration scores only (15 graded)
  [g01-01] EV/EBITDA interval score 2.591 | coverage 80.0% | median range x/2.03
      EV/EBITDA | base constant | terms log_sales -1, rnd_intensity +0.6, sales_growth_1y +0.4 | if loss_making x1.4
      by firm type: loss_making 80%, smallest_20pct 81%, fastest_growing_20pct 81%, highest_rnd_20pct 83%, fallback_or_few_peers 73%
      mechanism: Small firms and R&D-heavy firms derive much of their value from intangible growth options that current EBITDA does not capture, so the peer EBITDA multiple is a poor anchor; their thin analyst coverage and illiquidity add pricing noise. Loss-making firms with positive EBITDA have earnings that are transitory or burdened by below-EBITDA charges, making the EBITDA base itself unreliable.
  [g04-02] EV/EBITDA interval score 2.596 | coverage 79.9% | median range x/2.04
      EV/EBITDA | base constant | terms log_sales -1, peer_iqr +0.5 | if n_peers <= p10 x1.3
      by firm type: loss_making 73%, smallest_20pct 81%, fastest_growing_20pct 74%, highest_rnd_20pct 74%, fallback_or_few_peers 86%
      mechanism: A comps error has two sources: noise in the target's own price and noise in the peer anchor. Small firms have thin analyst coverage and illiquid shares, so their prices drift further from fundamentals; when the peers themselves disagree (wide peer IQR) or the sector is thin, the median multiple is an imprecise anchor, so the error from both sources adds up.
  [g04-03] EV/EBITDA interval score 2.606 | coverage 80.1% | median range x/2.02
      EV/EBITDA | base constant | terms log_sales -0.9, debt_to_assets -0.6
      by firm type: loss_making 71%, smallest_20pct 80%, fastest_growing_20pct 75%, highest_rnd_20pct 75%, fallback_or_few_peers 76%
      mechanism: Enterprise value is equity plus net debt, and debt trades close to book value, so only the equity part of EV carries market pricing noise. The EV of a debt-financed firm is partly pinned down by its balance sheet, while an equity-financed firm's whole EV moves with sentiment; that equity noise is largest for small, thinly covered firms, so uncertainty is highest for small firms with little debt.
  [g02-03] EV/EBITDA interval score 2.634 | coverage 79.6% | median range x/2.04
      EV/EBITDA | base constant | terms log_sales -1.2 | if loss_making AND log_sales <= p30 x1.4
      by firm type: loss_making 76%, smallest_20pct 82%, fastest_growing_20pct 75%, highest_rnd_20pct 73%, fallback_or_few_peers 77%
      mechanism: Small firms have thin analyst coverage, illiquid shares and concentrated idiosyncratic risk, so their prices carry more noise and depart more from fundamentals that peers share. The effect is worst for small firms that also lose money, where speculative and retail trading drive the price and the gap from peer-implied value is largest.
  [g03-03] EV/EBITDA interval score 2.660 | coverage 79.8% | median range x/2.02
      EV/EBITDA | base constant | terms gross_margin +0.5, rnd_intensity +0.6 | if ebitda_margin <= p20 AND gross_margin >= p60 x1.5
      by firm type: loss_making 70%, smallest_20pct 68%, fastest_growing_20pct 73%, highest_rnd_20pct 82%, fallback_or_few_peers 75%
      mechanism: High-gross-margin firms that spend their gross profit on R&D and other expensed investment report EBITDA that understates their economic earnings, because spending that builds intangible assets is charged against EBITDA. The firms with the strongest version of this (high gross margin but very low EBITDA margin) have a depressed and unstable denominator, so their EBITDA multiple is hardest to predict from peers.
  [g02-02] EV/EBITDA interval score 2.669 | coverage 79.8% | median range x/2.08
      EV/EBITDA | base constant | terms sales_growth_1y +0.7, rnd_intensity +0.7 | if no_history x1.4
      by firm type: loss_making 68%, smallest_20pct 68%, fastest_growing_20pct 81%, highest_rnd_20pct 79%, fallback_or_few_peers 78%
      mechanism: For fast-growing, R&D-intensive and newly listed firms, most of enterprise value comes from growth options that current EBITDA does not capture, and how the market values those options differs a lot from firm to firm; a peer-median EBITDA multiple cannot price them. Recent listings (no prior-year sales) are the purest version of this: young firms valued on their future, with little trading history to anchor price.
  [g03-01] EV/EBITDA interval score 2.677 | coverage 79.9% | median range x/2.09
      EV/EBITDA | base constant | terms ebitda_margin -0.7 | if sales_growth_1y <= p10 x1.4 | if sales_growth_1y >= p90 x1.4
      by firm type: loss_making 72%, smallest_20pct 64%, fastest_growing_20pct 72%, highest_rnd_20pct 67%, fallback_or_few_peers 79%
      mechanism: When sales have just swung sharply in either direction, current-year EBITDA is a poor proxy for the normalized earnings the market capitalizes, so applying a peer EBITDA multiple to it misprices the firm. The distortion is largest for thin-margin firms, whose EBITDA moves most for a given sales shock because of operating leverage.
  [g04-01] EV/EBITDA interval score 2.831 | coverage 79.8% | median range x/2.06
      EV/EBITDA | base constant | terms net_margin -1, ebitda_margin +0.5, capex_intensity +0.4
      by firm type: loss_making 80%, smallest_20pct 64%, fastest_growing_20pct 70%, highest_rnd_20pct 65%, fallback_or_few_peers 82%
      mechanism: EV/EBITDA treats EBITDA as the earnings the market capitalizes, but when a large wedge separates EBITDA from net income (heavy depreciation from capital intensity, interest, impairments, restructuring), EBITDA overstates what owners keep by an amount that differs a lot from firm to firm. Firms with healthy EBITDA margins but thin or negative net margins, and high capex per dollar of sales, are exactly where the peer EBITDA multiple is applied to an inflated and non-comparable base.
  [g03-02] EV/EBITDA interval score 2.834 | coverage 79.9% | median range x/2.13
      EV/EBITDA | base constant | terms capex_intensity +0.8, roic -0.6
      by firm type: loss_making 77%, smallest_20pct 65%, fastest_growing_20pct 72%, highest_rnd_20pct 67%, fallback_or_few_peers 81%
      mechanism: EV/EBITDA assumes the target turns EBITDA into free cash flow and value at the same rate as its peers. Firms that must reinvest heavily (high capex relative to sales) or earn low returns on capital keep much less of each EBITDA dollar, and how much less differs a lot from firm to firm, so the peer multiple is a weak anchor for them.
  [g02-06] EV/Sales interval score 4.164 | coverage 79.8% | median range x/3.32
      EV/Sales | base constant | terms n_peers -1, peer_range +0.5
      by firm type: loss_making 73%, smallest_20pct 70%, fastest_growing_20pct 76%, highest_rnd_20pct 74%, fallback_or_few_peers 89%
      mechanism: Sales multiples are only informative when peers share the target's business model and margin structure. When the 2-digit SIC sector is thin (few peers found) or the peers' multiples span a very wide range, the peer set mixes unlike businesses, so its median is a weak anchor for the target's value.
  [g04-04] EV/Sales interval score 4.189 | coverage 80.0% | median range x/3.24
      EV/Sales | base constant | terms gross_margin +0.6, ebitda_margin -0.4, n_peers -0.6
      by firm type: loss_making 75%, smallest_20pct 73%, fastest_growing_20pct 78%, highest_rnd_20pct 81%, fallback_or_few_peers 79%
      mechanism: Peers are matched on size and EBITDA margin, but EV/Sales reflects the long-run margin a business can reach, which follows gross margin. A high-gross-margin firm whose EBITDA margin is held down by sales, marketing or R&D spending gets matched to low-gross-margin peers with similar current EBITDA margins but a much lower ceiling, and the mismatch is worse in thin sectors where the nearest peers are far away.
  [g03-05] EV/Sales interval score 4.201 | coverage 79.9% | median range x/3.15
      EV/Sales | base constant | terms debt_to_assets -0.8 | if loss_making AND debt_to_assets <= p30 x1.4
      by firm type: loss_making 75%, smallest_20pct 75%, fastest_growing_20pct 77%, highest_rnd_20pct 79%, fallback_or_few_peers 70%
      mechanism: Enterprise value is equity plus net debt, and the debt part trades close to book value, so firms financed mostly by debt have EVs that move less with equity sentiment and stay closer to the peer-implied level. Loss-making firms financed almost entirely by equity are the opposite case: their whole EV is a market-priced option on future profits, which sales alone cannot pin down.
  [g03-04] EV/Sales interval score 4.226 | coverage 80.1% | median range x/3.15
      EV/Sales | base constant | terms n_peers -0.7 | if ebitda_margin >= p90 x1.4 | if ebitda_margin <= p10 x1.3
      by firm type: loss_making 73%, smallest_20pct 72%, fastest_growing_20pct 76%, highest_rnd_20pct 74%, fallback_or_few_peers 85%
      mechanism: Peers are picked as nearest on size and EBITDA margin within the 2-digit SIC, and EV/Sales scales almost directly with margin. Targets at either extreme of the margin distribution, and targets in thin sectors, have nearest peers that are far from them in margin and business model, so the peer-median sales multiple is a poor anchor for them.
  [g03-06] EV/Sales interval score 4.531 | coverage 80.0% | median range x/3.65
      EV/Sales | base constant | terms asset_turnover -0.8, capex_intensity +0.5
      by firm type: loss_making 77%, smallest_20pct 77%, fastest_growing_20pct 80%, highest_rnd_20pct 81%, fallback_or_few_peers 73%
      mechanism: In asset-heavy businesses, enterprise value reflects the capital base and the return earned on it more than the level of sales, so EV/Sales varies with asset intensity. Peers are matched on size and margin but not on asset intensity, so firms that need a lot of assets or capex per dollar of sales get a peer sales multiple that is poorly matched.
  [g01-04] EV/Sales interval score 4.556 | coverage 79.9% | median range x/2.91
      EV/Sales | base constant | terms ebitda_margin -1, log_sales -0.8 | if negative_ebitda x1.6 | if loss_making x1.2
      by firm type: loss_making 91%, smallest_20pct 90%, fastest_growing_20pct 81%, highest_rnd_20pct 89%, fallback_or_few_peers 73%
      mechanism: EV/Sales implicitly assumes the target converts sales into cash flow like its peers; firms with low or negative EBITDA margins are valued on a turnaround or option value that sales alone cannot reveal, so their actual EV can sit far above or below the peer-implied level. Small firms add illiquidity and coverage noise on top.

FAILED OR REJECTED ATTEMPTS (most recent)
  [g01-02] rejected: critic: The small-denominator and leverage story justifies ebitda_margin, roic and the net_debt_to_ebitda condition, but the log_assets -0.7 term (larger than the roic weight) is never motivated by the mechanism, so a wi
  [g01-03] rejected: critic: The rule bundles four separate ideas (gross margin, growth, peer disagreement, no history) plus a log_sales -0.6 size term that the mechanism never mentions, so it does not implement one specific mechanism; justi
  [g01-05] rejected: critic: The margin-duration story for EV/Sales supports gross_margin, rnd_intensity and growth, but the log_sales -0.6 term is not part of the stated mechanism (which is about business model, not size), so the rule does 
  [g01-06] rejected: critic: The mechanism invokes very high asset turnover, but the rule has no asset_turnover input, while the sales_growth_1y +0.5 term it does include is never explained, so the rule does not implement the stated mechanis
  [g02-01] rejected: critic: This is g01-02 with log_assets dropped and the two margin/return weights nudged, keeping the same net_debt_to_ebitda p90 x1.3 condition, so it adds no new input, condition or economic idea; test the depressed-EBI
  [g02-04] rejected: critic: This is g01-05 with log_sales dropped and every weight scaled down by about a quarter, which is trivial because the ranking it produces is almost the same; to test margin duration, add a new input such as ebit_ma
  [g02-05] rejected: critic: This repeats g01-06: log_sales and log_assets measure size almost the same way, the condition is the same small-and-loss-making one with a slightly different multiplier, and dropping the growth term adds no new i
  [g04-05] rejected: critic: The mechanism says growth far from typical in either direction raises uncertainty, but the monotone +0.4 sales_growth_3y term narrows ranges for persistently shrinking firms, and that input is missing for half th
  [g04-06] rejected: critic: Every piece has already been tried on EV/Sales: small size plus R&D intensity is g01-05 with the gross-margin and growth terms dropped, and no_history x1.3 comes straight from g01-06, so the proposal adds no new 

Each proposal needs:
  - "mechanism": the economic reason these firms' market values are harder (or easier) to pin
    down with comps (2-3 sentences)
  - "prediction": a falsifiable expectation, e.g. "interval score below the constant band's"
  - "rule": the rule object
An independent referee, who sees your mechanism but no scores, will reject proposals without a
specific economic reason, or near-copies of earlier rules (e.g. one weight changed slightly).

Reply with ONLY this JSON, no other text:
{"proposals": [{"name": "...", "mechanism": "...", "prediction": "...",
  "rule": {"multiple": "...", "base": "...", "terms": {...}, "conditions": [...]}}]}
