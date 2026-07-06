# DWSIM Base Flowsheet — Step-by-Step Build Guide (P2)
**Repo:** `ipis-thesis-pyrolysis-epr` · **For:** first DWSIM build of the pyrolysis + fractionation flowsheet.
**How to read this:** do the steps in order. Each step is one action. Don't skip. Where a number is **PROVISIONAL**, it's a placeholder so you get a working flowsheet *now* — you replace it when Genuino's oil boiling curve arrives (Item 1). The reactor yields are already verified (V3); only the oil *cut split* is provisional.

**What you are building:**
```
FEED (pyrolysis product, from the Python yield table)
  → COOLER (condense the oil)
    → SEPARATOR (gas off the top, liquid oil out the bottom)
      → COLUMN 1 (naphtha off the top, heavier oil to bottom)
        → COLUMN 2 (diesel off the top, wax at the bottom)
```
Char (solid) is handled outside DWSIM in the mass balance — DWSIM does the gas + liquid part. You end with 4 product streams: **GAS, NAPHTHA, DIESEL (middle), WAX**.

---

## PART 0 — Get DWSIM open (5 min)

1. Download DWSIM from **dwsim.org** (the free "Classic" or "Cross-Platform" build for your OS). Install it. Open it.
2. Click **File → New → Steady-State Simulation**. A blank flowsheet canvas appears.
3. Look at the **bottom-right panel** ("Simulation Settings"). Find **Units System**. Confirm it says **SI**. If not, pick SI. (Done — SI is the default.)

---

## PART 1 — Make the 3 oil "pseudocompounds" (15 min)

Real pyrolysis oil is thousands of molecules. We represent it as **3 fake compounds** (pseudocomponents), one per boiling cut. You create each with the Compound Creator.

4. Open **Tools → Compound Creator Utility** (a wizard opens).
5. Create the **first** pseudocompound. Enter:
   - **Name:** `NAPHTHA`
   - **Normal Boiling Point (NBP):** `100` °C  *(PROVISIONAL)*
   - **Molecular Weight:** `100` g/mol  *(PROVISIONAL)*
   - **Specific Gravity / liquid density:** `0.72` (≈720 kg/m³)  *(PROVISIONAL)*
   - Let DWSIM **estimate the rest** (it uses Joback/Lee-Kesler/Riedel to fill critical properties automatically). Click through to finish, and **Save** the compound.
6. Repeat step 5 for the **second**:
   - **Name:** `DIESEL` · **NBP:** `260` °C · **MW:** `200` g/mol · **SG:** `0.81`  *(all PROVISIONAL)*
7. Repeat step 5 for the **third**:
   - **Name:** `WAX` · **NBP:** `420` °C · **MW:** `380` g/mol · **SG:** `0.86`  *(all PROVISIONAL)*
8. Close the Compound Creator. Your 3 pseudocompounds are now saved to your user database.

> Why these numbers: naphtha ≈ C5–C12, diesel ≈ C13–C20, wax ≈ C21+ — the NBP/MW/SG are literature-typical midpoints for polyolefin pyrolysis oil. **Flag:** replace with real values from Genuino's SI GC-SimDist when you have it. The *structure* of the flowsheet does not change when you update them — only the numbers.

---

## PART 2 — Add all compounds to the simulation (5 min)

9. Open the **Compounds** panel (left side, or **Simulation Settings → Compounds**). You'll search a list of 1500+ compounds and tick the ones you want.
10. Tick these **gas** compounds (type each name in the search box, tick it):
    - `Methane`
    - `Ethylene` (ethene)
    - `Propylene` (propene)
    - `Propane`
11. Tick your 3 pseudocompounds: `NAPHTHA`, `DIESEL`, `WAX` (they appear in the list because you saved them).
12. That's **7 compounds** total. (We skip char here — it's a solid, handled in the mass balance outside DWSIM.)

---

## PART 3 — Pick the thermodynamics (2 min)

13. Open the **Property Packages** panel (Simulation Settings → Property Packages).
14. From the list, add **Peng-Robinson (PR)**. Click Add. Done.

> Why PR: the whole mixture is non-polar hydrocarbons over a wide boiling range — PR is the refinery-standard equation of state for exactly this. (NRTL/UNIQUAC are for water/alcohols — wrong here.)

---

