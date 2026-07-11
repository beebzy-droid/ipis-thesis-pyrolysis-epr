# P8 — Adversarial Review: CACE Reviewer 2 Pass on Draft 2
**Stance:** hostile-but-fair PSE reviewer, full access to the claims-to-evidence map. Verdict first, then majors, minors, and disposition.

## Verdict
**Major revision, publishable core.** The contribution (chance-constrained recovery-constrained network design; the VSS-misleads argument; the assurance-cost curve) is genuine and the validation chain is unusually complete. The paper survives its own worst objections because most are pre-empted in text. The remaining majors are addressable without new experiments except M1 and M4.

## Major comments
**M1 — Stage-2 revenue coefficients use central prices while the TEA samples prices.** The network model prices products deterministically inside scenarios; price risk enters only the offline TEA. Either propagate price scenarios into the SP (cheap: prices multiply revenue coefficients) or state explicitly that stage-2 revenue uncertainty is second-order for the *design* because prices carry Sobol ST ≤ 0.13 vs composition 0.62. *Disposition: rebut with the Sobol argument + one added sentence; optional robustness solve at price bounds in revision.*

**M2 — Single national-concentration sensitivity.** c_LGU is varied (60/15) but the national Dirichlet concentration c = 25 is fixed. A reviewer will ask for c ∈ {10, 25, 50}. *Disposition: run in revision; machinery exists (one parameter, ~40 solves). Expect the chemistry-bound conclusion to strengthen at low c.*

**M3 — In-sample recalibration.** ~~Fit and validation shared the 24 cells.~~ **Resolved this pass:** leave-one-case-out CV added; worst held-out 1.87%, mean 0.52% (§2.4). Objection dead.

**M4 — Static model vs the 2023–2028 ramp.** The paper solves ρ = 0.80 steady state; the statute ramps 20→80%. A multi-period model with capacity timing is the obvious extension and a reviewer may demand at least a paragraph on why the steady-state bound is the binding case (it is: if 80% fails 70% of the time, earlier years pass trivially). *Disposition: add the one-paragraph argument; multi-period deferred to future work explicitly.*

**M5 — Chance-constraint statistical validity at S = 100.** ~~"90% guarantee" overstated.~~ **Resolved this pass:** Clopper–Pearson 95% lower bound 0.836 computed and stated in §2.7 and §3.3; guarantee phrased as sample-based with the bound attached.

**M6 — Gas-credit creditability is a legal assumption driving the headline.** ~~Stated as fact.~~ **Resolved this pass:** policy paragraph rewritten conditionally (if creditable → module decisive; if not → obligation near-infeasible). Both branches are findings. Author-side action remains: read DAO 2023-02's diversion definitions directly.

**M7 — LCA is thin relative to its visibility.** Streamlined gate-to-gate with a displacement credit that flips the sign. *Disposition: already reported both signs; demote LCA to one paragraph + SI in revision, or drop from the paper and keep in the thesis. Recommend demote.*

## Minor comments (all resolved this pass unless noted)
m1 em-dash punctuation purged (0 remaining); prose de-templated, sentence rhythm varied. m2 "provably ≈ 0" contradiction fixed ("zero to within solver tolerance, for reasons we identify"). m3 pp, LGU, DKR-350 defined at first use. m4 Table 3 cells shortened to prevent mid-word breaks in Word autofit. m5 figure overlaps fixed (F1 labels, F2 headroom, F5 annotations + y-label, F6 annotation). m6 abstract density: 8 numbers retained deliberately; editor-triage argument wins. m7 notation table for §2.7 symbols: add in revision (open). m8 data-availability statement citing single-script figure regeneration: add at submission (open).

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
