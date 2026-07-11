# DWSIM 6-Point Validation — Step-by-Step Walkthrough
**Do the steps in order. One action per step. Total ~45 min. You need: `pyrolysis_base_v2.dwxmz`, the numbers table below, a piece of paper or the results table at the bottom.**

## PART 0 — Protect your verified file (2 min)
1. Open DWSIM.
2. **File → Open** → `pyrolysis_base_v2.dwxmz`.
3. **File → Save As** → name it `pyrolysis_validation.dwxmz`. ← you will do all validation in THIS copy. Your verified v2 file stays untouched.

## PART 1 — Understand what you're doing (1 min)
You will run the same flowsheet 6 times. Each time, you change ONLY the 7 numbers in the FEED stream (the component mass flows), press F5, and write down 4 numbers (the product mass flows). Nothing else changes — not temperatures, not pressures, not column settings. Just FEED in, 4 numbers out, 6 times.

## PART 2 — Run Case V1 (7 min; V2–V6 are identical repeats)
4. **Double-click the FEED stream** (far left of the flowsheet).
5. In the properties panel, find **Temperature** — confirm it still says **500 °C**. Don't change it.
6. Find **Pressure** — confirm **1 bar**. Don't change it.
7. Find the **composition / component mass flows** section (where you originally typed the 7 compound flows). Set the basis to **Mass Flows (kg/h)** if it isn't already.
8. Type these 7 numbers for **V1** (replace whatever is there):

| Compound | kg/h |
|---|---|
| Methane | 14.6 |
| Ethylene | 22.6 |
| Propylene | 22.6 |
| Propane | 14.6 |
| NAPHTHA (pseudo) | 281.1 |
| DIESEL (pseudo) | 320.6 |
| WAX (pseudo) | 187.9 |

9. Check the **total mass flow** now reads **864.0 kg/h** (±0.5). If not, one number was mistyped — recheck against the table.
10. Close the FEED editor. Press **F5**. Wait until all blocks are green.
11. Now read 4 numbers. Double-click each product stream and write down its **Mass Flow (kg/h)**:
    - `NAPHTHA-S` → write it in the results table under V1
    - `DIESEL` → write it
    - `WAX` → write it
    - `FUELGAS` → write it
12. That's Case V1 done.

## PART 3 — Repeat for V2 through V6 (7 min each)
13. Repeat steps 4–11 five more times, using each row below for the FEED numbers:

| Case | Methane | Ethylene | Propylene | Propane | NAPHTHA | DIESEL | WAX | Total check |
|---|---|---|---|---|---|---|---|---|
| V2 | 15.6 | 24.2 | 24.2 | 15.6 | 256.8 | 292.8 | 171.7 | 800.9 |
| V3 | 13.1 | 20.3 | 20.3 | 13.1 | 305.5 | 348.4 | 204.2 | 924.9 |
| V4 | 18.8 | 29.2 | 29.2 | 18.8 | 263.3 | 300.2 | 176.0 | 835.5 |
| V5 | 14.2 | 22.1 | 22.1 | 14.2 | 280.7 | 320.1 | 187.7 | 861.1 |
| V6 | 14.7 | 22.8 | 22.8 | 14.7 | 272.9 | 311.2 | 182.5 | 841.7 |

14. If any case fails to converge (red blocks): press F5 once more. If still red, note which case and which block turned red, skip it, continue with the next case. (One stubborn case is information, not failure.)

## PART 4 — Fill the results table and score it (5 min)
15. For each cell compute: **%err = (DWSIM − Expected) ÷ Expected × 100.** A calculator or one Excel row is fine.
16. **PASS = every %err between −5 and +5.**

| Case | Stream | Expected | DWSIM actual | %err | Pass? |
|---|---|---|---|---|---|
| V1 | NAPHTHA-S | 260.8 | | | |
| V1 | DIESEL | 320.6 | | | |
| V1 | WAX | 187.9 | | | |
| V1 | FUELGAS | 94.6 | | | |
| V2 | NAPHTHA-S | 235.4 | | | |
| V2 | DIESEL | 292.8 | | | |
| V2 | WAX | 171.7 | | | |
| V2 | FUELGAS | 101.0 | | | |
| V3 | NAPHTHA-S | 286.8 | | | |
| V3 | DIESEL | 348.4 | | | |
| V3 | WAX | 204.2 | | | |
| V3 | FUELGAS | 85.5 | | | |
| V4 | NAPHTHA-S | 237.8 | | | |
| V4 | DIESEL | 300.2 | | | |
| V4 | WAX | 176.0 | | | |
| V4 | FUELGAS | 121.4 | | | |
| V5 | NAPHTHA-S | 260.9 | | | |
| V5 | DIESEL | 320.1 | | | |
| V5 | WAX | 187.7 | | | |
| V5 | FUELGAS | 92.4 | | | |
| V6 | NAPHTHA-S | 252.5 | | | |
| V6 | DIESEL | 311.2 | | | |
| V6 | WAX | 182.5 | | | |
| V6 | FUELGAS | 95.5 | | | |

## PART 5 — What the outcome means (read after scoring)
- **All 24 cells pass** → the shortcut oracle is validated across the uncertainty set. P5 closes.
- **Only V4 fails, only on NAPHTHA-S/FUELGAS** → expected suspect (highest gas make = strongest flash-coupling extrapolation). Send me the numbers; I recalibrate K_FLASH on two points instead of one. 10-minute fix.
- **Several cases fail** → the flash model needs revisiting; send me the full table and I diagnose.
- Either way: send the filled table (photo or typed, doesn't matter). Don't overwrite `pyrolysis_base_v2.dwxmz`.
