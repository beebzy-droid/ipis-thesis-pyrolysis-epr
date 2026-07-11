# DWSIM Multi-Point Validation Protocol (P5, user-side, ~45 min)
**Purpose:** the flowsheet-shortcut oracle is calibrated to ONE DWSIM point. This validates it at 6 compositions spanning the P3 uncertainty set. **Acceptance: every product mass flow within ±5% of the expected value.**

**Procedure (per case, ~7 min):** open `pyrolysis_base_v2.dwxmz` → edit ONLY the FEED stream component mass flows to the row below (T=500 °C, P=1 bar unchanged) → F5 → record NAPHTHA-S, DIESEL, WAX, FUELGAS mass flows → compare to expected.

## FEED inputs (kg/h; 1000 kg/h plastic basis, char/unconverted already excluded)
| Case | Total | Methane | Ethylene | Propylene | Propane | NAPHTHA pc | DIESEL pc | WAX pc |
|---|---|---|---|---|---|---|---|---|
| V1 central | 864.0 | 14.6 | 22.6 | 22.6 | 14.6 | 281.1 | 320.6 | 187.9 |
| V2 hi-multilayer | 800.9 | 15.6 | 24.2 | 24.2 | 15.6 | 256.8 | 292.8 | 171.7 |
| V3 hi-polyolefin | 924.9 | 13.1 | 20.3 | 20.3 | 13.1 | 305.5 | 348.4 | 204.2 |
| V4 hi-PET | 835.5 | 18.8 | 29.2 | 29.2 | 18.8 | 263.3 | 300.2 | 176.0 |
| V5 hi-PS | 861.1 | 14.2 | 22.1 | 22.1 | 14.2 | 280.7 | 320.1 | 187.7 |
| V6 hi-clogged | 841.7 | 14.7 | 22.8 | 22.8 | 14.7 | 272.9 | 311.2 | 182.5 |

## Expected outputs (shortcut oracle; record DWSIM actuals beside, compute %err)
| Case | NAPHTHA-S | DIESEL | WAX | FUELGAS | DWSIM actuals → | %err ≤5%? |
|---|---|---|---|---|---|---|
| V1 | 260.8 | 320.6 | 187.9 | 94.6 | ___ / ___ / ___ / ___ | |
| V2 | 235.4 | 292.8 | 171.7 | 101.0 | ___ | |
| V3 | 286.8 | 348.4 | 204.2 | 85.5 | ___ | |
| V4 | 237.8 | 300.2 | 176.0 | 121.4 | ___ | |
| V5 | 260.9 | 320.1 | 187.7 | 92.4 | ___ | |
| V6 | 252.5 | 311.2 | 182.5 | 95.5 | ___ | |

Where the shortcut's largest error is expected: FUELGAS/NAPHTHA-S at V4 (highest gas make → strongest flash-coupling extrapolation from the calibration point). If only V4 fails ±5%, recalibrate K_FLASH on two points; if several fail, we revisit the flash model. Report the filled table back and I close P5.
