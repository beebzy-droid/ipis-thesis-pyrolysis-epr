# ipis-thesis-pyrolysis-epr

[![DOI](https://zenodo.org/badge/1289682085.svg)](https://doi.org/10.5281/zenodo.21317616)

Uncertainty-aware surrogate optimization of decentralized mixed-plastic
pyrolysis networks for EPR-compliant liquid-fuel recovery in the Philippines (W1/A).

## Layout
- `literature/` -- annotated bibliography, gap matrix, references, gap reframe
- `src/` -- reproducible source (kinetics, surrogate, optimization)
- `models/` -- DWSIM flowsheet spec + build guide + `.dwxmz`
- `data/` -- inputs (no proprietary plant data; see data/README.md)
- `docs/` -- prospectus and manuscript
- `notebooks/`, `results/` -- analysis + generated figures

Generated artifacts (e.g. yield tables) are git-ignored and regenerate from `src/`.
