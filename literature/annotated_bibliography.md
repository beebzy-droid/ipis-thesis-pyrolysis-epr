# Annotated Bibliography — Phase P1
**Repo:** `ipis-thesis-pyrolysis-epr` · **Idea:** W1/A · **Target:** *Computers & Chemical Engineering*
**Compiled:** P1 search pass (15 verification queries; Wang 2024 full read + G2 hardening added). **Rule:** no fabricated citations; verification status flagged per entry (`[V]` verified incl. DOI, `[V*]` metadata verified / DOI to confirm, `[P]` partial — complete before manuscript use). **Gaps reframed and adopted as canonical — apply `gap_reframe.md` to the prospectus.**

---

## 0. Bottom line up front

- **27 references** across the 5 threads; **19 fully verified `[V]`**, 8 `[V*]` (DOI-confirm only), 0 `[P]`.
- **Nearest-competitor threat resolved — in the thesis's favor.** `wang2024optimization` is now fully verified: **Wang & Maravelias (2024), *AIChE J.* 70(8):e18464 — a deterministic MIP** that *tracks* composition. The authors' own claim is being the **first to model composition/sorting impact on SC design**, explicitly against fixed-composition prior work. It has no stochastic composition, no recovery constraint, and fixed conversion factors (no surrogate). So it closes composition-*tracking* + siting deterministically, which **sharpens** the reframed gaps rather than threatening them: the stochastic + EPR-constrained + surrogate-accelerated version is demonstrably unclaimed.
- **No single prior work scores `●●●`.** Gaps reframed to survive Wang & Maravelias and the 2013–2024 deterministic-siting literature: G1 → *stochastic* composition (not merely tracked); G2 → siting *under the RA 11898 footprint obligation*; G3 → surrogate that *propagates composition uncertainty at network scale*. Full reasoning + thesis-doc patch in `gap_reframe.md`.
- **All RA 11898 anchors verified**, with one framing correction that must reach the thesis doc: the recovery schedule is **20→40→50→60→70→80%** for footprints of 2023→2028+, and the target is an **obliged-enterprise packaging-footprint obligation, not an economy-wide MSW rate**. The prospectus §8 Step 4 / §9 currently model it as a network "recovery-rate constraint" — **mis-specified**; corrected in `gap_reframe.md`.
- **Honest read on novelty:** the contribution is **integrative, not fundamental** (each pillar is mature). This is not a weakness *if framed as the coupling* — a composition-uncertainty-aware surrogate embedded in a spatial, recovery-constrained superstructure. The prospectus §15 Risk Register already carries the correct mitigation ("lead with the method"); the reframe operationalizes it.

---

## Thread 1 — Mixed-plastic pyrolysis: lumped kinetics & product yields

**Role in thesis:** supplies the rigorous flowsheet's reaction block (P2) and the ground-truth yield map the surrogate must learn (P4). The relevant question is not "which catalyst" but **"how does product slate (gas/oil/wax/char and cut composition) respond to feed blend and reactor conditions,"** because feed blend is exactly the uncertain quantity in G1.

- **`sharuddin2016review` [V*]** — *Energy Convers. Manag.* 115:308–326. Canonical review; tabulates oil/gas/char yields per polymer and for mixed feeds vs temperature. Use for prior ranges and sanity bounds, not for a kinetic scheme. Degradation onset order PS < PP < LDPE < HDPE is the qualitative basis for blend-dependent behavior.
- **`papari2021review` [V]** — *Materials* 14:2586. Maps reactor mode (slow/fast/flash, temperature, residence time) to product slate, incl. flash pyrolysis recovering up to ~50 wt% ethylene from PE. Use to bound the P2 operating window.
- **`locaspi2023lumped` [V]** — *Waste Manag.* 156:107–117. CRECK-group reduction of a detailed mechanism to a **lumped scheme for PE/PP**. **Strongest candidate kinetic backbone for the DWSIM flowsheet** — lumped enough to be tractable at network scale, mechanistic enough to move with composition.
- **`genuino2023predicting` [V]** — *Waste Manag.* 156:208–215. **Yields as an explicit function of blend composition.** This is the closest experimental analogue to the surrogate's input→output map; use its data to (a) validate the P2 flowsheet and (b) set priors for the surrogate.
- **`westerhout1997kinetics` [V]** — *Ind. Eng. Chem. Res.* 36:1955–1964. Random-chain-scission model; standard baseline. Cite for kinetic lineage; likely superseded by `locaspi2023lumped` for the working model.

