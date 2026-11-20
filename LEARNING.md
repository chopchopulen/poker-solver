# What I learned

## Phase 1: Kuhn poker + vanilla CFR

**What it does.** Kuhn poker: 3 cards (J<Q<K), each player antes 1, one bet of 1 allowed. CFR plays the game against itself many times. At every information set (what the player can see: own card + action history) it tracks how much it *regrets* not having played each action, and shifts toward actions with high regret. The *average* strategy over all iterations converges to a Nash equilibrium. Player 1's value at equilibrium is $-1/18$.

**Regret matching.** Let $v^\sigma(I,a)$ be the counterfactual value of taking $a$ at infoset $I$, and $v^\sigma(I)=\sum_a \sigma(I,a)\,v^\sigma(I,a)$. Counterfactual reach $\pi_{-i}^\sigma(I)$ is the product of the opponent's and chance's probabilities of reaching $I$. Instantaneous and cumulative regret:
$$r^t(I,a)=\pi_{-i}^{\sigma^t}(I)\,\big(v^{\sigma^t}(I,a)-v^{\sigma^t}(I)\big),\qquad R^T(I,a)=\sum_{t=1}^T r^t(I,a).$$
Next strategy (uniform if the denominator is 0, with $R^+=\max(R,0)$):
$$\sigma^{T+1}(I,a)=\frac{R^{T,+}(I,a)}{\sum_{b}R^{T,+}(I,b)}.$$

**Average strategy.** The current strategy $\sigma^t$ does not converge; the reach-weighted average does. Within one iteration $\sigma^t$ is frozen: an infoset reached under several deals uses the same $\sigma^t$ each time, and new regrets only affect $\sigma^{t+1}$.
$$\bar\sigma^T(I,a)=\frac{\sum_{t=1}^T \pi_i^{\sigma^t}(I)\,\sigma^t(I,a)}{\sum_{t=1}^T \pi_i^{\sigma^t}(I)}.$$
Average regret $R^T/T=O(1/\sqrt T)$, and in a two-player zero-sum game, if each player's average regret is $\le\varepsilon$ then $\bar\sigma$ is a $2\varepsilon$-Nash equilibrium.

**Kuhn equilibrium family.** P1 bets J with prob $\alpha\in[0,1/3]$, bets K with $3\alpha$, calls Q (after check-bet) with $\alpha+1/3$. P2 always bets/calls with K, bluffs J with 1/3 after a check, calls Q with 1/3. Game value is $-1/18$ for every $\alpha$. Our run: $\alpha\approx0.21$, value $-0.055555$ (`python scripts/run_kuhn_cfr.py`).

**Q&A**
1. *Why use the average strategy, not the current one?* Regret matching's current strategy can cycle around equilibrium and need not converge. The no-regret guarantee applies to the time-averaged strategy, which does converge in two-player zero-sum games.
2. *Why weight regret by opponent reach and chance, not own reach?* Counterfactual value asks "if I tried to reach this infoset, how good is action $a$?", so my own reach probability is set to 1. Only opponent and chance probabilities determine how often the infoset is really reached. The average strategy is instead weighted by my own reach, so rarely-reached infosets count less.
3. *Why does Kuhn have many equilibria, and how do you know the value is right?* P1 has a free parameter $\alpha$ (how often to bluff with J) that P2's best response cannot exploit, giving a one-parameter family. All members give value $-1/18$ because the minimax value of a zero-sum game is unique. We compute the value of the average strategy and compare to $-1/18$ (error $\sim10^{-6}$).

## Phase 2: Best response and exploitability

**What it does.** A best response (BR) to a fixed strategy $\sigma_{-i}$ is the strategy for player $i$ that maximizes its expected payoff against $\sigma_{-i}$. Exploitability measures how much a strategy profile loses to a perfect opponent; it is 0 exactly at a Nash equilibrium. It is the honest score for a solver: game value alone can look right for a bad strategy.

**Computing BR exactly.** Player $i$ may only condition on its own information set $I$. For each $I$, sum over all histories $h \in I$ the opponent-and-chance reach $\pi_{-i}^\sigma(h)$ times the value of each action, then pick the best action. Never use the opponent's hidden card to choose an action (that would be peeking and overstate BR). Bottom-up:
$$v_i^{BR}(I)=\max_{a}\sum_{h\in I}\pi_{-i}^{\sigma}(h)\,u_i(h,a),$$
where $u_i(h,a)$ is the continuation value after $a$ with $i$ playing BR below.

**Exploitability.** In a zero-sum game,
$$\mathrm{expl}(\sigma)=\tfrac12\Big(\max_{\sigma_1'}u_1(\sigma_1',\sigma_2)+\max_{\sigma_2'}u_2(\sigma_1,\sigma_2')\Big) \ge 0 .$$
Units: mbb/hand $=1000\cdot\mathrm{expl}/\text{big blind}$.

**Convergence bound.** Average regret $R^T_i/T \le \Delta\sqrt{|A|}/\sqrt{T}$ ($\Delta$ = payoff range), and the average profile is an $\varepsilon$-Nash with $\varepsilon \le (R_1^T+R_2^T)/T$, so
$$\mathrm{expl}(\bar\sigma^T)=O\big(1/\sqrt{T}\big),$$
a slope of $-1/2$ on a log-log plot. Measured on Kuhn: slope $-0.544$ for $T\ge 10^4$ (`analysis/results.md`).

