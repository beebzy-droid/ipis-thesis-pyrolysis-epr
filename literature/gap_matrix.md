# Gap Matrix — Phase P1 (reframed gaps — CANONICAL)
**Repo:** `ipis-thesis-pyrolysis-epr` · **Idea:** W1/A · **Target:** *Computers & Chemical Engineering*
**Status:** gaps reframed and adopted as the authoritative set. The prospectus §3 (naive wording) is superseded — apply `gap_reframe.md` to the thesis doc.

Each cited work is scored against the three gaps the thesis closes **jointly**. Scoring is against the **reframed** definitions below — the honest, defensible versions. The brief's/prospectus's original G1 and G2 are partly falsified by `wang2024optimization` (now fully verified) and by a 2013–2024 deterministic-siting literature; the reframed gaps survive that challenge.

## Gap definitions (reframed — canonical)

| ID | Prospectus §3 wording (superseded) | Reframed (defensible) definition used for scoring |
|----|-----------------|---------------------------------------------------|
| **G1** | Treats feedstock as fixed, ignoring PH MSW composition variance | Treats feed composition as an **empirically characterized stochastic quantity** propagated through surrogate yields into the design decision — not fixed, and not merely *tracked deterministically* |
| **G2** | Optimizes single plants, not decentralized-vs-centralized network siting against a recovery-rate constraint | Makes the **decentralized-vs-centralized siting decision jointly under the RA 11898 packaging-footprint recovery obligation**, with composition-dependent yields |
| **G3** | Relies on expensive rigorous simulation, which does not scale without a surrogate | Uses a surrogate that **propagates feedstock-composition uncertainty into network-scale** siting — a UQ-carrying surrogate inside a stochastic superstructure, not a single-flowsheet speed-up |

## Legend
`●` closes · `◐` partial (method/ingredient present, not the full coupling) · `○` does not address · `def` defines the constraint (policy) · `data` supplies grounding data · verification `[V]`/`[V*]`/`[P]`.

---

## Matrix

| # | Reference | Thread | G1 (stochastic composition) | G2 (siting under EPR constraint) | G3 (UQ-aware surrogate at network scale) |
|---|-----------|:------:|:---:|:---:|:---:|
| 1 | `sharuddin2016review` [V] | 1 | ○ | ○ | ○ |
| 2 | `papari2021review` [V] | 1 | ○ | ○ | ○ |
| 3 | `locaspi2023lumped` [V] | 1 | ◐ | ○ | ○ |
| 4 | `genuino2023predicting` [V] | 1 | ◐ | ○ | ○ |
| 5 | `westerhout1997kinetics` [V] | 1 | ○ | ○ | ○ |
| 6 | `bhosekar2018advances` [V] | 2 | ○ | ○ | ◐ |
| 7 | `caballero2008algorithm` [V] | 2 | ○ | ○ | ◐ |
| 8 | `cozad2014learning` [V] | 2 | ○ | ○ | ◐ |
| 9 | `wilson2017alamo` [V] | 2 | ○ | ○ | ◐ |
| 10 | `mcbride2019overview` [V] | 2 | ○ | ○ | ◐ |
| 11 | `boukouvala2013surrogate` [V] | 2 | ○ | ○ | ◐ |
| 12 | `mencarelli2020review` [V] | 3 | ○ | ◐ | ○ |
| 13 | `yeomans1999systematic` [V] | 3 | ○ | ◐ | ○ |
| 14 | `santibanez2013optimal` [V] | 3 | ○ | ◐ | ○ |
| 15 | `wang2024optimization` [V] | 3 | ◐ | ◐ | ○ |
| 16 | `cristiu2024economic` [V] | 3 | ○ | ◐ | ○ |
| 17 | `ma2023economic` [V] | 3 | ○ | ◐ | ○ |
| 18 | `sahinidis2004optimization` [V] | 4 | ◐ | ○ | ○ |
| 19 | `grossmann2016recent` [V] | 4 | ◐ | ○ | ○ |
| 20 | `li2021review` [V] | 4 | ◐ | ○ | ○ |
| 21 | `bertsimas2004price` [V] | 4 | ◐ | ○ | ○ |
| 22 | `bental2009robust` [V] | 4 | ◐ | ○ | ○ |
| 23 | `birge2011introduction` [V*] | 4 | ◐ | ○ | ○ |
| 24 | `ra11898_2022` [V] | 5 | ○ | def | ○ |
| 25 | `denr_dao_2023_02` [V] | 5 | ○ | def | ○ |
| 26 | `denr_dao_2024_04` [V] | 5 | ○ | def | ○ |
| 27 | `worldbank2021philippines` [V] | 5 | data | ○ | ○ |
| — | **THESIS W1/A (this work)** | — | **●** | **●** | **●** |

