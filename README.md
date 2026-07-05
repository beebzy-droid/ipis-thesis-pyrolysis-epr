# ipis-thesis-pyrolysis-epr

**Uncertainty-Aware Surrogate Optimization of Decentralized Mixed-Plastic Pyrolysis Networks for EPR-Compliant Liquid Fuel Recovery in the Philippines**

Primary MS thesis (UP Diliman, Chemical Engineering). Idea **W1 / A**. Part of the IPIS research program.

## One-line contribution
A Bayesian/GP surrogate of a rigorous pyrolysis-plus-separation flowsheet, embedded in a spatial superstructure optimization solved as a stochastic/robust program over empirically-characterized Philippine feedstock composition uncertainty, subject to the RA 11898 recovery-rate constraint.

## Target journal
Computers & Chemical Engineering (fallback: Journal of Cleaner Production / ACS Sustainable Chemistry & Engineering).

## Status
- [x] P0 — Repository & environment setup
- [ ] P1 — Literature review & gap matrix
- [ ] P2 — Base pyrolysis+distillation flowsheet (verified)
- [ ] P3 — Feedstock characterization + DOE
- [ ] P4 — Surrogate + stochastic superstructure
- [ ] P5 — Validation & benchmarking
- [ ] P6 — Sensitivity/UQ + TEA/LCA
- [ ] P7 — Manuscript drafting
- [ ] P8 — Defense & submission
- [ ] P9 — Zenodo DOI preservation

## Environment
```bash
conda env create -f environment.yml
conda activate ipis-thesis-pyrolysis-epr
```
DWSIM is a separate .NET desktop application; it is driven externally and its outputs are exported to `/data` (see `models/README.md`).

## Structure
See `docs/` for the full prospectus (`docs/00_prospectus.docx`) and the session brief (`docs/SESSION_BRIEF.md`). Folder purposes are documented in each folder's README.

## Data governance
No proprietary plant, partner, or company data is committed. See `data/README.md`.

## License
MIT (code). See `LICENSE`.

## Citation
See `CITATION.cff`. A Zenodo DOI is minted at the pre-submission release (P9).