## PART 4 — Drop the blocks on the canvas (10 min)

You add blocks with **Object → Add New Simulation Object**, or drag from the **Object Palette** on the side. Add these and place them left-to-right:

15. **Material Stream** → name it `FEED`. (This is your reactor product going in.)
16. **Cooler** → name it `E-101`. (Condenses the oil.)
17. **Material Stream** → name it `COOLED`. (Between cooler and separator.)
18. **Vessel / Gas-Liquid Separator** (a flash drum) → name it `V-101`.
19. **Material Stream** → name it `GAS` (top product of the separator).
20. **Material Stream** → name it `OIL` (bottom liquid of the separator).
21. **Shortcut Column** (Distillation - Shortcut) → name it `C-101`.
22. **Material Stream** → `NAPHTHA` (top of C-101).
23. **Material Stream** → `HEAVY` (bottom of C-101 → feed to C-102).
24. **Shortcut Column** → name it `C-102`.
25. **Material Stream** → `DIESEL` (top of C-102).
26. **Material Stream** → `WAX` (bottom of C-102).
27. Add **2 Energy Streams** (for the cooler duty and column reboiler/condenser if asked) — name them `Q-cool`, `Q-col`. (DWSIM will prompt for energy streams where a block needs one.)

---

## PART 5 — Wire the blocks together (10 min)

Connect by **clicking the little arrow (connector) on the edge of a block and dragging to the next block's inlet**. Or right-click a block → **Edit Connections**.

28. `FEED` → into `E-101` (inlet).
29. `E-101` outlet → `COOLED` → into `V-101` (feed inlet).
30. `V-101` **vapor outlet** → `GAS`.
31. `V-101` **liquid outlet** → `OIL` → into `C-101` (feed inlet).
32. `C-101` **distillate (top)** → `NAPHTHA`.
33. `C-101` **bottoms** → `HEAVY` → into `C-102` (feed inlet).
34. `C-102` **distillate (top)** → `DIESEL`.
35. `C-102` **bottoms** → `WAX`.
36. Attach `Q-cool` to `E-101`'s energy port. (Columns create their own condenser/reboiler duties.)

Your flowsheet should now look like the chain in "What you are building" above. Blocks will show **red/error** until you give them numbers — that's normal.

---

## PART 6 — Type in the FEED numbers (10 min)

This is the reactor product. Numbers below are for **1000 kg/h of PH mixed plastic** = {HDPE 45%, PP 30%, PS 10%, multilayer 15%}, pyrolysed at **500 °C** — taken from the verified `yield_table.csv` (GAS 4.6 / OIL_WAX 88.2 / SOLID 6.6 wt%). Char (66 kg/h) is removed before DWSIM. The DWSIM feed is the **gas + oil** = 928 kg/h.

37. Double-click `FEED` → **Edit Properties**. Set:
    - **Temperature:** `500` °C (773 K)
    - **Pressure:** `101325` Pa (1 atm)
    - **Mass Flow:** `928` kg/h
    - **Composition basis:** Mass Flows (or Mass Fractions)
38. Enter the component **mass flows** (kg/h) — this splits GAS across light gases and OIL_WAX across the 3 cuts using the **PROVISIONAL** oil split (naphtha 35% / diesel 40% / wax 25% of the oil):

    | Compound | Mass flow (kg/h) | Note |
    |---|---|---|
    | Methane | 9 | GAS lump (PROVISIONAL split) |
    | Ethylene | 14 | GAS lump |
    | Propylene | 14 | GAS lump |
    | Propane | 9 | GAS lump |
    | NAPHTHA | 309 | 35% of 882 oil *(PROVISIONAL)* |
    | DIESEL | 353 | 40% of 882 oil *(PROVISIONAL)* |
    | WAX | 220 | 25% of 882 oil *(PROVISIONAL)* |
    | **Total** | **928** | |

39. Close the FEED editor. The FEED block should turn **green** (solved).

---

## PART 7 — Configure the units (15 min)

**Cooler E-101:**
40. Double-click `E-101`. Set **Calculation Mode = Outlet Temperature**. Set **Outlet Temperature = 40 °C** (313 K). Set **Pressure Drop = 0**. (This condenses the oil; gas stays vapor.)