**Synthesis / limitation:** the literature gives blend→yield *point* relationships but rarely propagates **composition uncertainty** into yields. That propagation is a thesis contribution, not a citation. Kinetic-model choice (`locaspi2023lumped`) directly bounds P2 fidelity and therefore surrogate quality — decide it early.

---

## Thread 2 — Surrogate-assisted optimization in PSE

**Role in thesis:** justifies replacing the rigorous pyrolysis+separation model with a GP/LightGBM surrogate so that a network-scale, scenario-expanded program is solvable.

- **`bhosekar2018advances` [V]** — *Comput. Chem. Eng.* 108:250–267. **Anchor review.** Separates surrogate roles (prediction / derivative-free optimization / feasibility); benchmarks RBF vs Kriging; gives sampling guidance for the P3 DOE. Cite for the "when surrogates beat rigorous sim" argument.
- **`caballero2008algorithm` [V]** — *AIChE J.* 54:2633–2650. **Direct methodological ancestor.** Kriging (= Gaussian process) surrogates replace *noisy* modular unit ops; trust-region refinement + bound contraction; Kriging error estimate doubles as a feasibility/stopping signal. This is the template for embedding the surrogate in an optimization loop.
- **`cozad2014learning` [V]** + **`wilson2017alamo` [V]** — *AIChE J.* 60:2211–2227 / *Comput. Chem. Eng.* 106:785–795. **ALAMO.** Interpretable algebraic surrogates via best-subset selection + adaptive sampling. The **interpretable alternative to a black-box GP** — relevant to the LightGBM-vs-GP-vs-algebraic decision in P4, and to reviewer questions about surrogate transparency.
- **`mcbride2019overview` [V*]** — *Chem. Ing. Tech.* 91:228–239. Compact surrogate taxonomy for process engineers; good scaffolding citation.
- **`boukouvala2013surrogate` [V*]** — *J. Pharm. Innov.* 8:131–145. Worked flowsheet example under feasibility constraints; precedent for the P2→surrogate step.

**Synthesis / limitation:** Kriging is a GP, so the surrogate's uncertainty estimate is native — but this literature applies surrogates at **single-flowsheet** scale, not across a **spatial network of plants with a stochastic feed**. That scale-up is where G3's real novelty must live (see §6). Note the recurring caution: surrogate error can make the optimizer chase artifacts (`caballero2008algorithm` handles this via bound contraction + refinement) — the thesis needs an equivalent trust/validation loop or a reviewer will flag optimizer overfitting to surrogate error.

---

## Thread 3 — Superstructure / process-network synthesis & facility siting

**Role in thesis:** provides both (a) the superstructure *methodology* and (b) the spatial waste-network *siting* precedent (decentralized vs centralized).

