# Thesis Skeleton — chapter map with numbers wired to sources
**Working title:** Uncertainty-Aware Surrogate Optimization of Decentralized Mixed-Plastic Pyrolysis Networks for EPR-Compliant Liquid-Fuel Recovery in the Philippines
**Rule:** every number cites the script that regenerates it. Nothing enters a chapter that `/src` cannot reproduce.

## Ch.1 Introduction (≈10 pp)
1.1 The sachet economy and RA 11898 (World Bank 2021 [V]: 2.7 Mt/yr; DAO 2023-02 [V]: 20→80% footprint obligation, ₱5–20M fines) · 1.2 Problem: no PH-specific design answers scale/config under real composition uncertainty · 1.3 The three reframed gaps (verbatim from `gap_reframe.md`; Wang & Maravelias 2024 and Crîstiu 2024 cited by name up front) · 1.4 Contribution = the coupling: UQ-carrying surrogate inside a recovery-constrained stochastic superstructure · 1.5 **Closing paragraph = the motivating number:** P(recovery ≥ 80%) = 24% for realistic PH streams (`flowsheet_shortcut.py`).

## Ch.2 Literature Review (≈15 pp)
Five threads from `annotated_bibliography.md` (28 refs, 27 [V]). Gap matrix table (`gap_matrix.md`): no prior row scores ●●●. Positioning paragraph verbatim from gap_reframe (Wang deterministic-first-mover → this work adds uncertainty + constraint + surrogate).

## Ch.3 Methods I — Process Model (≈15 pp)
3.1 Yield-shift architecture; Gibbs rejection documented · 3.2 Genuino superposition + Westerhout kinetics (`lumped_kinetics.py`; V3: 4.6 pp ≤ 5) · 3.3 DWSIM flowsheet v3 (PR; stabilizer; vacuum SCOL-2; balance 0.0014%; `flowsheet_spec.md` §6.1 actuals) · 3.4 Flowsheet-shortcut oracle + **6-point DWSIM validation: prediction falsified, mechanism found (SCOL-2 HK leak + stale loss calibration), 2-param recal, 24/24 ≤ 2%** (`verify_vs_dwsim.py`, `p5_dwsim_validation.md`) · 3.5 Cut split as declared uncertainty (option 3; `cut_split_uncertainty.py`: separation proof, var = 0).

## Ch.4 Methods II — Uncertainty & Optimization (≈15 pp)
4.1 Composition uncertainty set: constructed, not measured (WACS gap is the premise); Dirichlet c=25 + robust box (`feedstock_doe.py`) · 4.2 GP surrogate: beats LightGBM all targets, 95%-CI coverage 0.99–1.00; exact linear embedding via scenario coefficients (`surrogate_train.py`) · 4.3 Two-stage SP + four levers + statute-faithful penalty (`superstructure_p4b.py`) · 4.4 Chance-constrained formulation — the correct lens (F2 argument) · 4.5 A1–A4 assumptions stated.

## Ch.5 Results (≈20 pp)
5.1 Compliance is chemistry-bound: 30%, gas module → 80% (F1) · 5.2 VSS ≈ 0 robustly + why (fines ≪ profit; `p4_findings.md` F2) · 5.3 **Cost-of-assurance curve** (SAA R=10×S=100): ₱18.3±9.9M mild vs median ₱413M strong; mechanism switch; structural-vs-noise table (`p5_validation.md` R1–R2) · 5.4 Deterministic over-promise 25–30 pp (R3) · 5.5 Vacuous-compliance artifact + min-service refinement (R4) · 5.6 Hybrid config F4.

## Ch.6 TEA + LCA (≈12 pp)
Headline-as-upper-bound discipline (T1/T2 headroom form: absorbs ₱26–30k/t unmodeled cost); Sobol: composition = 62% of NPV variance (T3); LCA both signs reported (T4); verified diesel parity ₱51–55/L (`tea_uq.py`, `p6_tea.md`).

## Ch.7 Conclusions & Policy (≈6 pp)
(1) 80% liquid-only infeasible for realistic streams → accounting question is decisive · (2) gas-recovery credit = single highest-leverage design/policy item · (3) commission resin-resolved WACS — two independent cases (compliance F3 + economics T3) · (4) methodological: chance constraints, not VSS, for profit-dominant compliance networks.

## Appendices
A: verification actuals · B: DOE tables · C: solver logs · D: DWSIM build guide + validation protocol · E: reproducibility (repo, tags, Zenodo DOI at P9).
