# Changelog

## [1.0.3] — 2026-07-12
Added the DWSIM flowsheet artifacts (`pyrolysis_base_v3.dwxmz`, `pyrolysis_validation.dwxmz`), which a `*.dwxmz` rule in the original `.gitignore` had been silently excluding since project start.

## [1.0.2] — 2026-07-12
Manuscript cites the Zenodo **concept DOI** only (no version pin), making the data-availability statement stable across all future re-archiving.

## [1.0.1] — 2026-07-12
Zenodo metadata driven by a schema-validated `CITATION.cff`; removed `.zenodo.json`, whose invalid `related_identifiers` placeholder had failed a release.

## [1.0.0] — 2026-07-12
First archived release at submission.

### Project lifecycle (P0–P9)
- **P1** Literature review, gap matrix, gap reframing against Wang & Maravelias (2024) and Crîstiu et al. (2024)
- **P2** DWSIM pyrolysis + fractionation flowsheet; yield model verified to 4.6 pp
- **P3** Feedstock-composition uncertainty set (Dirichlet + robust box) and LHS design
- **P4** GP/LightGBM surrogates; two-stage stochastic and chance-constrained superstructure
- **P5** SAA replication study; deterministic benchmark; 6-point DWSIM validation with LOOCV
- **P6** Techno-economic analysis, Sobol sensitivity, streamlined LCA
- **P7** Manuscript and six publication figures
- **P8** Adversarial review pass; DAO 2023-02 primary-source integration
- **P9** Zenodo archive and submission to *Computers & Chemical Engineering* (`CACE-D-26-01165`)
