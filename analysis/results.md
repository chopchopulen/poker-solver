# Results

## Kuhn poker: vanilla CFR convergence (P2.4)

Plot: `analysis/kuhn_convergence.png` (log-log, exploitability vs iterations, with T^-1/2 reference).

- Data: `analysis/kuhn_convergence.csv` (38 log-spaced points, T = 1 to 100,000).
- Exploitability at T=1: 0.4583; at T=100,000: 6.76e-4.
- Log-log slope fit over T >= 10,000: -0.544 (about -1/2, as the O(1/sqrt(T)) bound predicts).

Reproduce:

```
python scripts/kuhn_convergence.py
python analysis/plot_convergence.py
```

Expected summary line from the second command: `plot_convergence: 38 pts, slope(T>=10000)=-0.544, wrote analysis/kuhn_convergence.png`

## Kuhn: CFR+ vs vanilla CFR speedup

Target: exploitability < 1e-3. First iteration reaching it, from `analysis/kuhn_speedup.csv`:

| solver | iters to expl < 1e-3 |
|---|---|
| vanilla CFR | 43,080 |
| CFR+ | 130 |

Speedup: 331x (43080 / 130 = 331.38).

Plot with both solvers: `analysis/kuhn_convergence.png` (log-log, exploitability vs iterations, T^-1/2 reference).

Reproduce:

```
python scripts/kuhn_convergence.py --solver cfr
python scripts/kuhn_convergence.py --solver cfr_plus
python analysis/plot_convergence.py
```

Expected summary line from the last command: `plot_convergence: 76 pts, cfr slope=-0.544, cfr_plus slope=-0.849, wrote analysis/kuhn_convergence.png`

## Leduc: exploitability vs time, all solvers

Source: `analysis/leduc_benchmark.csv` (140 s training budget per solver, last logged point):

| solver | final exploitability (mbb/hand) | iterations |
|---|---|---|
| vanilla CFR | 12.25 | 7,999 |
| CFR+ | 0.0154 | 4,740 |
| MCCFR (external sampling) | 10.51 | 1.17M |

Plot: `analysis/leduc_benchmark.png` (log-scale y, exploitability in mbb/hand vs training seconds).

Reproduce:

```
python scripts/leduc_benchmark.py
python analysis/plot_leduc.py
```

Expected summary line from the last command: `plot_leduc: 73 pts, cfr final=12.25, cfr_plus final=0.01541, mccfr final=10.51, wrote analysis/leduc_benchmark.png`

## Leduc game value (P4.7 verification)

CFR+ 3000 iterations: P1 value of average strategy = -0.085605 chips/hand. Certified bounds on the true game value from exact best responses, $-BR_1(\sigma_0) \le v^* \le BR_0(\sigma_1)$: v* in [-0.085655, -0.085586] (exploitability 3.45e-05 chips/hand). The interval contains the commonly cited Leduc value of about -0.0856 for P1. That citation was not checked against a source in this run because web access was denied.

Units: Leduc has no blinds, so 1 big blind = 1 chip = the ante, and mbb/hand = 1000 * chips/hand.

```
python scripts/leduc_value.py --iters 3000
```

Expected: `leduc cfr_plus iters=3000 value_p1=-0.085605 bounds=[-0.085655,-0.085586] expl=3.45e-05 chips/hand`

## Leduc: equilibrium and exploiter vs fixed bots (P5.5)

Data: `analysis/bot_matches.csv`. 150,000 mirrored pairs (300,000 hands) per pairing, seed 0; mbb/hand for the agent (1 chip = 1 bb), 95% CI over pair means; `exact_mbb` = exact EV from the game tree for comparison. Equilibrium = CFR+ 2000-iter average strategy.

Reproduce: `python scripts/bot_matches.py --pairs 150000 --seed 0` (about 60 s)

Per-pairing mbb/hand and CI are in the csv (all 8 pairings: 2 agents x 4 bots).
