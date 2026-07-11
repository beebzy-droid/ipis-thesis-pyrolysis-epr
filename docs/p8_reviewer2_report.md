# P8 — Adversarial Review: CACE Reviewer 2 Pass on Draft 2
**Stance:** hostile-but-fair PSE reviewer, full access to the claims-to-evidence map. Verdict first, then majors, minors, and disposition.

## Verdict
**Draft 3 status: all seven majors and all minors resolved or rebutted with computation. Re-review verdict: minor revision at worst.**  Original Draft-2 verdict follows for the record: **Major revision, publishable core.** The contribution (chance-constrained recovery-constrained network design; the VSS-misleads argument; the assurance-cost curve) is genuine and the validation chain is unusually complete. The paper survives its own worst objections because most are pre-empted in text. The remaining majors are addressable without new experiments except M1 and M4.

## Major comments
**M1 — Stage-2 revenue coefficients use central prices while the TEA samples prices.** The network model prices products deterministically inside scenarios; price risk enters only the offline TEA. Either propagate price scenarios into the SP (cheap: prices multiply revenue coefficients) or state explicitly that stage-2 revenue uncertainty is second-order for the *design* because prices carry Sobol ST ≤ 0.13 vs composition 0.62. **Resolved (Draft 3):** low-price-bound solve run, design invariant (same sites, module, 8/8 contracted); Sobol argument added; reported in §3.7.

**M2 — Single national-concentration sensitivity.** c_LGU is varied (60/15) but the national Dirichlet concentration c = 25 is fixed. A reviewer will ask for c ∈ {10, 25, 50}. **Resolved (Draft 3):** c ∈ {10,25,50} run (2,000 draws each) + SP/CC at c=10. P(≥80%) = 36/30/19% with mean pinned at ~77%: tighter knowledge makes failure MORE certain. Gas module survives the widest set. Reported as §3.7; the conclusion strengthened, as predicted.

**M3 — In-sample recalibration.** ~~Fit and validation shared the 24 cells.~~ **Resolved this pass:** leave-one-case-out CV added; worst held-out 1.87%, mean 0.52% (§2.4). Objection dead.

**M4 — Static model vs the 2023–2028 ramp.** The paper solves ρ = 0.80 steady state; the statute ramps 20→80%. A multi-period model with capacity timing is the obvious extension and a reviewer may demand at least a paragraph on why the steady-state bound is the binding case (it is: if 80% fails 70% of the time, earlier years pass trivially). **Resolved (Draft 3):** ramp-dominance argument added to §4 Limitations (early-year obligations of 20 to 50% pass trivially when 80% fails in a minority of scenarios; ramp adds timing refinement, not feasibility risk).

**M5 — Chance-constraint statistical validity at S = 100.** ~~"90% guarantee" overstated.~~ **Resolved this pass:** Clopper–Pearson 95% lower bound 0.836 computed and stated in §2.7 and §3.3; guarantee phrased as sample-based with the bound attached.

**M6 — Gas-credit creditability is a legal assumption driving the headline.** ~~Stated as fact.~~ **FULLY RESOLVED (Draft 4, primary source):** DAO 2023-02 full text read. Waste-to-fuel and waste-to-energy are NAMED creditable dispositions (Secs. 16.3.3.4, 12.2.2.2.7); incineration-exclusion nuance handled (Sec. 6.59). Conditional replaced by grounded claim + pending-standards caveat. Bonus finds integrated: Rigid/Flexible segregated crediting (16.3.3.3) and third-offense permit suspension (21.1), which completes the F2 argument. See docs/dao_2023-02_legal_read.md.

**M7 — LCA is thin relative to its visibility.** Streamlined gate-to-gate with a displacement credit that flips the sign. **Resolved by scope check:** the LCA never entered the manuscript; it lives in the thesis TEA chapter (`p6_tea.md`) with both signs reported. No paper action required.

## Minor comments (all resolved this pass unless noted)
m1 em-dash punctuation purged (0 remaining); prose de-templated, sentence rhythm varied. m2 "provably ≈ 0" contradiction fixed ("zero to within solver tolerance, for reasons we identify"). m3 pp, LGU, DKR-350 defined at first use. m4 Table 3 cells shortened to prevent mid-word breaks in Word autofit. m5 figure overlaps fixed (F1 labels, F2 headroom, F5 annotations + y-label, F6 annotation). m6 abstract density: 8 numbers retained deliberately; editor-triage argument wins. m7 nomenclature block added after §2.7 (Draft 3). m8 data-availability statement added before References (Draft 3).

## What I could not break
The validation chain (verified yields → verified flowsheet → LOOCV-validated oracle → calibrated GP → exact embedding) has no weak link a reviewer can sever without proposing new experiments. The falsified-prediction narrative in §2.4 and the self-reported artifact in §3.5 make the usual credibility attacks unavailable. The VSS finding is protected by the tight-gap discipline. The constructed uncertainty set is protected by being the stated premise plus the robust export.

## Open items ledger (for the revision letter)
| Item | Owner | Effort |
|---|---|---|
| M2 national-c sensitivity {10,25,50} | PM (code exists) | ~1 session |
| M4 ramp-dominance paragraph | PM | 1 paragraph |
| M1 optional price-robust solve | PM | ~1 session |
| M7 demote LCA to SI | PM | trivial |
| m7 notation table; m8 data statement | PM | trivial |
| DAO 2023-02 diversion-definition read | **Bien** | 1 hour |
