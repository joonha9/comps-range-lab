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

ARCHIVE: your earlier graded attempts, exploration scores only (21 graded)
  [g04-02] EV/EBITDA interval score 2.505 | coverage 79.8% | median range x/1.99
      EV/EBITDA | base constant | terms log_sales -0.8, ebitda_margin -0.6, net_debt_to_ebitda -0.5, rnd_intensity +0.3 | if loss_making x1.25 | if sales_growth_1y >= p85 x1.25 | if sales_growth_1y <= p10 x1.25
      by firm type: loss_making 78%, smallest_20pct 79%, fastest_growing_20pct 78%, highest_rnd_20pct 79%, fallback_or_few_peers 74%
      mechanism: EV equals equity plus debt minus cash. In firms holding large net cash relative to EBITDA, EV is smaller than market capitalization, so a given percentage uncertainty in the equity value becomes a larger percentage error in EV, and the market additionally disagrees on how much trapped or idle cash is worth. In heavily indebted firms the reverse holds: near-face-value debt dominates EV and damps log errors, which also explains why widening for high net debt (g02-02) scored worse. A single linear net_debt_to_ebitda term captures this whole capital-structure gradient on top of the size and thin-margin channels.
  [g03-03] EV/EBITDA interval score 2.521 | coverage 79.7% | median range x/2.00
      EV/EBITDA | base constant | terms log_sales -0.8, ebitda_margin -0.6, rnd_intensity +0.4 | if sales_growth_1y >= p85 x1.3 | if sales_growth_1y <= p10 x1.3 | if loss_making x1.25 | if no_history x1.2
      by firm type: loss_making 81%, smallest_20pct 77%, fastest_growing_20pct 76%, highest_rnd_20pct 77%, fallback_or_few_peers 75%
      mechanism: Trailing EBITDA is a poor run-rate when the firm is in transition: after an acquisition or explosive ramp (top growth tail), or after a demand collapse or divestiture (bottom tail), and in newly listed firms with no history, the market prices forward earnings that differ sharply from the trailing number in either direction. A linear growth term misses the collapse tail, so both tails get their own condition, on top of the thin-margin, small-size and R&D-expensing channels.
  [g03-02] EV/EBITDA interval score 2.523 | coverage 79.9% | median range x/1.99
      EV/EBITDA | base constant | terms gross_margin +0.6, ebitda_margin -0.7, log_sales -0.8, debt_to_assets -0.3 | if loss_making x1.3
      by firm type: loss_making 79%, smallest_20pct 80%, fastest_growing_20pct 73%, highest_rnd_20pct 79%, fallback_or_few_peers 75%
      mechanism: A firm with a high gross margin but a low EBITDA margin has EBITDA depressed by discretionary opex (selling, marketing, R&D) that may later be cut, so the market values a normalized margin far above current EBITDA, and investors disagree on how much. A firm whose thin EBITDA comes from a thin gross margin has no such headroom and its multiple is pinned by its peers. Separately, in heavily indebted firms most of EV is debt carried near face value, so the uncertain equity is a smaller share of EV and log EV errors shrink.
  [g04-03] EV/EBITDA interval score 2.526 | coverage 79.7% | median range x/2.01
      EV/EBITDA | base constant | terms log_sales -0.8, ebitda_margin -0.5, debt_to_assets -0.3 | if rnd_intensity >= p75 AND ebitda_margin <= p35 x1.35 | if sales_growth_1y >= p85 x1.25 | if sales_growth_1y <= p10 x1.2 | if loss_making x1.25
      by firm type: loss_making 80%, smallest_20pct 78%, fastest_growing_20pct 77%, highest_rnd_20pct 75%, fallback_or_few_peers 75%
      mechanism: Expensing R&D understates the earnings base only when R&D is large relative to what is left over: a mature pharma or semiconductor firm with heavy R&D but a fat EBITDA margin is valued on stable EBITDA, while an R&D-heavy firm with thin EBITDA is valued on pipeline and growth options that trailing EBITDA cannot measure. This is an interaction, so it enters as a joint condition rather than a linear R&D term that also widens profitable R&D firms. Size, thin margins, losses and growth-tail transitions remain separate channels; debt share of EV damps errors.
  [g02-01] EV/EBITDA interval score 2.540 | coverage 79.9% | median range x/2.00
      EV/EBITDA | base constant | terms log_sales -0.8, ebitda_margin -0.6, rnd_intensity +0.5, sales_growth_1y +0.4 | if loss_making x1.3
      by firm type: loss_making 79%, smallest_20pct 77%, fastest_growing_20pct 79%, highest_rnd_20pct 80%, fallback_or_few_peers 75%
      mechanism: Two separate things make trailing EV/EBITDA unreliable. First, when EBITDA is a thin slice of sales, small cost shocks swing it by large percentages, so the market prices normalized rather than current EBITDA (made worse in small and loss-making firms). Second, R&D-heavy and fast-growing firms expense investment that is economically capex, so current EBITDA understates the earnings base on which EV is set. A rule with only one channel leaves the other group under-covered.
  [g01-01] EV/EBITDA interval score 2.571 | coverage 79.8% | median range x/2.05
      EV/EBITDA | base constant | terms log_sales -1, ebitda_margin -0.8 | if loss_making x1.4
      by firm type: loss_making 83%, smallest_20pct 78%, fastest_growing_20pct 72%, highest_rnd_20pct 71%, fallback_or_few_peers 75%
      mechanism: When EBITDA is a small slice of sales, a given dollar shock to costs moves EBITDA by a large percentage, so the market prices the firm off normalized rather than current EBITDA and the trailing multiple is noisy. Small firms add idiosyncratic risk, illiquidity and thin analyst coverage, so peers' multiples transfer poorly; loss-making firms with positive EBITDA have earnings below the line (interest, D&A, write-offs) that the multiple ignores.
  [g01-02] EV/EBITDA interval score 2.606 | coverage 79.6% | median range x/2.01
      EV/EBITDA | base constant | terms rnd_intensity +0.8, sales_growth_1y +0.6, log_assets -0.7 | if no_history x1.5
      by firm type: loss_making 69%, smallest_20pct 77%, fastest_growing_20pct 81%, highest_rnd_20pct 83%, fallback_or_few_peers 75%
      mechanism: Firms that expense heavy R&D and grow fast have current EBITDA depressed by investment that is really capital spending, so their EV reflects growth options that trailing EBITDA cannot capture and that differ greatly from peer to peer. Recently listed or newly covered firms (no prior-year sales) have short track records, so investors disagree more about their steady-state earnings.
  [g02-03] EV/EBITDA interval score 2.608 | coverage 79.8% | median range x/2.08
      EV/EBITDA | base constant | terms log_sales -0.8, net_margin -0.5 | if sales_growth_1y >= p85 x1.3 | if sales_growth_1y <= p10 x1.3
      by firm type: loss_making 79%, smallest_20pct 75%, fastest_growing_20pct 76%, highest_rnd_20pct 70%, fallback_or_few_peers 78%
      mechanism: A firm whose sales just jumped or collapsed is likely at a cyclical or event-driven peak or trough (acquisition, divestiture, lost contract), so trailing EBITDA is a poor proxy for the run-rate the market values. Investors look through it and the multiple swings far from peers in either direction. The relationship is U-shaped in growth, which a single linear growth term cannot capture, so both tails get their own condition, on top of size and net-margin scaling.
  [g02-02] EV/EBITDA interval score 2.637 | coverage 79.7% | median range x/2.04
      EV/EBITDA | base constant | terms capex_intensity +0.5, ebit_margin -0.7, log_sales -0.7 | if net_debt_to_ebitda >= p85 x1.25
      by firm type: loss_making 78%, smallest_20pct 74%, fastest_growing_20pct 72%, highest_rnd_20pct 69%, fallback_or_few_peers 81%
      mechanism: EBITDA comes before depreciation and capex. In capital-intensive firms where D&A and reinvestment eat most of EBITDA, the earnings investors actually value (EBIT, free cash flow) are a small, volatile residual, so the same EBITDA supports very different EVs across peers. When net debt is large relative to EBITDA, equity is a thin levered claim whose value depends on refinancing and covenant risk, which adds dispersion that peers with ordinary leverage do not share.
  [g01-03] EV/EBITDA interval score 2.661 | coverage 79.9% | median range x/2.07
      EV/EBITDA | base constant | terms roic -0.8, log_sales -0.8 | if ebitda_margin <= p20 x1.4 | if debt_to_assets >= p80 AND ebit_margin <= p30 x1.3
      by firm type: loss_making 82%, smallest_20pct 77%, fastest_growing_20pct 73%, highest_rnd_20pct 70%, fallback_or_few_peers 81%
      mechanism: Firms earning low returns on invested capital are valued closer to their asset base or liquidation and restructuring outcomes than to a going-concern multiple of EBITDA, so earnings-based comps describe them poorly. Highly levered firms with thin margins carry distress and refinancing risk, and that risk moves the debt and equity parts of EV in ways the peers do not share.
  [g03-04] EV/Sales interval score 4.052 | coverage 79.9% | median range x/3.09
      EV/Sales | base constant | terms n_peers -0.6, peer_range +0.3, log_assets -0.3 | if sales_growth_1y >= p85 x1.3 | if sales_growth_1y <= p10 x1.3 | if no_history x1.2 | if negative_ebitda x1.25
      by firm type: loss_making 79%, smallest_20pct 80%, fastest_growing_20pct 82%, highest_rnd_20pct 81%, fallback_or_few_peers 82%
      mechanism: EV/Sales comps fail for two independent reasons. The anchor is weak when the 2-digit SIC sector is thin or its peers disagree, because the nearest peers come from different business models. And trailing sales are not the revenue run-rate after a big acquisition, divestiture, demand collapse or ramp, or for new listings, so the multiple departs from peers in both directions. Earlier rules each fixed one channel; combining them should cover both under-covered groups without heavy size weights that over-cover small firms.
  [g02-04] EV/Sales interval score 4.079 | coverage 80.0% | median range x/3.15
      EV/Sales | base constant | terms n_peers -0.6, log_sales -0.4, peer_range +0.3 | if negative_ebitda x1.3
      by firm type: loss_making 79%, smallest_20pct 79%, fastest_growing_20pct 78%, highest_rnd_20pct 81%, fallback_or_few_peers 83%
      mechanism: When a 2-digit SIC sector is thin, the 'nearest' peers are forced from businesses that differ in model and margin structure, so the peer median EV/Sales is a weak anchor. These fallback firms are the only group the constant band under-covers that earlier rules never fixed. Size adds idiosyncratic and liquidity noise but only mildly: earlier rules that weighted size and margin heavily over-covered small and loss-making firms (about 90%) and scored worse than the constant band, so this rule keeps those weights low and adds peer dispersion only as a moderate term.
  [g04-05] EV/Sales interval score 4.097 | coverage 80.0% | median range x/3.12
      EV/Sales | base constant | terms n_peers -0.6, peer_range +0.3, log_assets -0.3 | if gross_margin >= p70 AND ebitda_margin <= p30 x1.4 | if sales_growth_1y >= p85 x1.3 | if sales_growth_1y <= p10 x1.3 | if no_history x1.2
      by firm type: loss_making 78%, smallest_20pct 77%, fastest_growing_20pct 83%, highest_rnd_20pct 81%, fallback_or_few_peers 82%
      mechanism: A revenue multiple is a margin times an earnings multiple, so it is hardest to pin down when the eventual margin is genuinely open: firms with a high gross margin but a low EBITDA margin could become very profitable if selling, marketing and R&D scale down, and the market's guess of that terminal margin varies widely. This headroom is a joint property of the two margins, so it is a two-clause condition rather than separate linear margin terms (which over-covered high-R&D firms). Thin sectors, peer disagreement, growth-tail transitions and new listings weaken the anchor independently.
  [g04-04] EV/Sales interval score 4.098 | coverage 80.0% | median range x/3.07
      EV/Sales | base constant | terms n_peers -0.5, debt_to_assets -0.4, peer_range +0.3, log_assets -0.2 | if net_debt_to_ebitda <= p15 AND ebitda_margin >= p30 x1.3 | if sales_growth_1y >= p85 x1.3 | if sales_growth_1y <= p10 x1.25 | if negative_ebitda x1.25
      by firm type: loss_making 78%, smallest_20pct 80%, fastest_growing_20pct 84%, highest_rnd_20pct 83%, fallback_or_few_peers 78%
      mechanism: An EV/Sales comp effectively prices equity plus net debt; debt is nearly a fixed claim, so in debt-heavy firms the uncertain equity is a small share of EV and log errors shrink, while profitable firms sitting on large net cash have EV below market capitalization, so equity uncertainty is amplified in EV. The peer anchor is also weak in thin or dispersed sectors, and trailing sales misstate the run-rate in both growth tails and for firms with negative EBITDA whose value depends on future margins.
  [g04-06] EV/Sales interval score 4.117 | coverage 79.9% | median range x/3.05
      EV/Sales | base constant | terms debt_to_assets -0.5, n_peers -0.5, log_sales -0.3 | if rnd_intensity >= p75 AND sales_growth_1y >= p70 x1.4 | if sales_growth_1y <= p10 x1.3 | if negative_ebitda x1.25 | if no_history x1.2
      by firm type: loss_making 79%, smallest_20pct 81%, fastest_growing_20pct 81%, highest_rnd_20pct 86%, fallback_or_few_peers 79%
      mechanism: Firms that both spend heavily on R&D and are growing fast are priced on growth options whose value depends on future scale, so their revenue multiples spread widely even among close peers; R&D-heavy firms that are not growing, or fast growers without R&D, are priced closer to their peers. Earlier linear R&D and growth terms over-covered both groups (about 90%), so the channel enters only as their joint condition. Debt-heavy EVs are damped by near-face-value debt, thin sectors weaken the anchor, and collapsing sales, negative EBITDA and new listings break the run-rate assumption.
  [g02-06] EV/Sales interval score 4.124 | coverage 80.0% | median range x/3.15
      EV/Sales | base constant | terms log_assets -0.3 | if sales_growth_1y >= p85 x1.35 | if sales_growth_1y <= p10 x1.3 | if no_history x1.25
      by firm type: loss_making 76%, smallest_20pct 75%, fastest_growing_20pct 81%, highest_rnd_20pct 77%, fallback_or_few_peers 72%
      mechanism: EV/Sales assumes trailing sales represent the firm's revenue run-rate. After a big acquisition, a divestiture, a collapse in demand or an explosive ramp, they do not: the market values forward revenue that is far above or below trailing sales, so the multiple departs from peers in both directions. Newly listed firms with no prior-year sales are often in exactly this kind of transition. This is a U-shaped growth effect plus a history flag, not a size or margin effect.
  [g02-05] EV/Sales interval score 4.153 | coverage 80.0% | median range x/3.14
      EV/Sales | base constant | terms gross_margin +0.6, ebitda_margin -0.6, log_sales -0.3
      by firm type: loss_making 78%, smallest_20pct 77%, fastest_growing_20pct 79%, highest_rnd_20pct 85%, fallback_or_few_peers 70%
      mechanism: A firm with a high gross margin but a low EBITDA margin spends heavily on discretionary opex (selling, marketing, R&D) that could in principle be cut. Its EV depends on whether the market thinks that spending will scale down into high mature margins, a judgment that varies widely across firms with similar current economics. A firm whose low gross margin limits its EBITDA has no such headroom, and its revenue multiple is pinned by structurally thin margins.
  [g03-06] EV/Sales interval score 4.171 | coverage 79.9% | median range x/3.07
      EV/Sales | base constant | terms debt_to_assets -0.5, rnd_intensity +0.4, n_peers -0.5, log_sales -0.3 | if negative_ebitda x1.3
      by firm type: loss_making 79%, smallest_20pct 81%, fastest_growing_20pct 80%, highest_rnd_20pct 87%, fallback_or_few_peers 78%
      mechanism: EV is equity plus net debt, and debt is close to a fixed claim, so in heavily indebted firms the uncertain equity is a smaller share of EV and the log error of an EV-based comp shrinks; earlier rules that widened ranges for high leverage scored worse, which fits this. R&D-intensive firms are the opposite: almost all their EV is equity priced on intangible growth options that revenue barely measures. Thin sectors weaken the peer anchor for everyone.
  [g01-04] EV/Sales interval score 4.447 | coverage 79.9% | median range x/2.93
      EV/Sales | base constant | terms ebitda_margin -1, log_sales -0.8 | if negative_ebitda x1.6 | if no_history x1.3
      by firm type: loss_making 88%, smallest_20pct 90%, fastest_growing_20pct 80%, highest_rnd_20pct 89%, fallback_or_few_peers 74%
      mechanism: EV/Sales is essentially a margin times an earnings multiple, so it transfers across firms only when they have similar margins; when a firm's EBITDA margin is low or negative, its value rests on the market's guess of future margins rather than current economics, and that guess varies widely. Small firms add idiosyncratic and liquidity noise on top of this.
  [g01-06] EV/Sales interval score 4.469 | coverage 79.9% | median range x/3.21
      EV/Sales | base constant | terms log_sales -1, peer_iqr +0.5, net_margin -0.6 | if loss_making AND log_sales <= p30 x1.5 | if debt_to_assets >= p80 x1.3
      by firm type: loss_making 88%, smallest_20pct 91%, fastest_growing_20pct 80%, highest_rnd_20pct 87%, fallback_or_few_peers 73%
      mechanism: Small, loss-making firms with heavy debt have option-like equity whose value depends on survival rather than on revenue, so EV/Sales drawn from healthier peers misprices them in either direction. Where peers themselves disagree strongly, the sector holds several business models, and the median multiple is a less reliable anchor; this enters as a moderate term rather than the base because a pure peer_iqr scaling overweights it.
  [g01-05] EV/Sales interval score 4.649 | coverage 79.9% | median range x/3.32
      EV/Sales | base constant | terms gross_margin +0.8, rnd_intensity +0.7, sales_growth_1y +0.7, log_assets -0.6
      by firm type: loss_making 77%, smallest_20pct 80%, fastest_growing_20pct 90%, highest_rnd_20pct 92%, fallback_or_few_peers 66%
      mechanism: High gross margin, R&D-intensive, fast-growing firms (software and biotech style) are valued on scalable future margins, so their revenue multiples spread over an order of magnitude even within a 2-digit SIC code, and a peer median is a weak anchor. Low-gross-margin, slow-growing distributors and manufacturers trade in narrow revenue-multiple bands set by their thin, stable margins.

FAILED OR REJECTED ATTEMPTS (most recent)
  [g03-01] rejected: critic: The prediction that capital-intensive firms are over-covered by a constant band means they are easier to value than average, which contradicts the mechanism and the +0.4 capex_intensity weight that widens their r
  [g03-05] rejected: critic: The mechanism says headroom matters most in thin sectors (an interaction), but adding gross_margin and n_peers as separate terms in the exponent widens them independently, so this is really g02-05 plus g02-04's p
  [g04-01] rejected: critic: This is a mechanical splice of g03-02's linear terms (identical inputs and near-identical weights) with g03-03's growth-tail, loss and no_history conditions, minus R&D, so it adds no input, condition or economic 

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
