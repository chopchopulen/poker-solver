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
