# Energy Audit — Step-by-Step Guide (for the P6 TEA)
**Repo:** `ipis-thesis-pyrolysis-epr` · **Use with:** your converged DWSIM file.
**What you're doing:** counting every kW the plant uses, naming what kind of energy each one is, and turning that into pesos per year. Do the steps in order. One action per step. Numbers in `[GK]` are bounded general knowledge — the TEA phase verifies them with PH quotes.

**The idea in one sentence:** every lightning-bolt (energy stream) in your flowsheet is money leaving the plant — your job is to read each one, price it, and find which ones you can cancel against each other.

---

## PART 1 — Read the numbers off your flowsheet (10 min)

1. Open your converged simulation.
2. Click energy stream **E1** (on the cooler E-101). Read its **duty in kW**. Write it down.
3. Repeat for **E2** (C-101 condenser), **E3** (C-101 reboiler), **E4** (SCOL-2 condenser), **E5** (SCOL-2 reboiler).
4. You should have (from your current run — yours will shift slightly after the mitigation fixes):

| Stream | Duty | Direction |
|---|---|---|
| E1 cooler | 369.78 kW | heat OUT (cooling) |
| E2 C-101 condenser | 154.74 kW | heat OUT (cooling) |
| E3 C-101 reboiler | 229.76 kW | heat IN (heating) |
| E4 SCOL-2 condenser | 102.15 kW | heat OUT (cooling) |
| E5 SCOL-2 reboiler | 124.65 kW | heat IN (heating) |

5. Add one row DWSIM does **not** know about — the **reactor endotherm** (the reaction happens in Python, outside DWSIM). Pyrolysis needs ~**0.5–1.5 MJ per kg of plastic** `[GK]`. For 1,000 kg/h: 1000 × (0.5 to 1.5) MJ/h ÷ 3.6 = **139–417 kW heat IN**. Use **278 kW** (1.0 MJ/kg) as the central value until P3 refines it.

---

## PART 2 — Name each duty's utility (what actually supplies/removes the heat) (10 min)

Rule of thumb: look at the **temperature** the duty happens at, then pick the cheapest utility that can reach it.