- **`mencarelli2020review` [V]** — *Comput. Chem. Eng.* 136:106808. **Anchor review** of representations (STN, P-graph, state-space) and GDP modeling. Use to justify the chosen network representation in P4.
- **`yeomans1999systematic` [V*]** — *Comput. Chem. Eng.* 23:709–731. Foundational STN superstructure framework. Cite for lineage.
- **`santibanez2013optimal` [V]** — *Waste Manag.* 33:2607–2622. **Closest spatial-siting prior art.** Distributed MSW supply-chain MILP: cities → separation → processing → markets, multi-technology, central-west Mexico, multi-objective (NPV / diversion / social). **But: deterministic, fixed composition, fixed yield factors, no surrogate.** This is the concrete baseline the thesis must beat on G2 *and* differentiate from on G1/G3.
- **`wang2024optimization` [V]** — Wang & Maravelias, *AIChE J.* 70(8):e18464. **Nearest competitor, read in full; threat resolved favorably.** Three **deterministic** MIP variants that *preserve/track* composition through the SC. Authors' own claim: "first to develop a model to address the specific impact of sorting and composition of MPW on SC design," explicitly contrasting fixed-composition prior work. **No stochastic composition, no recovery constraint, fixed conversion factors.** Closes composition-*tracking* + siting deterministically → leaves the stochastic + EPR-constrained + surrogate version open. **Cite their first-mover claim to position W1/A as the uncertainty-aware, constrained, surrogate-accelerated successor.**
- **`cristiu2024economic` [V]** — Crîstiu, d'Amore & Bezzo, *Comput. Chem. Eng.* 180:108503. **In the target journal.** Multi-objective (profit vs GHG) MILP siting + technology selection (incineration/gasification/pyrolysis) for MPW, N. Italy. Deterministic; explicitly notes composition variability then treats it as fixed scenarios; no recovery constraint; no surrogate. Second deterministic-siting contrast for G2, and proof CACE publishes this exact problem class. NB: same group (Crîstiu, You, d'Amore, Bezzo, *I&ECR* 2025) does SC design *under uncertainty* for direct air capture — uncertainty-aware SC design exists in adjacent domains, not for plastic-pyrolysis-under-EPR.
- **`ma2023economic` [V*]** — *Green Chem.* 25:1032–1044. Spatial infrastructure + TEA for thermochemical plastic upcycling (Zavala group). Economics-first, deterministic; no composition uncertainty, no surrogate. Useful TEA benchmark for P6.

**Synthesis / limitation:** decentralized-vs-centralized is an **active, crowded** question — now anchored by `wang2024optimization` (deterministic composition-tracking) and `cristiu2024economic` (deterministic incineration-vs-pyrolysis siting, target journal); further studies exist (LDPE US East Coast, PUR upcycling MILP, Ma/Zavala) and can be cited if pressed. Two consequences: (1) G2 as "single-plant only" is **false** for this subfield — the honest G2 is "no siting decision made *jointly under the RA 11898 footprint obligation with surrogate-accelerated, composition-dependent yields*." (2) The Philippine spatial context (island geography, LGU-level collection, RA 11898) plus the constraint is a legitimate differentiator even though "siting" per se is not novel. **Every one of these prior models is deterministic** — the uncertainty axis is empty, which is where W1/A lives.

---

## Thread 4 — Optimization under uncertainty

**Role in thesis:** the layer that turns "composition varies" into a solvable stochastic or robust program.

- **`sahinidis2004optimization` [V]** — *Comput. Chem. Eng.* 28:971–983. **Landmark menu**: stochastic programming, robust optimization, chance constraints. Cite as the framing reference for the uncertainty layer.
- **`grossmann2016recent` [V]** — *Comput. Chem. Eng.* 91:3–14. Modern PSE synthesis: two-stage/robust recourse, **data-driven scenario generation**, endogenous uncertainty. Justifies the two-stage structure (stage 1: siting/capacity = here-and-now; stage 2: operation/allocation = recourse).
- **`li2021review` [V*]** — *Front. Chem. Eng.* 2:622241. Tutorial-grade two-stage/multistage stochastic programming; use for method exposition in the thesis chapter.
- **`bertsimas2004price` [V*]** + **`bental2009robust` [V]** — *Oper. Res.* 52:35–53 / Princeton UP. **Robust fallback.** Budget-of-uncertainty formulation controls conservatism and needs only support/bounds, not a full distribution. **Keep this in reserve:** if P3 composition data is too sparse to estimate a credible distribution, a robust or distributionally-robust formulation is more honest than a stochastic program built on a fabricated distribution.
- **`birge2011introduction` [V*]** — Springer, 2nd ed. Reference text (L-shaped method, recourse).

