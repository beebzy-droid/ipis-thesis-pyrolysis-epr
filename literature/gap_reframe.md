# Gap Reframe — patch for `01_pyrolysis-epr-network.docx`
**Repo:** `ipis-thesis-pyrolysis-epr` · **Idea:** W1/A
**Purpose:** apply the P1 evidence to the prospectus. Five edits: §2, §3, §6 (gap/novelty reframe), §8 Step 4 + §9 (EPR-constraint mis-specification fix), §9 (composition-variance data-risk correction).
**Why:** the prospectus §3 states G1/G2 in forms that verified literature falsifies — `wang2024optimization` (deterministic composition-tracking, self-described first-mover) and a 2013–2024 deterministic-siting literature. The reframed gaps survive that challenge; the naive ones invite a desk-reject at CACE. Review each diff before applying — this touches the committed thesis doc.

---

## Edit 1 — §3 Research Gap (the core reframe)

**BEFORE:**
> The plastic-pyrolysis techno-economic literature is saturated but three gaps remain jointly unaddressed: (1) it treats feedstock as fixed, ignoring the high composition variance of Philippine MSW; (2) it optimizes single plants, not decentralized-vs-centralized network siting against a recovery-rate constraint; and (3) it relies on expensive rigorous simulation, which does not scale to network-level optimization without a surrogate.

**AFTER:**
> The plastic-pyrolysis techno-economic literature is saturated, and recent work is more advanced than a naive gap statement suggests: composition-aware supply-chain design (Wang & Maravelias, 2024) and deterministic decentralized-vs-centralized siting (Santibañez-Aguilar, 2013; Crîstiu et al., 2024) already exist. Three gaps nonetheless remain **jointly** unaddressed. **(1) Deterministic feedstock.** Prior models treat composition as a known input — fixed across locations, or at most deterministically *tracked* through the network — never as an empirically characterized **stochastic** quantity whose variance is propagated into product yields. **(2) Unconstrained siting.** The siting question is studied deterministically but never **jointly under a binding recovery obligation** such as RA 11898, with composition-dependent yields. **(3) Sim-only, single-scale surrogates.** Surrogate acceleration of flowsheet optimization is established at single-flowsheet scale but is not used to **propagate feedstock-composition uncertainty into network-scale** siting. The contribution is the **coupling** of the three: a composition-uncertainty-aware surrogate, embedded in a spatial superstructure, solved under the EPR recovery obligation.

**Rationale:** cites the two closest competitors *by name and up front* (pre-empts the reviewer who knows them), then carves the delta on the three axes each competitor leaves empty — uncertainty, constraint, surrogate-scale. The competitors' own framing (composition matters; deterministic) does the work of justifying the reframe.

---

## Edit 2 — §2 Problem Statement (footprint-obligation framing + characterized uncertainty)

**BEFORE:**
> …at what scale and spatial configuration can a pyrolysis network meet the 60→80% recovery trajectory at minimum total cost and carbon, given the composition and variability of actual local waste streams?

**AFTER:**
> …at what scale and spatial configuration can a pyrolysis network satisfy the RA 11898 recovery obligation (a rising share of the plastic-packaging **footprint** it serves — 60% for 2026 rising to 80% by 2028) at minimum total cost and carbon, given the **empirically characterized composition uncertainty** of actual local waste streams?

**Rationale:** "recovery trajectory" reads as an economy-wide MSW rate; the statute is a per-obliged-enterprise footprint obligation. "variability" → "characterized composition uncertainty" aligns the problem statement with the stochastic method.

---

## Edit 3 — §6 Novelty Statement (claim the delta over Wang & Crîstiu; fix "recovery-rate constraint")

**BEFORE:**
> A Bayesian/Gaussian-process surrogate of a rigorous pyrolysis-plus-separation flowsheet is embedded in a spatial superstructure optimization that is solved as a stochastic/robust program over empirically-characterized Philippine feedstock composition uncertainty, subject to the EPR recovery-rate constraint. The defensible contribution is the method and the PH-specific decentralized design, not the reaction itself.

