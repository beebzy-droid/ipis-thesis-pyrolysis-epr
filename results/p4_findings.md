# P4 Findings — Stochastic Superstructure Results (prototype instance)
**Repo:** `ipis-thesis-pyrolysis-epr` · Metro Manila instance: 8 LGUs (130 kt/yr), 4 candidate sites, S=50 scenarios, MIP gap 1e-4, HiGHS. Economics [GK], P6 verifies. Reproduce: `python src/superstructure_p4b.py`.

## F1 — Compliance is chemistry-bound; the gas-recovery module is the single highest-leverage decision
Liquid-only accounting: P(recovery ≥ 80%) = **30%** for ANY all-processing design (P4a). One gas-energy-recovery module at the central site (₱15M/yr [GK], gas credited at η=0.9): **P(compliance) → 80%**. No siting rearrangement achieves any of this.

## F2 — VSS ≈ 0 robustly, even with four recourse levers. This is a methodological finding, not a failure.
| Case | VSS | Why |
|---|---|---|
| P4a (base) | 0 (exact) | identical configs; composition risk irreducible under serve-all |
| P4b mild heterogeneity | −0.1 MPHP (≈0, tol) | best hedge (gas module) visible at the mean too |
| P4b strong heterogeneity | −0.3 MPHP (≈0, tol) | same |

Mechanism: statutory fines (₱20M lump; 2× recovery cost) are **two orders of magnitude below network profit** (~₱2.75B/yr), so the risk-neutral expectation barely feels non-compliance; and the dominant hedge is already optimal at the mean composition. **For profit-dominant waste-valorization networks under compliance obligations, VSS understates the value of stochastic design — the value lives in the risk constraint, not the expected cost.** Hence the chance-constrained formulation is the correct lens (F3). This is a claimable methodological contribution.

## F3 — The cost-of-assurance result (the thesis's headline design table)
Chance-constrained: min cost s.t. P(recovery ≥ 80%) ≥ 90%.

| LGU heterogeneity | Cost of 90% assurance | Mechanism |
|---|---|---|
| Mild (c_lgu=60) | **₱39.6 M/yr** (1.4% of profit) | hardware: 2nd gas module + upsize Valenzuela S→M |
| Strong (c_lgu=15) | **₱644.4 M/yr** (25% of profit) | structural: **drops Caloocan** (7/8 contracted) — selective contracting |

17× cost ratio; the *mechanism of assurance changes* from hardware hedging to network reshaping as spatial heterogeneity grows. Since no PH data constrains within-metro heterogeneity (P3 finding), this sensitivity IS the honest result — and the strongest argument for commissioning resin-resolved WACS.

## F4 — Decentralization answer (this instance): hybrid, never pure
Every solve selects **1 small north satellite (15–30 kt) + 1 XL central (120 kt, Carmona)**. Neither full centralization nor full decentralization is ever optimal at [GK] economics. Transport is cheap (₱240/t typical) relative to scale economies (exponent 0.65), but the satellite persists for northern-catchment transport savings.

## Caveats / P5 backlog
1. SAA stability: S=50, single sample path; resample (N≥10 replications, S=100) for CI on the assurance costs; Caloocan-drop may be sample-specific.
2. Economics [GK] throughout — P6 TEA disciplines prices/CAPEX; profit dominance could soften at low fuel prices, which would revive VSS.
3. Single-point DWSIM calibration of the oracle (P4 backlog: 5–10 DWSIM validation points).
4. Prototype spatial instance; LGU populations [GK, PSA 2020 — verify].
