# SESSION BRIEF — pin this in the dedicated Claude session

**Repo:** `ipis-thesis-pyrolysis-epr` · **Idea:** W1 / A (primary thesis) · **Program:** IPIS
**Session rule:** This chat works ONLY on W1/A. Keep other theses out of context.

---

## Standing instructions (PM mode)
Numbers-first. Lead with the answer, then reasoning. No filler, no sycophancy. Critique honestly; flag limitations and better alternatives. Flag general-knowledge vs. verified. SI units. Tables for comparisons. Every recommendation ties to a measurable outcome. Do not fabricate citations — pull exact, verifiable references and flag anything unverified.

## Thesis in one line
Bayesian/GP surrogate of a rigorous pyrolysis+separation flowsheet, embedded in a spatial superstructure optimization solved as a stochastic/robust program over empirically-characterized PH feedstock composition uncertainty, subject to the RA 11898 recovery-rate constraint. Target: Computers & Chemical Engineering.

## Grounded anchors (verify in P1)
- RA 11898 recovery: 60% (2026) → 70% (2027) → 80% (2028); fines PHP 5–20M.
- ~2.7 Mt/yr plastic generated; near-zero domestic chemical-recycling capacity for multilayer/film.
- Novelty lever: uncertainty-aware surrogate + spatial superstructure under data scarcity.

## Phase plan (status)
- [x] **P0** Repo + env + this brief. **DONE.**
- [ ] **P1** Literature review + gap matrix.  ← **START HERE**
- [ ] P2 Base pyrolysis+distillation flowsheet (DWSIM), verified.
- [ ] P3 Feedstock characterization + Latin-hypercube DOE.
- [ ] P4 GP/LightGBM surrogate + Pyomo stochastic superstructure.
- [ ] P5 Validation & benchmarking vs. deterministic baseline.
- [ ] P6 Sensitivity/UQ (SALib) + TEA (NPV/IRR, break-even PHP/L) + streamlined LCA.
- [ ] P7 Thesis chapters + CACE manuscript in parallel.
- [ ] P8 Defense prep (reviewer-style critique pass) + submission.
- [ ] P9 Zenodo DOI on pre-submission release.

## Immediate task — P1 (do this first in the new session)
Deliverables: `literature/references.bib`, `literature/annotated_bibliography.md`, `literature/gap_matrix.md` (each cited work × which of the 3 gaps it does/does not close).

Search strategy (run these threads, verify every claim):
1. Mixed-plastic pyrolysis lumped kinetics & product yields (reviews + primary kinetic schemes).
2. Surrogate-assisted optimization in PSE (GP / gradient-boosting; when surrogates beat rigorous sim).
3. Superstructure / process-network synthesis (facility siting; decentralized vs. centralized).
4. Optimization under uncertainty (stochastic programming, robust optimization, chance constraints).
5. PH waste characterization (NSWMC / World Bank / LGU) + RA 11898 implementing rules (DAO 2023-02, 2024-04).

Gap to defend (the 3 the thesis closes jointly):
(1) feedstock treated as fixed → ignores PH MSW composition variance;
(2) single-plant optimization → no decentralized-vs-centralized siting under a recovery constraint;
(3) rigorous sim only → no surrogate acceleration for network-scale optimization.

## Guardrails
- No proprietary plant data in the repo (see `data/README.md`).
- Commit early/often; one branch per phase; tag releases at milestones.
- Reproducibility: `/src` must regenerate every figure from raw inputs.