6. For each **cooling** duty, read the stream temperature it serves:
   - Above ~45 °C → **cooling water** (PH CW supply ≈ 33 °C) — cheapest.
   - Below ~45 °C → **chilled water / refrigeration** — expensive. (This is why Issue 1's −0.3 °C condenser was a trap; after the partial-condenser fix, E2 sits at ~45 °C = cooling water. ✅)
7. For each **heating** duty, read the temperature:
   - Below ~180 °C → **LP/MP steam**.
   - 180–250 °C → **MP/HP steam**.
   - 250–400 °C → **hot oil**.
   - Above ~400 °C → **fired heater** (avoid — that was Issue 3; the vacuum fix brings E5 to ~350 °C = hot oil. ✅)
   - The **reactor** (500 °C) → fired heater or the plant's own **fuel gas** (your GAS stream!).
8. Fill the utility column:

| Stream | Duty (kW) | T (°C) | Utility |
|---|---|---|---|
| E1 | 369.78 | 500→40 | cooling water (after heat recovery, Part 4) |
| E2 | 154.74 | ~45 (post-fix) | cooling water |
| E3 | 229.76 | ~260 | hot oil |
| E4 | 102.15 | ~180–240 (vacuum) | cooling water |
| E5 | 124.65 | ~350 (post-fix) | hot oil |
| Reactor | ~278 | 500 | fuel gas (own GAS stream) |

---

## PART 3 — Turn kW into MJ/kg and pesos (15 min)

9. **Specific energy** (the number that goes in the thesis): for each duty,
   `MJ per kg feed = duty_kW × 3.6 ÷ feed_kg/h`.
   Example E3: 229.76 × 3.6 ÷ 928 = **0.89 MJ/kg**.
10. Compute the totals:
    - Heating (E3 + E5 + reactor): (229.76 + 124.65 + 278) = **632 kW** → **2.45 MJ/kg feed**
    - Cooling (E1 + E2 + E4): (369.78 + 154.74 + 102.15) = **627 kW** → **2.43 MJ/kg feed**
    - Sanity check: heating ≈ cooling within ~20% for a plant like this — yours match almost exactly. ✅ (Not a coincidence — energy in must come out.)
11. **Annual energy**: `kW × 8,000 h ÷ 1,000 = MWh/yr`. Example: 632 kW heating → 5,056 MWh/yr = 18,200 GJ/yr.
12. **Price each utility** `[GK — verify with PH quotes in P6]`:

| Utility | Cost |
|---|---|
| Cooling water | ₱20–60 / GJ |
| Hot oil (gas-fired heater loop) | ₱400–700 / GJ |
| Fuel gas | free up to your own GAS production (51 kg/h ≈ **~650 kW** at ~46 MJ/kg LHV `[GK]`) — this **covers the whole 278 kW reactor duty** with margin; the rest is flare/export |
| Electricity (pumps, vacuum, air coolers) | ₱6–8 / kWh |

13. **Annual utility bill** = Σ (GJ/yr × ₱/GJ per line). With the numbers above:
    - Hot oil: (229.76+124.65) kW = 354 kW → 10,200 GJ/yr × ₱400–700 = **₱4.1–7.1 M/yr**
    - Cooling water: 627 kW → 18,100 GJ/yr × ₱20–60 = **₱0.4–1.1 M/yr**
    - Reactor fuel: **₱0** (own fuel gas covers it)
    - **Total utility OPEX ≈ ₱4.5–8.2 M/yr** (pre-heat-integration)
14. Divide by annual feed (8,000 t/yr) → **utility cost ≈ ₱560–1,030 per tonne of plastic**. That number goes straight into the TEA's cost-of-diversion metric.

---

## PART 4 — Heat integration (make hot streams pay cold streams) (15 min)

The trick: E1 throws away 370 kW of *hot* heat (500 °C!) while E3+E5 *buy* 354 kW of heat. Match them.

15. The matching rule (keep a **ΔT_min = 20 °C** gap): a hot stream can heat a cold one only while it is at least 20 °C hotter.
16. E1 cools 500 → 40 °C. E3 needs heat at ~260 °C; E5 at ~350 °C.
    - E1's 500→370 °C portion can supply **E5** (350 °C + 20).
    - E1's 370→280 °C portion can supply **E3** (260 °C + 20).
17. Roughly, the 500→280 °C slice of E1 is ~45–55% of its duty ≈ **170–200 kW recoverable**.
18. Money: 170–200 kW of hot oil displaced → 4,900–5,800 GJ/yr × ₱400–700 = **₱2.0–4.0 M/yr saved** → total utility OPEX drops to ≈ **₱2.5–4.5 M/yr** (₱310–560/t).
19. How to *model* it later (P4/P6, not now): replace E-101 with two exchangers in series — a **feed/product interchanger** (or hot-oil generator) taking the 500→280 °C duty, then a CW trim cooler for 280→40 °C. In DWSIM: two Cooler/Heater blocks, or a Heat Exchanger block with the reboiler-side stream.
20. Record all of Parts 1–4 in one table in `results/energy_audit.csv` — that file becomes TEA input. Columns: `stream, duty_kW, T_C, utility, MJ_per_kg, GJ_per_yr, PHP_per_yr_low, PHP_per_yr_high`.

---

## What you now have

- **2.45 MJ/kg heating / 2.43 MJ/kg cooling** — the plant's specific energy signature (thesis-quotable).
- **₱560–1,030/t utility OPEX**, dropping to **₱310–560/t with heat integration** — direct inputs to break-even ₱/L.
- Reactor heat **self-supplied by the fuel-gas byproduct** — a genuinely nice result for the TEA narrative (the "waste" gas closes the energy loop).
- All `[GK]` prices flagged for P6 verification with Philippine utility quotes.