**Separator V-101:**
41. Double-click `V-101`. It's a simple flash — usually no input needed beyond the feed. Confirm **Flash = PT** (pressure-temperature). It will split vapor (gas) from liquid (oil) at 40 °C, 1 atm.

**Column C-101 (naphtha / heavier):**
42. Double-click `C-101` (shortcut column). Set:
    - **Light Key = NAPHTHA**, **Heavy Key = DIESEL**
    - **Light Key recovery in distillate = 0.98**, **Heavy Key recovery in distillate = 0.02**
    - **Reflux ratio = 2** (start here)
    - **Condenser pressure = 101325 Pa**, **Reboiler pressure = 101325 Pa** (or 110000 Pa for a small drop)
43. Column C-101 will compute min stages/reflux (Fenske-Underwood-Gilliland) and split NAPHTHA overhead, (DIESEL+WAX) to bottoms.

**Column C-102 (diesel / wax):**
44. Double-click `C-102`. Set:
    - **Light Key = DIESEL**, **Heavy Key = WAX**
    - **LK recovery in distillate = 0.98**, **HK recovery in distillate = 0.02**
    - **Reflux ratio = 2**
    - **Condenser/Reboiler pressure = 101325 Pa**

---

## PART 8 — Run it (2 min)

45. Press **F5** (or the green **Solve/Play** button). DWSIM solves module-by-module.
46. Blocks turn **green** = solved. If a column shows an error, see Part 10.

---

## PART 9 — Check it's right (verification, 10 min)

**V1 — Mass balance (must close):**
47. Add up the 4 product mass flows: `GAS + NAPHTHA + DIESEL + WAX`. Double-click each stream to read its mass flow.
48. They must sum to **928 kg/h** (the feed), within **±0.1%** (≤ ~1 kg/h). If yes → mass balance closes. ✅
    *(Char 66 kg/h + unconverted 6 kg/h are the separate offline streams; full plant balance = 928 + 66 + 6 = 1000 kg/h in.)*

**V5 — Cuts make sense:**
49. Read each product's temperature and composition. Sanity checks:
    - `GAS` is mostly the light compounds, leaves cold at the top of V-101.
    - `NAPHTHA` overhead of C-101, mostly the NAPHTHA pseudocompound.
    - `DIESEL` overhead of C-102; `WAX` at the bottom, hottest.
    - No negative flows; cut temperatures increase naphtha < diesel < wax.

**Save your work:** File → Save As → `models/pyrolysis_base.dwxmz` in the repo.

---

## PART 10 — If a column won't converge (troubleshooting)

- **Shortcut column errors:** check the light/heavy keys are adjacent in volatility (NAPHTHA→DIESEL, DIESEL→WAX — correct). Make sure both keys actually exist in that column's feed.
- **Reflux too low:** raise reflux ratio from 2 → 3.
- **Later, for a rigorous column:** DWSIM has a **"Use Shortcut Results as Initial Estimates"** option — always tick it; it feeds the shortcut answer as the starting guess and dramatically improves convergence. Set composition tolerance **1e-4 to 1e-6**.
- **Everything red on open:** you probably missed a connection (Part 5) or a feed number (Part 6). Green propagates left-to-right as each block gets what it needs.

---

## What is PROVISIONAL vs VERIFIED

| Item | Status | When it's fixed |
|---|---|---|
| Reactor yields (GAS/OIL_WAX/SOLID = 4.6/88.2/6.6) | **VERIFIED** (Genuino, V3 = 4.6 pp) | done |
| Oil cut split (35/40/25 naphtha/diesel/wax) | **PROVISIONAL** | replace with Genuino SI GC-SimDist (Item 1) |
| Pseudocompound NBP/MW/SG | **PROVISIONAL** | same |
| Property package (PR) | VERIFIED choice | — |
| Flowsheet structure | final | — |

When the boiling curve arrives, you change **only**: (a) the 3 pseudocompound NBP/MW/SG (Part 1), and (b) the naphtha/diesel/wax mass flows in FEED (Part 6). Nothing else moves.

---

## Later (not now): automate the reactor with a Python Script UO

For the network-scale study you won't retype FEED for every case. DWSIM's **Python Script unit operation** can read a feed mass flow, call the yield table, and set the product stream automatically (snippet in `src/lumped_kinetics.py`, `DWSIM_SCRIPT_UO`). Do this **after** the manual flowsheet converges and is verified — walk before running.