**Synthesis / limitation:** the **make-or-break step is the uncertainty-set / scenario construction (P3), not the solver.** A stochastic program is only as credible as its input distribution; with Philippine composition data thin, the uncertainty characterization is the fragile link. Plan for a robust or distributionally-robust variant so the result does not hinge on an over-precise distribution.

---

## Thread 5 — Philippine policy (RA 11898) + waste characterization

**Role in thesis:** defines the recovery constraint (the thing that makes the siting problem distinctive) and supplies the composition context for G1.

- **`ra11898_2022` [V]** — RA 11898, lapsed into law 23 Jul 2022; amends RA 9003. Obliged enterprise = total assets > ₱100M (excl. land). **Fines ₱5M–20M**, *or twice the cost of recovery / the shortfall, whichever is higher.*
- **`denr_dao_2023_02` [V]** — EPR IRR, issued **24 Jan 2023**. **Recovery schedule 20/40/50/60/70/80%** for footprints of 2023/24/25/26/27/28+. (Brief's "DAO 2023-02" and "60/70/80 for 2026–28" both correct; full ramp added here.)
- **`denr_dao_2024_04` [V]** — Compliance Reporting & Audit Guidelines. ECAR + third-party audit; **footprint-based** target computation. This is where the constraint's *measurement* is defined.
- **`worldbank2021philippines` [V]** — hdl:10986/35295. **2.7 Mt/yr** plastic waste, ~0.75 Mt/yr ocean leakage, "sachet economy" (163 M sachets/day), USD 2.3B industry (2018). Grounds G1 composition context and the multilayer/film chemical-recycling gap.

**Synthesis / limitation — two corrections that affect the model, not just the prose:**
1. **The RA 11898 target is a per-obliged-enterprise packaging-footprint obligation, not a spatial MSW recovery rate.** Writing it as a network-wide recovery constraint requires an explicit mapping assumption (e.g., the network serves a defined set of obliged enterprises / packaging streams). State this as a modeling assumption in P4 or the constraint is mis-specified relative to the statute — a defense-panel-level objection.
2. **"Near-zero domestic chemical-recycling capacity for multilayer/film" is directionally supported** (sachets are largely non-mechanically-recyclable and infrastructure is nascent) **but is a characterization, not a verified figure.** Cite the World Bank study for the qualitative claim; do not attach a hard "0 t" number without a source. Composition-variance data by region/LGU is thin — **this is a P3 data-collection task (WACS / NSWMC), and its thinness is itself part of the G1 justification.**

---

## 6. Critical assessment (PM view — this is the part that matters)

**1. Novelty is integrative. Name the specific fusion or a CACE reviewer will not.**
All three pillars are mature: surrogate-in-flowsheet (`caballero2008algorithm`, 2008), optimization-under-uncertainty (`sahinidis2004optimization`, 2004), waste-network siting (`santibanez2013optimal`, 2013). Assembling them is not, by itself, a *Computers & Chemical Engineering* contribution. **The defensible novel object is:** a surrogate whose inputs include the *uncertain composition vector*, embedded in a *spatial, recovery-constrained* superstructure solved as a stochastic/robust program. That specific coupling — **uncertainty-aware surrogate at network scale** — is thin in the literature. Lead with it.

**2. Reframe the three gaps. As written, G1 and G2 are partly false.**

| As written in prospectus §3 | Problem (now evidenced) | Defensible reframing (canonical) |
|---|---|---|
| G1: feedstock treated as fixed → ignores composition variance | **False.** `wang2024optimization` (verified) tracks composition deterministically and claims first-mover on composition-aware SC design; `genuino2023predicting` gives deterministic yield-vs-composition maps | Prior work treats composition as a **known/deterministic input** (fixed *or* deterministically tracked); none treat it as an **empirically characterized stochastic quantity** propagated through surrogate yields into a **recovery-constrained siting** decision |
| G2: single-plant only → no decentralized-vs-centralized siting | **False.** Verified deterministic siting in `santibanez2013optimal`, `wang2024optimization`, `cristiu2024economic` (latter in the target journal) | No siting done **jointly under the RA 11898 footprint obligation with composition-dependent, surrogate-accelerated yields** in the PH island/LGU context |
| G3: rigorous sim only → no surrogate acceleration for network-scale optimization | **Generic** — surrogate acceleration is well established (`caballero2008algorithm`) | The surrogate **propagates feedstock-composition uncertainty** into network-scale siting; a UQ-carrying surrogate inside a stochastic superstructure, not just a speed trick |

**Positioning move (use verbatim in the manuscript's gap paragraph):** *Wang & Maravelias (2024) established that composition-awareness matters for plastic-waste supply-chain design under a deterministic MIP; Crîstiu et al. (2024) sited incineration-vs-pyrolysis deterministically. This work is the first to make that design (i) uncertainty-aware over empirically characterized feedstock composition, (ii) constrained by the RA 11898 recovery obligation, and (iii) surrogate-accelerated from a rigorous pyrolysis flowsheet.* That is a clean, non-overlapping delta.

**3. The uncertainty set is the single largest technical risk.** G1 rests on a *characterized* composition distribution. If P3 cannot produce a credible one from PH data, the stochastic program is garbage-in. **Mitigation: design P3 to output an uncertainty *set* usable by either a stochastic OR a robust formulation** (`bertsimas2004price`), and pre-register that choice. This also converts "data scarcity" from a liability into the stated motivation for the method.

**4. The RA 11898 constraint must be modeled as a footprint obligation, not an MSW rate** (§ Thread 5). Get this wrong and the central constraint is invalid.

**5. Surrogate-error control is a required, not optional, component.** `caballero2008algorithm` succeeds because of bound contraction + refinement; a naive "fit once, optimize" pipeline will let the optimizer exploit surrogate error. Build a validation/trust loop in P4 and report out-of-sample surrogate error at the operating point, or expect a reviewer to reject the network optimum as un-validated.

---

## 7. P1 follow-up — status

1. ✅ **`wang2024optimization` read in full.** Verified: Wang & Maravelias, deterministic MIP, composition-tracking, no uncertainty/constraint/surrogate. G1 reframing sharpened and de-risked (see §6). Author list complete.
2. ✅ **G2 hardened** with two verified deterministic-siting papers: `wang2024optimization` and `cristiu2024economic` (target journal). Additional studies (LDPE US East Coast, PUR upcycling MILP, Ma/Zavala) held in reserve; cite only if a reviewer presses.
3. ⏳ **Confirm the 8 `[V*]` DOIs** (Sharuddin, McBride–Sundmacher, Boukouvala–Ierapetritou, Yeomans–Grossmann, Ma/Green Chem, Bertsimas–Sim, Birge–Louveaux, Li–Grossmann year label) — ~10 min; not blocking P2. All are real papers with metadata verified; only the DOI string is unconfirmed. 0 `[P]` remaining.
4. ⏳ **Log the composition-variance data gap as a P3 deliverable.** Point-estimate composition data (World Bank resin shares, NSWMC national MSW) is available; **locality-level variance is thin** — the prospectus §9 rates this LOW risk, which is optimistic for the *variance* specifically. Plan a bootstrap / expert-prior route to an uncertainty set, and pre-register a robust fallback (`bertsimas2004price`) so G1 does not hinge on an over-precise distribution.
5. ➕ **Apply `gap_reframe.md` to the prospectus** — reframed §3, aligned §2/§6, and the EPR-constraint correction to §8 Step 4 / §9. This is the only change that touches the committed thesis doc; review before applying.