**Q&A**
1. *Why is exploitability better than checking game value?* Game value only checks the profile's payoff against itself. A non-equilibrium profile can have the right value yet be badly beatable. Exploitability is the gain of a best-responding opponent, so it is 0 iff Nash.
2. *Why must best response aggregate over histories in an infoset?* The player cannot distinguish histories in the same infoset, so one action must serve all of them. Weight each history by opponent and chance reach, then maximize. Choosing per history would leak hidden information and overstate BR value.
3. *Why a slope near -1/2 on the log-log plot?* Regret matching gives $O(\sqrt{T})$ cumulative regret, so average regret and hence exploitability decay like $T^{-1/2}$. Observed rates can be slightly better; CFR+ is often faster still.

## Phase 3: CFR+

**What it does.** CFR+ is vanilla CFR with three changes: (1) regret matching+ floors cumulative regret at zero, (2) players are updated alternately, (3) the average strategy is weighted linearly in the iteration. Same tree walk, same per-iteration cost, far fewer iterations needed.

**The changes.**
$$R^{T,+}(I,a)=\max\big(R^{T-1,+}(I,a)+r^T(I,a),\,0\big),\qquad \sigma^{T+1}(I,a)=\frac{R^{T,+}(I,a)}{\sum_{a'}R^{T,+}(I,a')}$$
$$\bar\sigma^T(I,a)=\frac{\sum_{t=1}^T t\,\pi_i^{\sigma^t}(I)\,\sigma^t(I,a)}{\sum_{t=1}^T t\,\pi_i^{\sigma^t}(I)}$$

**Why faster.** Vanilla CFR lets an action with large negative regret stay buried: it needs many iterations of positive regret just to climb back to zero. Flooring at 0 lets an action recover as soon as it becomes good. Linear weights discount the early, bad iterates (weight $t$ vs $1$), so the average tracks recent, near-equilibrium strategies. Alternating updates make each player respond to the other's freshly updated strategy. The proven worst-case bound is still $O(1/\sqrt T)$; the speedup is empirical.

**Measured (Kuhn).** Iterations to exploitability $<10^{-3}$: vanilla 43080, CFR+ 130, speedup 331x (`analysis/results.md`, `analysis/kuhn_speedup.csv`). At 100k iters CFR+ exploitability is 2.14e-6 vs 6.76e-4 vanilla.

**Q&A**
1. *Why floor regrets at zero?* Negative regret only says an action was bad in the past. Keeping it delays that action's return when the opponent's strategy changes. Flooring discards stale history so play adapts fast.
2. *Why average with weight $t$?* Early iterates are far from equilibrium. Linear weighting shrinks their influence, so the average converges faster. We still evaluate the average, not the current strategy.
3. *Does CFR+ beat $O(1/\sqrt T)$ in theory?* No, the proven bound is the same. The gain is empirical (hundreds of times fewer iterations here), observed not guaranteed.

## Phase 4: Leduc poker + external-sampling MCCFR

**Leduc rules.** 6 cards (J, Q, K in 2 suits). Each player antes 1 and gets one private card. Round 1: bets/raises of 2, max 2 raises. Then one public card is dealt. Round 2: bets/raises of 4, max 2 raises. At showdown a pair (private rank = public rank) beats high card, otherwise higher rank wins; equal ranks split. 30 private deals, 4 board outcomes. Infoset key = own card rank + public card (if dealt) + betting history, so the opponent's card is never visible.

**Why MCCFR.** Vanilla CFR walks the whole tree every iteration. External sampling traverses all actions of the updating player $i$ but samples one action at each chance node and each opponent node from $\sigma_{-i}$. Iterations are far cheaper but noisier.

**Unbiased estimator.** Sampled terminal $z$ has probability $q(z)=\pi_{-i}^{\sigma}(z)\,\pi_c(z)$ (opponent and chance reach; player $i$'s own actions are not sampled). The sampled counterfactual value
$$\tilde v_i(I,a)=\sum_{z\in Q\cap Z_I}\frac{u_i(z)\,\pi_i^{\sigma}(z[I]\to z)}{q(z)},\qquad \mathbb{E}_Q[\tilde v_i(I,a)]=v_i^{\sigma}(I,a)$$
is unbiased because $q(z)$ cancels the $\pi_{-i}\pi_c$ factor in the true counterfactual value. Hence $\tilde r(I,a)=\tilde v_i(I,a)-\sum_{a'}\sigma(I,a')\tilde v_i(I,a')$ is an unbiased regret estimate, and the average strategy converges to Nash with expected exploitability $O(1/\sqrt T)$. The average strategy is accumulated at the opponent's nodes (where actions are sampled from $\sigma$), so no extra reach weighting is needed.

**Measured (Leduc, 140 s per solver).** CFR 12.2, CFR+ 0.015, MCCFR 10.5 mbb/hand (`analysis/results.md`). CFR+ wins on this small game; MCCFR runs 1.17M iterations vs 8k for CFR but they are noisy. MCCFR pays off when the tree is too big to traverse.

**Q&A**
1. *Why is the external-sampling estimate unbiased?* Each sampled terminal is divided by its sampling probability $\pi_{-i}\pi_c$, cancelling the opponent/chance reach in the counterfactual value, so the expectation equals the full-tree value.
2. *Why does CFR+ beat MCCFR on Leduc?* Leduc is small enough to traverse fully, so CFR+ iterations carry no sampling variance and the regret floor speeds convergence. MCCFR's edge is cost per iteration, which matters only for huge trees.
3. *Why must infoset keys hide the opponent card?* Keys must contain only what the player sees. Including the opponent card lets the solver peek, giving an invalid strategy whose exploitability looks artificially low.