*(27 bib entries; DAO 2023-02 and 2024-04 listed separately for their distinct constraint roles.)*

---

## How to read this matrix (the argument it makes)

**No prior row scores `◐`-or-better in all three columns.** The `◐` cells cluster by thread:
- **G1 partials** = deterministic yield-vs-composition maps (Thread 1: `locaspi`, `genuino`) + uncertainty *methods* not applied here (Thread 4) + one deterministic composition-*tracking* model (`wang2024optimization`).
- **G2 partials** = siting/network/technology-selection models (Thread 3), **all deterministic, none under a recovery constraint.**
- **G3 partials** = surrogate methods (Thread 2), all at single-flowsheet scale.

**The thesis is the only row that targets `●●●` — the joint coupling.** State the contribution as the coupling, not any single column.

## The competitor row, now verified: `wang2024optimization` (row 15)

Full read complete. **Wang & Maravelias (2024), *AIChE J.* 70(8):e18464 — a deterministic MIP.** It is the only prior work with partial credit in two gap columns (`◐ ◐ ○`), but the read *strengthens* the thesis: the authors' own novelty claim is being the **first to model the impact of composition/sorting on SC design**, explicitly against fixed-composition prior work. That establishes composition-awareness as a live problem while leaving the stochastic + constrained + surrogate version unclaimed.

| Dimension | `wang2024optimization` (verified) | `cristiu2024economic` (verified) | THESIS W1/A |
|---|---|---|---|
| Composition (G1) | **Tracked deterministically** (3 MIP variants preserve composition) | Fixed deterministic scenarios | **Stochastic** — characterized distribution/uncertainty set propagated into yields |
| Yields | Fixed conversion factors | Fixed conversion factors | **Surrogate of a rigorous DWSIM flowsheet** — composition-dependent, UQ-carrying |
| Constraint (G2) | Network design objective; no recovery constraint | Multi-objective profit/GHG; no recovery constraint | **RA 11898 footprint-obligation constraint** binds siting |
| Surrogate (G3) | None | None | GP/LightGBM surrogate at network scale |
| Context | US / generic | N. Italy (in target journal) | PH island + LGU; sachet/multilayer stream |

**Consequence for the manuscript:** cite Wang & Maravelias' "first composition-aware SC design" claim, then position W1/A as the first to make that design **(a) uncertainty-aware, (b) recovery-constrained, and (c) surrogate-accelerated**. That is a clean, non-overlapping delta a CACE reviewer can accept.

## Second-closest: `santibanez2013optimal` (row 14, `○ ◐ ○`)

Canonical distributed-siting baseline — deterministic, fixed composition, fixed yields, no recovery constraint. **This is the P5 deterministic benchmark.** Quantify the value of stochastic + surrogate + constraint against this exact model class (e.g., the cost/feasibility penalty of the deterministic optimum once composition is revealed = the "cost of ignoring composition uncertainty").

## Caveats on the matrix

1. **Scoring is against the reframed gaps.** Under the prospectus's naive G1/G2, `wang2024optimization` → G1 `●` and the siting papers → G2 `●`. The stricter reframed scoring is what survives peer review — hence the mandatory `gap_reframe.md` patch to the thesis doc.
2. **`◐` spans two meanings:** "provides a method W1/A will use" (Threads 2, 4) vs. "does a deterministic version of the target problem" (Thread 3). The annotated bib distinguishes these per entry.
3. **Rows 24–27 are grounding, not competitors.** Policy defines the G2 constraint; the World Bank study supplies G1 context. Not scored as methods contributions.
4. **G2 coverage now hardened:** added `wang2024optimization` (verified) and `cristiu2024economic` (verified, in target journal). Additional deterministic-siting studies exist and can be cited if a reviewer presses — LDPE US East Coast (Sustainable Production & Consumption 2024), PUR upcycling MILP (Özkan/Lucia/Engell), Ma/Zavala infrastructure TEA — all expected to score `○/◐ ◐ ○`, reinforcing that the recovery-constrained + stochastic-composition + surrogate coupling is unoccupied.
