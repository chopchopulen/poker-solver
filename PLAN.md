# PLAN

Task queue for overnight.sh. Format: `- [ ] ID | model | task | done when: check`. `[x]` = done, `[!]` = blocked (reason in PROGRESS.md).
Long runs go in scripts/ and write to analysis/*.csv. Tests stay under ~10 s total.

## Phase 1: Kuhn + vanilla CFR
- [x] P1.1 | haiku | Scaffold: add __init__.py to games/ solvers/ eval/ agents/ play/ tests/; add scripts/ dir; requirements.txt (numpy, pytest, matplotlib); pytest.ini with testpaths=tests; tests/test_smoke.py that imports every package | done when: `pytest -q` passes
- [x] P1.2 | sonnet | games/base.py: abstract Game class with initial_state, is_terminal, is_chance, chance_outcomes (action, prob), current_player, legal_actions, next_state, utility(state, player), infoset_key(state, player); docstrings on each | done when: test that a subclass missing a method cannot be instantiated passes
- [x] P1.3 | sonnet | games/kuhn.py implementing Game (3 cards, ante 1, bet 1, histories p/b); tests: 6 equally likely deals, every terminal payoff hand-checked against Kuhn rules, infoset key contains only own card + public history | done when: `pytest -q` passes
- [ ] P1.4 | sonnet | solvers/cfr.py: vanilla CFR, full tree traversal, chance nodes weighted by probability, regret matching, average strategy weighted by own reach; eval/game_value.py computes expected value of a strategy profile | done when: test that 2000 iterations gives P1 value within 0.005 of -1/18 passes
- [ ] P1.5 | sonnet | scripts/run_kuhn_cfr.py: 100k iterations, writes analysis/kuhn_cfr.csv (infoset, action probs) and prints one summary line; test (small iters) that average strategy fits the known equilibrium family: P1 bets J with alpha in [0,1/3], bets K with 3*alpha, calls Q with alpha+1/3; P2 bets K/calls K always, bluffs J 1/3 after check, calls Q 1/3 | done when: script runs, value within 1e-3 of -1/18, family test passes
- [ ] P1.6 | sonnet | Docs: LEARNING.md Phase 1 entry (what CFR does, regret matching + average strategy math in LaTeX, 3 Q&As); README Kuhn/CFR sections and run command | done when: both files updated, `pytest -q` passes
- [ ] P1.7 | opus | VERIFY Phase 1: review kuhn.py payoffs and cfr.py math line by line, rerun scripts/run_kuhn_cfr.py, confirm value vs -1/18 and equilibrium family, check LEARNING.md math; fix anything wrong; mark Phase 1 DONE in PROGRESS.md | done when: all checks pass and PROGRESS.md says Phase 1 DONE

## Phase 2: Best response + exploitability
- [ ] P2.1 | sonnet | eval/best_response.py: exact best response value for one player vs a fixed strategy profile (aggregate opponent and chance reach per infoset, then pick best action per infoset) | done when: tests pass: BR value vs CFR Kuhn equilibrium within 1e-3 of game value for each player; BR vs uniform >= value of uniform
- [ ] P2.2 | sonnet | eval/exploitability.py: exploitability = (BR_1(sigma_2) + BR_2(sigma_1)) / 2, plus mbb/hand helper | done when: tests pass: exploitability of CFR 5k-iter Kuhn strategy < 0.01, uniform strategy > 0.05, always >= 0
- [ ] P2.3 | sonnet | scripts/kuhn_convergence.py: vanilla CFR to 100k iters, logs exploitability at log-spaced iterations to analysis/kuhn_convergence.csv (solver, iter, seconds, exploitability), one summary line | done when: csv exists and exploitability at last row < at first row
- [ ] P2.4 | haiku | analysis/plot_convergence.py: log-log plot exploitability vs iterations from the csv, saved to analysis/kuhn_convergence.png; add entry to analysis/results.md with exact reproduce command | done when: png exists, results.md entry has command
- [ ] P2.5 | sonnet | Docs: LEARNING.md Phase 2 entry (best response, exploitability, O(1/sqrt(T)) bound in LaTeX, 3 Q&As); README chart + results row | done when: files updated, `pytest -q` passes
- [ ] P2.6 | opus | VERIFY Phase 2: review best_response.py for infoset aggregation bugs (no peeking at opponent cards), confirm exploitability -> 0, check log-log slope is about -0.5 or better from csv; fix issues; mark Phase 2 DONE in PROGRESS.md | done when: checks pass and PROGRESS.md says Phase 2 DONE

## Phase 3: CFR+
- [ ] P3.1 | sonnet | solvers/cfr_plus.py: regrets floored at 0 (regret-matching+), alternating updates, linearly weighted average strategy | done when: tests pass: Kuhn value within 0.005 of -1/18 after 1000 iters, exploitability < vanilla CFR at same iters
- [ ] P3.2 | sonnet | Extend scripts/kuhn_convergence.py with --solver cfr_plus; append to csv; compute speedup = iters for vanilla to reach exploitability 1e-3 / iters for CFR+, print one summary line and write analysis/kuhn_speedup.csv | done when: both solvers in csv, speedup csv exists
- [ ] P3.3 | haiku | Update plot_convergence.py to draw both solvers on one log-log chart; results.md entry for speedup with command | done when: png shows 2 lines, results.md updated
- [ ] P3.4 | sonnet | Docs: LEARNING.md Phase 3 entry (CFR+ changes and why they speed up convergence, LaTeX, 3 Q&As); README CFR+ row | done when: files updated, `pytest -q` passes
- [ ] P3.5 | opus | VERIFY Phase 3: review cfr_plus.py (floor at 0, averaging weights, alternation), rerun convergence script, confirm speedup number matches csv; mark Phase 3 DONE in PROGRESS.md | done when: checks pass and PROGRESS.md says Phase 3 DONE

## Phase 4: Leduc + MCCFR
- [ ] P4.1 | sonnet | games/leduc.py: 6 cards (2 suits x J,Q,K), ante 1, raise 2 in round 1 and 4 in round 2, max 2 raises per round, public card after round 1, pair beats high card; tests for deal count, sample terminal payoffs, fold payoffs, infoset keys hide opponent card | done when: `pytest -q` passes
- [ ] P4.2 | sonnet | Make CFR, CFR+, best response, exploitability run on Leduc (generic over Game); tests with small iteration counts that exploitability decreases | done when: `pytest -q` passes in < 10 s
- [ ] P4.3 | sonnet | solvers/mccfr.py: external-sampling MCCFR with seeded RNG | done when: tests pass: Kuhn value within 0.02 of -1/18 after 20k iters, exploitability decreases on Leduc
- [ ] P4.4 | sonnet | scripts/leduc_benchmark.py: run vanilla CFR, CFR+, MCCFR on Leduc for a fixed wall-clock budget each (total < 8 min), log exploitability in mbb/hand vs seconds to analysis/leduc_benchmark.csv, one summary line per solver | done when: csv has all 3 solvers
- [ ] P4.5 | haiku | analysis/plot_leduc.py: exploitability (mbb/hand) vs time, log scale, all solvers, saved to analysis/leduc_benchmark.png; results.md entry with command | done when: png exists, results.md updated
- [ ] P4.6 | sonnet | Docs: LEARNING.md Phase 4 entry (Leduc rules, MCCFR external sampling, unbiased estimator math in LaTeX, 3 Q&As); README Leduc + MCCFR rows and chart | done when: files updated, `pytest -q` passes
- [ ] P4.7 | opus | VERIFY Phase 4: review leduc.py rules and payoffs, mccfr.py sampling weights; compare Leduc game value from CFR+ to the published value (about -0.0856 for P1, confirm from a source); sanity-check mbb/hand units; mark Phase 4 DONE in PROGRESS.md | done when: checks pass and PROGRESS.md says Phase 4 DONE

## Phase 5: Bots + best response vs bots
- [ ] P5.1 | sonnet | agents/base.py Agent interface (act(game, state, infoset) -> action, reset); agents/equilibrium.py samples from a saved average strategy; scripts/save_strategies.py writes analysis/strategies/{kuhn,leduc}.json | done when: tests pass: equilibrium agent only plays legal actions with stored probabilities
- [ ] P5.2 | sonnet | agents/bots.py: always-call, always-raise, tight (raises/calls only strong hands), random | done when: tests pass: each bot only plays legal actions and matches its rule
- [ ] P5.3 | sonnet | eval/match.py: play N mirrored hand pairs (same deal, seats swapped), seeded; return mean chips/hand, mbb/hand, and 95% CI | done when: tests pass: agent vs itself CI contains 0; always-raise vs always-call is deterministic per deal
- [ ] P5.4 | sonnet | agents/exploiter.py: plays the exact best response to a known fixed bot strategy (uses eval/best_response.py) | done when: test passes: exploiter's exact EV vs each bot >= equilibrium agent's exact EV vs that bot
- [ ] P5.5 | sonnet | scripts/bot_matches.py: equilibrium and exploiter vs each bot on Leduc, enough hands for tight CIs (run time < 8 min), write analysis/bot_matches.csv, results.md entry with command | done when: csv has all pairings with CIs
- [ ] P5.6 | sonnet | Docs: LEARNING.md Phase 5 entry (mirrored hands, variance reduction, CI formula in LaTeX, 3 Q&As); README results rows | done when: files updated, `pytest -q` passes
- [ ] P5.7 | opus | VERIFY Phase 5: check simulated exploiter win rates fall within CI of the exact BR values, check CI math and mirroring, confirm no hand-typed numbers; mark Phase 5 DONE in PROGRESS.md | done when: checks pass and PROGRESS.md says Phase 5 DONE

## Phase 6: Adaptive agent
- [ ] P6.1 | sonnet | agents/adaptive.py: online opponent model (Dirichlet counts per opponent infoset-visible situation, prior centered on equilibrium), best response to the model mixed with equilibrium by a confidence weight that grows with observations | done when: tests pass: with no observations it plays equilibrium; after many always-call hands its strategy moves toward the exploiter's
- [ ] P6.2 | sonnet | Safety: cap exploitation weight so loss vs an equilibrium opponent stays small; test adaptive vs equilibrium agent over mirrored hands | done when: test passes: adaptive vs equilibrium CI lower bound > -50 mbb/hand (Leduc)
- [ ] P6.3 | sonnet | scripts/adaptive_matches.py: adaptive vs each bot and vs equilibrium, write analysis/adaptive_matches.csv with CIs and compare to exploiter + equilibrium rows; results.md entry with command | done when: csv complete
- [ ] P6.4 | sonnet | Docs: LEARNING.md Phase 6 entry (opponent modeling, safe exploitation trade-off, LaTeX, 3 Q&As); README adaptive row | done when: files updated, `pytest -q` passes
- [ ] P6.5 | opus | VERIFY Phase 6: review adaptive.py for leakage (model must use only what the agent observes), check win rates beat equilibrium vs weak bots and stay safe vs equilibrium; mark Phase 6 DONE in PROGRESS.md | done when: checks pass and PROGRESS.md says Phase 6 DONE

## Phase 7: Terminal play
- [ ] P7.1 | sonnet | play/cli.py: `python -m play.cli --game kuhn|leduc --seed N`, human vs equilibrium bot, shows bot's action probabilities at its infoset after each move, running chip total; input/output injectable | done when: `python -m play.cli --help` works
- [ ] P7.2 | haiku | tests/test_cli.py: scripted inputs play full Kuhn and Leduc hands, invalid input reprompts | done when: `pytest -q` passes
- [ ] P7.3 | sonnet | Docs: README play section; LEARNING.md Phase 7 short entry with 3 Q&As | done when: files updated
- [ ] P7.4 | opus | VERIFY Phase 7: play one scripted hand per game, confirm shown probabilities match stored strategy and chips are correct; mark Phase 7 DONE in PROGRESS.md | done when: checks pass and PROGRESS.md says Phase 7 DONE

## Phase 8: README + writeup
- [ ] P8.1 | sonnet | scripts/make_results_table.py: builds README results table from analysis/*.csv (every row includes its reproduce command) and inserts it between markers in README.md | done when: script runs, README table filled from csvs
- [ ] P8.2 | haiku | README polish: real quickstart commands, embed both charts, link LEARNING.md and analysis/results.md | done when: every command in README runs
- [ ] P8.3 | sonnet | analysis/writeup.md: 1-2 page writeup (method, results table, limits; no "solved poker" claims) plus a short summary using only numbers from csvs | done when: file exists, every number traceable to a csv
- [ ] P8.4 | opus | VERIFY Phase 8: rerun fast commands from analysis/results.md, confirm numbers match README/writeup, grep for overclaims; mark Phase 8 DONE in PROGRESS.md | done when: checks pass and PROGRESS.md says Phase 8 DONE
