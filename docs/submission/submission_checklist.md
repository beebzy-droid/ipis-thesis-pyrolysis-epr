# CACE Submission Checklist (verify against the current Guide for Authors at upload; items marked [GK] reflect Elsevier norms)
- [ ] Title page: full title, author, affiliation, email, ORCID (corresponding author ORCID required [GK])
- [ ] Abstract in system = manuscript abstract (currently 232 words; keep <250 [GK])
- [ ] Keywords (max 6): stochastic programming; chance constraints; surrogate modeling; plastic pyrolysis; extended producer responsibility; supply chain design
- [ ] Highlights file: 5 bullets, all <=85 chars (verified by script; docs/submission/highlights.md)
- [ ] Manuscript: full_manuscript_DRAFT4.docx after your final author pass (6,116 words; equations native OMML)
- [ ] Figures: upload the 6 PDFs from results/figures (vector, fonts embedded); captions list at manuscript end
- [ ] Declaration of competing interests: none (Elsevier form in system)
- [ ] CRediT author statement: Bien Busico: Conceptualization, Methodology, Software, Validation, Formal analysis, Investigation, Data curation, Writing - original draft, Writing - review & editing, Visualization. (Add advisor role lines if applicable: typically Supervision, Writing - review & editing.)
- [ ] Data availability: insert the Zenodo DOI into the manuscript's Data availability section after Step Z3 below
- [ ] Cover letter: docs/submission/cover_letter.md (date, affiliation filled)
- [ ] Suggested reviewers entered with verified institutional emails
- [ ] Funding statement: state grant or "no external funding"

## Zenodo DOI (Steps Z1-Z4, ~10 minutes, your credentials)
Z1. zenodo.org -> log in with GitHub -> Settings/GitHub -> flip the toggle ON for beebzy-droid/ipis-thesis-pyrolysis-epr.
Z2. In GitHub: Releases -> "Draft a new release" -> tag v1.0.0 -> title "Submission release" -> Publish. Zenodo auto-archives and mints the DOI (the .zenodo.json in the repo root supplies the metadata).
Z3. Copy the version DOI from the Zenodo record.
Z4. Paste it into the manuscript's Data availability paragraph and into the cover letter line "(DOI to be inserted at acceptance)" -> re-export the docx (pandoc docs/full_manuscript.md -o manuscript.docx).
