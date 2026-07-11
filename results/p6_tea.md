# P6 — TEA + UQ + Streamlined LCA
**Basis:** SAA-robust design (Valenzuela_S + Carmona_XL + gas module), 130.2 kt/yr. MC n=10,000 over composition (P3 set) × prices × CAPEX/OPEX ±30%. Reproduce: `python src/tea_uq.py`.
**Verified anchor:** diesel retail Metro Manila **₱69.90–74.03/L** (DOE, Jul 2026) → ex-plant parity ~₱51–55/L (net excise ₱6/L, VAT 12%, margin) [derived]. Product prices held below parity (diesel cut ₱55/kg ≈ ₱46/L): conservative.

## T1 — Headline economics (UPPER BOUND — read T2 before quoting)
| Metric | Mean | P5–P95 |
|---|---|---|
| NPV (12%, 15 yr) | ₱19.1 B | 13.7–24.6 |
| IRR | 50% | 35–70% |
| Payback | 2.1 yr | 1.4–2.8 |
| Liquid yield | 964 L/t | 862–1,065 |
| **Break-even price** | **₱15.1/L** | 11.7–18.7 |
| P(NPV>0) / P(IRR>12%) | 100% / 100% | — |

## T2 — Why T1 is an upper bound, and the honest claim
The model carries **zero** feedstock acquisition, collection, sorting, land, working capital, or oil-upgrading cost, and assumes cuts sell at (below-parity) fuel prices without quality discount. The defensible statement is the **cost-headroom form**:
> At P95 break-even (₱18.7/L) vs realizable ~₱46/L, the design absorbs **~₱26–30k per tonne of unmodeled cost before NPV ≤ 0.** Literature-class estimates for collection + sorting + upgrading (₱8–15k/t [GK]) fit inside that headroom with ~2× margin.
Profit dominance also explains P4's VSS≈0; if unmodeled costs consume the headroom, penalties become material and VSS revives — noted as the P7 sensitivity link.

## T3 — Sobol on NPV: composition is the #1 economic driver
| Factor | S1 | ST |
|---|---|---|
| **oil_yield (composition)** | **0.618** | **0.621** |
| p_diesel-cut | 0.124 | 0.125 |
| capex ±30% | 0.102 | 0.102 |
| p_naphtha | 0.080 | 0.082 |
| p_wax | 0.042 | 0.043 |
| opex ±30% | 0.030 | 0.030 |
**Feedstock composition explains 62% of NPV variance — more than all prices and CAPEX combined.** G1 drives the economics, not only compliance. This is the thesis's economic closing argument and the second independent case for resin-resolved WACS data.

## T4 — Streamlined LCA (central composition; [GK] emission factors, flagged)
| Term | kgCO2e/t diverted |
|---|---|
| Transport (20 km avg) | +2.0 |
| Process (own fuel-gas combustion) | +274.4 |
| Electricity (30 kWh/t aux) | +19.5 |
| Credit: avoided upstream refining | −577.0 |
| **Net** | **−281** (≈ −0.29 kgCO2e/L) |
Credit-dominated: without the displacement credit the process is **+296 kgCO2e/t**. Both numbers reported; the sign of the result is an accounting choice, stated as such. Landfill/ocean-leakage avoidance not carbon-credited (non-GHG benefit, reported qualitatively).

## Backlog to close P6
Verify [GK]: PH industrial electricity tariff, collection/sorting cost quotes, pyrolysis-oil quality discount, PH grid EF (DOE/CCC factor). Each slots into the MC ranges without structural change.
