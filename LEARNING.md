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
