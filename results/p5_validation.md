# P5 Validation Results — SAA Stability + Deterministic Benchmark
**Repo:** `ipis-thesis-pyrolysis-epr` · R=10 replications × S=100 scenarios per regime, MIP gap 1e-3, HiGHS. Reproduce: `python src/saa_stability.py batch|aggregate|benchmark`.

## R1 — SAA-disciplined cost of 90% assurance (revises P4b single-sample values)
| Regime | Mean ± 95% CI | Range | Median | P4b single-sample |
|---|---|---|---|---|
| Mild (c_lgu=60) | **₱18.3 ± 9.9 M/yr** | 3.6–41.5 | ~10 | 39.6 (high tail) |
| Strong (c_lgu=15) | ₱849 ± 635 M/yr | 6.5–2,662 | **~₱413 M/yr** | 644 |
Strong regime is **bimodal**: hardware-only solutions (₱6–23M), selective-contracting (₱209–1,414M), and 2/10 **exit solutions** (drop all LGUs, ₱2.5–2.7B = foregone business). Median is the honest summary; the CI is wide because the *mechanism* switches, not because the model is noisy.

## R2 — Structural vs sampling-noise design features (the point of SAA)
| Feature | Frequency | Verdict |
|---|---|---|
| Gas module @ Carmona | 10/10 mild, 8/10 strong | **STRUCTURAL** — the robust design element |
| Hybrid config (satellite + XL central) | every replication | **STRUCTURAL** |
| Selective contracting activates (strong) | 6/10 reps | **STRUCTURAL** (that it happens) |
| *Which* LGU is dropped | QC 4, Caloocan 3, Manila 3, Parañaque 3, others 2 | **SAMPLING NOISE** — P4b's "Caloocan" was sample-specific, as flagged |

## R3 — Deterministic over-promise (the benchmark table vs Santibañez-class models)
| Regime | Deterministic promise | Realized under uncertainty | Over-promise |
|---|---|---|---|
| Mild | 100% compliance | 75% | **25 pp** |
| Strong | 100% compliance | 70% | **30 pp** |
A mean-composition design *believes* it is fully compliant; it fails the obligation 1 in 4 years (mild) to nearly 1 in 3 (strong). This is the quantified case against the deterministic literature baseline.

## R4 — Model artifact found and logged: vacuous compliance by exit
2/10 strong replications satisfy the chance constraint by contracting **zero** footprint (0 ≥ 0.8×0). Statute-faithful in letter, absurd in spirit. Formulation refinement for the thesis model: minimum-service constraint or treat no-build as a separate branch. Found by SAA replication — exactly what validation is for.

## Remaining to close P5
DWSIM 6-point validation (`models/dwsim_validation_protocol.md`, user-side, ±5% acceptance).
