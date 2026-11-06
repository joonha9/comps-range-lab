"""Create agent runs or advance each by one stage (independent runs advance in parallel).

    python3 scripts/agent_step.py --new a1 a2 a3 a4 a5     # create runs, grade random controls, write gen-1 briefs
    python3 scripts/agent_step.py --runs a1 a2 a3 a4 a5    # process any replies that are ready

For each run: when proposals.txt exists, proposals are validated and the critic brief is written;
when verdicts.txt exists, approved rules are graded and the next proposer brief is written.
Prints the file each run now waits on.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rangelab import agents as ag  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--new", nargs="*", default=[])
ap.add_argument("--runs", nargs="*", default=[])
ap.add_argument("--no-critic", action="store_true")
a = ap.parse_args()


def brief(run: ag.Run, g: int) -> None:
    p = run.gen_dir(g) / "proposer_prompt.md"
    p.write_text(ag.proposer_prompt(run, g))
    run.save_state({"generation": g, "stage": "awaiting_proposals"})
    print(f"{run.name} gen{g}: PROPOSER {p.relative_to(ROOT)}")


for i, name in enumerate(a.new):
    run = ag.Run(name, {"critic": not a.no_critic, "random_seed": 1000 + i})
    ag.run_random(run, run.config["random_seed"])
    print(f"{name}: random control graded ({len(run.archive('random'))} rules)")
    brief(run, 1)

for name in a.runs:
    run = ag.Run(name)
    st, g = run.state, run.state["generation"]
    gd = run.gen_dir(g) if g else None
    if st["stage"] == "awaiting_proposals" and (gd / "proposals.txt").exists():
        try:
            reply = ag.parse_json_reply((gd / "proposals.txt").read_text())
        except Exception as e:  # malformed reply: archive nothing, ask again
            print(f"{name} gen{g}: could not parse proposals ({e}); re-run the proposer")
            continue
        pending = ag.register_proposals(run, reply, g)
        if run.config["critic"] and pending:
            (gd / "critic_prompt.md").write_text(ag.critic_prompt(run, pending))
            run.save_state({"generation": g, "stage": "awaiting_verdicts"})
            print(f"{name} gen{g}: {len(pending)} to critic -> CRITIC {(gd / 'critic_prompt.md').relative_to(ROOT)}")
            continue
        verdicts = None
    elif st["stage"] == "awaiting_verdicts" and (gd / "verdicts.txt").exists():
        try:
            verdicts = ag.parse_json_reply((gd / "verdicts.txt").read_text())
        except Exception as e:
            print(f"{name} gen{g}: could not parse verdicts ({e}); re-run the critic")
            continue
    else:
        print(f"{name}: waiting ({st})")
        continue
    recs = ag.apply_verdicts(run, verdicts, g)
    best = [r["explore"]["interval_score"] for r in recs if r.get("explore")]
    print(f"{name} gen{g}: graded {len(best)}/{len(recs)}" + (f", best {min(best):.3f}" if best else ""))
    if g < run.config["generations"]:
        brief(run, g + 1)
    else:
        run.save_state({"generation": g, "stage": "complete"})
        print(f"{name}: search complete {ag.funnel(run.archive())}")