**AFTER:**
> A Bayesian/Gaussian-process surrogate of a rigorous pyrolysis-plus-separation flowsheet is embedded in a spatial superstructure optimization solved as a stochastic/robust program over empirically-characterized Philippine feedstock-composition uncertainty, subject to the RA 11898 recovery obligation. Prior work has taken these ingredients only **separately and deterministically** — composition-aware supply-chain design (Wang & Maravelias, 2024) and incineration-vs-pyrolysis siting (Crîstiu et al., 2024) are both deterministic and unconstrained by a recovery target. The defensible contribution is their **coupling** — an uncertainty-aware surrogate inside a recovery-constrained spatial superstructure — plus the PH-specific decentralized design, not the reaction itself.

---

## Edit 4 — §8 Step 4 + §9 (EPR-constraint mis-specification — **model-level fix, not cosmetic**)

The prospectus models RA 11898 as a network "recovery-rate constraint." The statute is a **packaging-footprint obligation on obliged enterprises**, reported per enterprise via the ECAR (DAO 2024-04), computed as a % of the prior-year footprint. Modeling it as an economy-wide MSW recovery rate is **mis-specified** and is a defense-panel-level objection.

**§8 Step 4 — BEFORE:**
> …stochastic/robust formulation minimizing expected total cost + carbon subject to recovery-rate constraint.

**§8 Step 4 — AFTER:**
> …stochastic/robust formulation minimizing expected total cost + carbon subject to the RA 11898 recovery obligation, modeled as a **footprint-based recovery constraint** — the network must recover at least the mandated fraction (60→80%) of the defined packaging-footprint stream it serves — **not** as an economy-wide MSW recovery rate. The footprint→served-stream mapping is stated as an explicit modeling assumption (e.g., the network serves the aggregated packaging footprint of a defined set of obliged enterprises or LGU catchments).

**§9 Data Sources — EPR row, "What it unlocks" — BEFORE:** `Hard constraint + penalty term`
**AFTER:** `Footprint-obligation constraint (% of served packaging footprint) + non-compliance penalty (₱5–20M or 2× recovery-cost shortfall). Requires an explicit footprint→network mapping assumption.`

---

## Edit 5 — §9 Data Sources (composition-variance risk is under-rated)

Point-estimate composition data is LOW risk (World Bank resin shares; NSWMC national MSW composition). **Locality-level composition *variance* — the empirical basis for G1 — is thin**, and G1 is the thesis's headline gap. Rating it LOW is optimistic.

**§9 Waste-composition row, "Risk" — BEFORE:** `LOW`
**AFTER:** `LOW (point estimates) / MEDIUM (locality-level variance)`

**§9 Waste-composition row, "What it unlocks" — BEFORE:** `Feedstock scenarios + uncertainty ranges for the stochastic program`
**AFTER:** `Feedstock scenarios + uncertainty ranges. If only national aggregates exist, construct the uncertainty set via bootstrap / expert priors; pre-register a robust fallback (Bertsimas & Sim, 2004) so results do not hinge on an over-precise distribution.`

**Add to §15 Risk Register:**
> | Composition-variance data thin → weak uncertainty set | Build the uncertainty *set* to serve either a stochastic OR a robust formulation; pre-register the robust fallback; treat data scarcity as the stated motivation for the UQ method, not a hidden weakness. |

---

## New reference introduced by this reframe (already in `references.bib`)

- `cristiu2024economic` — Crîstiu, d'Amore & Bezzo (2024), *Comput. Chem. Eng.* 180:108503. [V] In the target journal; deterministic incineration-vs-pyrolysis MPW siting. Cited in §3 and §6.
- `wang2024optimization` — upgraded to [V]: Wang & Maravelias (2024), *AIChE J.* 70(8):e18464. Cited in §3 and §6.

## Applying this patch
These five edits are prose-level and touch the committed prospectus. Two options: (a) apply them yourself from the diffs above; (b) say the word and I will edit the `.docx` in place (unzip → `document.xml` → rezip; the affected paragraphs are contiguous prose and will patch cleanly without disturbing the tables/callout boxes). Recommend (a) for §2/§3/§6 (intellectual changes you should own) and (b) is fine for the mechanical §8/§9 table edits.
