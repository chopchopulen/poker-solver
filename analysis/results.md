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
