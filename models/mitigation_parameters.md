# Mitigation Parameters — the 3 flagged issues (P2 verified build)
**Repo:** `ipis-thesis-pyrolysis-epr` · applies to `pyrolysis_base.dwxmz` (converged, V1=0.00083%)
**Cost figures:** bounded estimates, general knowledge flagged `[GK]`, verified in P6 TEA. Basis 8,000 h/yr, PH industrial electricity ₱6–8/kWh `[GK]`, feed 1,000 kg/h plastic (928 kg/h to DWSIM).

---

## Issue 1 — NAPHTHA condenser at −0.29 °C (refrigeration trap)

**Root cause (verified from your run):** light gas (CH₄/C₂H₄) not stripped in V-101 rides into C-101 overhead; 7.1 mol% lights in the distillate pins the condenser dew point below 0 °C. E2 = 154.74 kW would need refrigeration, not cooling water.

**Why it matters in the Philippines specifically:** tropical cooling water supply is ~32–33 °C (cooling-tower approach on a 27–29 °C wet bulb) `[GK]`. Anything condensing below ~40 °C is already marginal on CW; below 0 °C means a chiller/refrigeration plant.

**Fix — change ONE setting on C-101: total → PARTIAL condenser.**

| Parameter | Set to | Effect |
|---|---|---|
| C-101 condenser type | **Partial (vapor + liquid distillate)** | lights leave as a small vapor vent; naphtha is the liquid distillate |
| Condenser temperature spec | **45 °C** | CW-coolable (ΔT ≈ 12 °C over 33 °C CW supply) |
| Vapor vent routing | to fuel-gas header (join GAS) | ~11 kg/h lights, keeps mass balance closed |
| Reflux ratio | keep 2 (raise to 3 if convergence complains) | — |

**Money:** refrigeration avoided = 154.74 kW<sub>th</sub> ÷ COP 2.5 ≈ 62 kW<sub>e</sub> → 495 MWh/yr → **₱3.0–4.0 M/yr saved** vs ~₱0.1–0.2 M/yr for CW `[GK]`. This is the single highest-value fix.

**Verify after change:** NAPHTHA stream T ≈ 40–50 °C; purity should rise from 92.9 → ≥97 mol%; mass balance still ≤0.1%.

---

## Issue 2 — ~11 kg/h naphtha lost to fuel gas (3.5% of naphtha)

**Root cause:** the 40 °C flash in V-101 leaves naphtha vapor in equilibrium with the gas — C_4429 is 21.9 mass% of the GAS stream.

**Decision: ACCEPT at P2 — do not chase it with cold.** Recovering it by dropping V-101 to 25 °C requires chilled water (PH CW floor ≈ 33 °C), i.e., a chiller on the whole 928 kg/h stream to save 11 kg/h. The cure costs more than the disease.

| Parameter | Value |
|---|---|
| V-101 flash temperature | **keep 40 °C** (PH CW practical floor) |
| Accepted loss | 11 kg/h naphtha → fuel gas = 88 t/yr |
| Value of loss | **₱3.1–4.8 M/yr** at naphtha ₱35–55/kg `[GK]` — but it is *not* wasted: it burns in the fuel-gas header, offsetting ~0.5 MJ/kg-feed of purchased fuel (~₱1.3–2.0 M/yr credit) |
| Net exposure | **₱1.5–3.0 M/yr** |
| P4 design lever (logged, not built now) | sponge-oil absorber on GAS using a WAX slipstream as lean oil; typical recovery 70–80% `[GK]`; evaluate in the network optimization as a CAPEX/OPEX trade |

---

## Issue 3 — WAX reboiler at 408 °C (fired-heater trap + cracking risk)

**Root cause:** atmospheric SCOL-2 must boil the wax bottoms → 408 °C. Two problems: (a) steam tops out ~250 °C and standard hot-oil fluids (Therminol/Dowtherm class) top out ~400 °C film temperature `[GK]` — 408 °C forces a **fired heater**; (b) paraffin wax **thermally cracks above ~370–380 °C** at reboiler residence times `[GK]` — you'd be running an unintentional second pyrolysis reactor in the column sump, fouling it.

**Fix — run SCOL-2 under vacuum (this is exactly why refineries have vacuum columns).**

| Parameter | Set to | Effect |
|---|---|---|
| SCOL-2 condenser pressure | **0.25 bar (25 kPa)** | — |
| SCOL-2 reboiler pressure | **0.30 bar** (small column ΔP) | bottoms T drops to ≈ **340–360 °C** (verify in DWSIM after the change) |
| Reboiler utility | **hot oil** (≤400 °C class) — no fired heater | avoids ₱15–30 M CAPEX for a fired heater `[GK]` at this scale |
| Cracking margin | bottoms ~350 °C < 370 °C onset | fouling risk retired |
| New equipment implied | vacuum system (steam ejector or liquid-ring pump), ~5–15 kW duty equivalent | small; standard |

**Verify after change:** SCOL-2 bottoms T ≤ 360 °C; DIESEL purity holds ≥95%; condenser T stays CW-coolable (vacuum lowers it — if DIESEL condenser drops below ~45 °C, back the condenser pressure up toward 0.35 bar).

---

## Heat integration — the fourth number that isn't an issue but is money

E1 rejects **369.78 kW** cooling the 500 °C reactor product to 40 °C. The 500→250 °C portion (≈ 45–55% of the duty ≈ **170–200 kW**) is above both reboiler temperatures and can supply them via a hot-oil loop or direct feed/effluent exchange, cutting the 354 kW reboiler demand by ~50%.

| Target | Value |
|---|---|
| Recoverable high-grade heat | 170–200 kW (ΔT_min = 20 °C) |
| Utility displaced | hot oil/steam, ₱300–700/GJ `[GK]` → **₱1.5–3.5 M/yr** |
| P2 action | none (record it); build the exchanger match in P4/P6 |

---

## Rolled-up impact

| Item | Annual value |
|---|---|
| Issue 1 fix (partial condenser) | +₱3.0–4.0 M/yr avoided OPEX |
| Issue 2 accept (net of fuel-gas credit) | −₱1.5–3.0 M/yr exposure, lever logged |
| Issue 3 fix (vacuum column) | avoids ₱15–30 M CAPEX + cracking/fouling risk |
| Heat integration (P4/P6) | +₱1.5–3.5 M/yr potential |

**Build order for you in DWSIM (10 min):** ① C-101 condenser → partial, T = 45 °C, vent to GAS. ② SCOL-2 pressures → 0.25/0.30 bar. ③ Re-run (F5). ④ Check: mass balance ≤0.1%, NAPHTHA T ≈ 45 °C, SCOL-2 bottoms ≤360 °C, purities ≥95%. That converged file is the **verified-and-mitigated** base model — save as `models/pyrolysis_base_v2.dwxmz`.
