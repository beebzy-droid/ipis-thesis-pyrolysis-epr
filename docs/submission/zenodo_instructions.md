# Zenodo DOI: why the repo isn't listed, and two ways to fix it

## Diagnosis
**Zenodo's GitHub page lists only PUBLIC repositories.** `beebzy-droid/ipis-thesis-pyrolysis-epr` is private (confirmed earlier in this project: a `git clone` without credentials was refused). A private repo will never appear in that list, no matter how many times you click Sync. Nothing is broken; the integration simply cannot see it.

Choose one path.

---

## PATH A - Make the repo public, then use the GitHub integration (recommended)
Best if you intend the repo to be the paper's public reproducibility artifact, which the manuscript's Data availability statement already promises. This is the norm for CACE computational papers and it is what reviewers will expect to be able to open.

**Before flipping it public, run this audit (5 minutes):**
1. `git log --oneline | wc -l` - skim for anything you would not want public.
2. Confirm no credentials, tokens, or `.env` files were ever committed: `git log --all --full-history -- "*.env" "*token*" "*secret*"` (should return nothing).
3. Confirm no proprietary plant data: `data/` should contain only `README.md`.
4. Confirm the other thesis never leaked in: `git log --all --oneline -- "*campaign_cap*" "*n2_onset*"` (should return nothing; the wrong-push incident was reverted on the OTHER repo, not this one, but verify).

**Then:**
1. GitHub -> repo -> Settings -> General -> scroll to Danger Zone -> **Change visibility -> Public**.
2. zenodo.org -> Log in with GitHub -> Settings -> GitHub -> click **Sync now** -> the repo now appears -> flip its toggle **ON**.
3. GitHub -> repo -> **Releases** -> "Draft a new release" -> choose tag `v1.0.0` (create it) -> title "Submission release" -> **Publish release**.
4. Zenodo auto-archives it and mints the DOI (metadata comes from `.zenodo.json` in the repo root). Copy the DOI from the Zenodo record.

**Note:** the Zenodo toggle only captures releases made AFTER the toggle is on. Toggle first, release second.

---

## PATH B - Keep the repo private, upload the archive manually
Best if you want the DOI now and the repo public later (you can do both: manual DOI now, GitHub integration for v2 after acceptance).

1. Download `zenodo_archive_v1.0.0.zip` (built for you; it is the git-tracked tree with generated artifacts excluded, exactly what a reviewer needs to reproduce).
2. zenodo.org -> **New upload** -> drag in the zip.
3. Fill the form to match `.zenodo.json`:
   - **Resource type:** Software
   - **Title:** ipis-thesis-pyrolysis-epr: Chance-constrained design of decentralized plastic-pyrolysis networks under feedstock-composition uncertainty
   - **Creators:** Busico, Bien (add ORCID and affiliation)
   - **Description:** paste the `description` field from `.zenodo.json`
   - **License:** MIT
   - **Keywords:** stochastic programming; chance constraints; surrogate modeling; plastic pyrolysis; extended producer responsibility; Philippines
   - **Version:** 1.0.0
   - **Related identifiers:** leave blank now; after acceptance add the article DOI with relation "is supplement to"
4. **Publish.** Copy the DOI.

---

## After you have the DOI (either path)
1. Open `docs/full_manuscript.md`, find the **Data availability** section, and replace the final sentence with:
   > The repository is archived at Zenodo, DOI: 10.5281/zenodo.XXXXXXX.
2. Re-export: `pandoc docs/full_manuscript.md -o 01_manuscript_FINAL.docx`
3. Do the same in the cover letter: replace "(DOI to be inserted at acceptance)" with the DOI.
4. Commit: `git add -A && git commit -m "docs: insert Zenodo DOI" && git push`

## Not in the archive (by design, and why)
- `models/*.dwxmz` - your DWSIM files live only on your machine. **Add `pyrolysis_base_v3.dwxmz` and `pyrolysis_validation.dwxmz` to `models/` before releasing.** They are the primary process artifact; a reviewer who wants to check the flowsheet needs them, and they are small.
- `docs/01_pyrolysis-epr-network.docx` (the prospectus) - optional; internal planning document, not part of the paper's reproducibility chain.
- Generated CSVs and trained surrogates - excluded on purpose; every one regenerates from `src/`, which is the claim the Data availability statement makes.
