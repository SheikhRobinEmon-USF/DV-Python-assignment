# Evidence-based rubric review

This is a deliverable audit, not a guaranteed professor's grade. The supplied rubric totals **60**, not 100. Requirements 1–6 have been implemented and executed; requirement 7 remains incomplete until the Module 3 workbook is supplied and tested in Tableau Desktop.

| Requirement | Listed points | Evidence | Status |
|---|---:|---|---|
| 1 | 5 | Notebook 01; all 52 source observations; yellow five-point star scatter; percentage axes; Matplotlib references | Complete |
| 2 | 5 | Notebook 02; Pasco daily counts and original moving average shown as two lines | Complete |
| 3 | 5 | Notebook 03; Hillsborough moving-average columns with daily-case line; suitable distinct colors and common units | Complete |
| 4 | 10 | Notebook 04; six horizontal bars; required countries; transaction totals; purchase + labor cost definition; USD confirmation | Complete |
| 5 | 5 | Notebook 05; both complete source files; full combined case CSV and county/day source; 2,279,873 records reconciled; provenance and audits | Complete |
| 6 | 15 | Notebook 05; `plt.subplots(2,2)`; Broward row 1, Palm Beach row 2; daily and mean columns; common scales | Complete |
| 7 | 15 | Python comparison and local TabPy server tested; exact inclusive 75% boundary and decimal handling | Python portion tested; original workbook and Tableau Desktop visualization/connection pending |

**Submission status:** 45 of the 60 listed points have complete source-backed deliverables; no grade is assigned to the outstanding Tableau requirement. It would be misleading to label the entire assignment 100/100 now.

All five notebooks executed from top to bottom with the actual inputs and saved figure outputs. Nineteen behavior checks passed, with no failed or skipped tests. Figure exports were visually inspected. The Python ZIP was extracted into a different directory, both full original CSVs were restored with verified hashes, and all five notebooks passed there as well. `reports/validation.json` records source hashes and counts; `reports/tabpy_smoke.json` records the actual server response on boundary-test values.

## Source decisions documented for grading

- Use the specified chart types, including the unusual moving-average-column/daily-line combination in requirement 3.
- The workbook's supplied averages match an eight-observation trailing mean; no unsupported seven-day label is used.
- Absent calendar dates remain gaps, not invented zeros.
- Cost totals include both purchase and labor amounts, with purchase-only costs itemized separately. This definition is explicit because the prompt does not say whether to include labor.
- USD is based on student confirmation, not inferred from the Excel formatting.
- The raw files and consolidated workbook differ on historical daily counts. Each required source is used as requested; mismatches are reported rather than silently corrected. Their cause is unknown.
- All source records remain, including Unknown county and three missing case flags. Those cases are excluded from a named-county chart only by the explicit county selection.
- Original case files are retained in lossless ZIP form because each exceeds GitHub's single-file size limit. Extraction restores original bytes and checksums.

## Final action needed

Provide the Module 3 `.twbx`, follow `tableau/TABLEAU_STEPS.md` on a computer with Tableau Desktop, verify the Python connection and reopened chart, and save the final workbook. Only then run the final-submission packager and upload the ZIP to the course assignment box.

## Missing-value update

Notebooks 02, 03, and 05 now show a source-versus-inserted-date null audit and label preview gaps **Not listed**. All five notebooks were re-executed successfully after this change. No source observations or moving averages were imputed. See `reports/MISSING_VALUES.md`.
