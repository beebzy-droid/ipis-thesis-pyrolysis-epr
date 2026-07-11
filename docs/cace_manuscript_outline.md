# CACE Manuscript Architecture
**Target:** *Computers & Chemical Engineering* (venue publishes this problem class: Crîstiu et al. 2024, CACE 180:108503). Length target ≈ 8,000 words + 6 figures + 4 tables.

## Title candidates
1. "Chance-constrained design of decentralized plastic-pyrolysis networks under feedstock-composition uncertainty: an EPR-compliance study for the Philippines"
2. "When the value of the stochastic solution is zero: compliance-risk design of recovery-constrained plastic valorization networks"
3. (conservative) "Uncertainty-aware surrogate optimization of mixed-plastic pyrolysis networks under Extended Producer Responsibility constraints"
**PM pick: #1** — names the method, the object, and the constraint; #2 is the punchy backup if reviewers like the VSS finding.

## Abstract skeleton (150–200 w)
Context (RA 11898 + no PH design) → method (validated superposition flowsheet → GP surrogate → two-stage SP → chance-constrained) → 4 numbers: P(compliance)=24–30% baseline; gas module →80%; over-promise 25–30 pp; assurance cost ₱18M vs ₱413M median by heterogeneity → conclusion (accounting + WACS data, chance constraints over VSS).

## Figures (each regenerable from /src)
| # | Figure | Source |
|---|---|---|
| F1 | Superstructure schematic + flowsheet inset | draw (models/) |
| F2 | Recovery distribution vs 80% target, 3 fidelity layers (38→22/24%) | feedstock_doe + flowsheet_shortcut |
| F3 | DWSIM 6-point parity plot, pre/post recal | verify_vs_dwsim |
| F4 | GP parity + CI-coverage panel | surrogate_train |
| F5 | **Cost-of-assurance: box plots by heterogeneity, mechanism-annotated** (the money figure) | saa_stability |
| F6 | Sobol tornado (NPV) | tea_uq |

## Tables
T1 gap matrix (condensed) · T2 verification actuals (V1–V6) · T3 SAA structural-vs-noise · T4 TEA with headroom framing.

## Claims-to-evidence map (defense-grade; keep updated)
| Claim | Number | Script | Status |
|---|---|---|---|
| Yield model verified | 4.6 pp ≤ 5 | verify_vs_genuino.py | [V] |
| Flowsheet verified | balance 0.0014%, 24/24 ≤2% | flowsheet_spec §6.1, verify_vs_dwsim.py | [V] |
| GP UQ calibrated | coverage 0.99–1.00 | surrogate_train.py | [V] |
| Compliance chemistry-bound | 30%→80% w/ gas module | superstructure_p4b.py | [V-model] |
| VSS ≈ 0 robust | \|VSS\|<0.012% @gap 1e-4 | saa_stability.py | [V-model] |
| Over-promise | 25–30 pp | saa_stability.py benchmark | [V-model] |
| Assurance cost | 18.3±9.9 / median 413 MPHP | saa_stability.py | [V-model] |
| Composition drives NPV | Sobol ST=0.62 | tea_uq.py | [V-model] |
| Diesel parity | ₱51–55/L ex-plant | DOE Jul-2026 | [V] |
| Economics upper bound | headroom ₱26–30k/t | tea_uq.py | [GK-flagged] |

## Pre-empted reviewer objections (write these INTO the paper)
1. "Surrogate of a linear model is trivial" → §Methods: linearity makes the embedding *exact*; GP's role = UQ carrier + architecture for higher-fidelity oracles; nonlinearities N1–N4 carried and validated.
2. "VSS=0 means stochastic adds nothing" → the F2 argument is the paper's methodological point (title #2 exists for a reason).
3. "Composition set is constructed, not measured" → stated as the premise; robust fallback pre-registered; heterogeneity sensitivity IS the result.
4. "Economics too optimistic" → upper-bound + headroom framing, in the abstract's own words.
5. "Vacuous compliance" → found by our own SAA, refinement stated (min-service).
6. "Single-point oracle calibration" → falsified-prediction→recalibration→24/24 narrative in §3.4.

## Writing order (P7 execution)
Methods (exists in repo docs) → Results (exists in results/) → Intro (gap_reframe verbatim core) → Discussion → Abstract last. Thesis chapters and paper share sources; paper is the 8k-word cut.
