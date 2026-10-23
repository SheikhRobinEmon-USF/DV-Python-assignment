# Run, review, and submit

The five notebooks cover Python requirements 1–6. Requirement 7 additionally needs the original Module 3 workbook and actual Tableau Desktop verification. The listed requirements total **60 points**. No numerical grade is guaranteed.

## Run the five notebooks

1. Clone/download this repository. Use **Python 3.12**.
2. Open a terminal in its root. Create a virtual environment: `python -m venv .venv`.
3. Activate it: Windows PowerShell `.venv\Scripts\Activate.ps1`; macOS/Linux `source .venv/bin/activate`.
4. Install the tested packages: `python -m pip install -r requirements.txt`.
5. Register the kernel: `python -m ipykernel install --sys-prefix --name python3 --display-name "Python 3 (assignment)"`.
6. Restore the full original case files: `python tools/prepare_data.py`. The script verifies original byte sizes and SHA-256 hashes. You need about 1 GB of free disk for the inputs and rebuilt outputs. No sampling, truncation, or lossy compression is used.
7. Start Jupyter: `python -m jupyterlab`. Open each notebook in `notebooks/`, select the assignment environment, and **Restart Kernel and Run All Cells**. Alternatively, execute all five: `python tools/run_notebooks.py`.
8. Check the figures, numeric tables, and source reconciliation. Exports are saved as PNG (300 dpi), PDF, and SVG under `figures/`.
9. Run the behavior checks: `python -m unittest discover -s tests -v`.

You can also run each script in `scripts/` individually from the repository root. Script 05 recreates the complete case-record CSV and county/day source before plotting. The scripts resolve paths relative to the repository.

## What to review

| Requirement | Notebook / deliverable | Key review |
|---|---|---|
| 1 | `01_unemployment_obesity.ipynb` | All 52 observations; yellow five-point stars; obesity x and unemployment y; percent units |
| 2 | `02_pasco_covid.ipynb` | Daily-case line and supplied moving-average line |
| 3 | `03_hillsborough_covid.ipynb` | Moving-average columns; daily-case line; one shared cases axis |
| 4 | `04_european_car_sales.ipynb` | Grouped horizontal bars for UK, France, Germany; USD; total cost explicitly includes purchase and labor |
| 5 | First part of notebook 05 | Both full original yearly files; unified IDs; 2,279,873 case records reconciled |
| 6 | Second part of notebook 05 | Exactly 2 × 2 panels; Broward in first row and Palm Beach in second row; common scales |
| 7 | Module 3 `.twbx` | Real TabPy connection and Python-returned profitability; visible unit costs, list prices, and status |

The cost definition is `sum(CostPrice + LaborCost)` because both components are provided. Purchase-only totals also appear in the table for transparency. Follow any more specific definition given in class.

The moving average supplied in `Combined.xlsx` is an **8-observation trailing mean**, not an assumed seven-day mean. It includes the current observation and partial initial windows. Missing dates remain gaps; the supplied means are preserved. The reconstructed panels use that same observation-window convention, documented in notebook 05.

The reconstructed source and `Combined.xlsx` do **not** contain identical counts. `reports/source_crosscheck.csv` records differences over the overlapping dates. Their export histories are unknown, so no reason is asserted. The assignment explicitly selects different sources for requirements 2–3 and 5–6; each is used as requested.

All original case records are retained, including three 2021 records missing the `Case_` flag in the supplied case-only file. Those records are reported in the audit rather than discarded. `Unknown` county records remain in the source but do not appear in the named-county charts. The complete rebuilt `data/derived/combined_case_records.csv` is produced locally; its source fields are retained except the verified empty 2020 `OBJECTID` column, with the two nonempty ID fields normalized to `record_id` and provenance added. Pandas normalizes missing-value string representations; the originals remain byte-for-byte intact in the supplied ZIP.

## Complete Tableau

Follow [tableau/TABLEAU_STEPS.md](tableau/TABLEAU_STEPS.md). Open the original Module 3 workbook, connect Tableau Desktop to the local Python server, add the provided calculation using the actual source fields, build and verify the view, and save the result as `tableau/07_product_profitability.twbx`.

## Create and upload the final ZIP

1. Recheck all five executed notebooks and the reopened Tableau workbook.
2. Run `python tools/package_submission.py --check`. It must report no missing final deliverables.
3. Run `python tools/package_submission.py` to produce `dist/assignment_submission.zip`. The package includes the original yearly ZIP unchanged, all five executed notebooks, the final `.twbx`, Python code, source workbooks, daily reconstruction, figures, and instructions. The 340 MB rebuilt row-level CSV is reproducible from the original ZIP and is not duplicated in the submission archive.
4. Extract the ZIP into a separate folder and run `python tools/prepare_data.py` and the notebooks there. The paths must work without this cloud workspace.
5. Upload `assignment_submission.zip` to your course assignment box yourself. GitHub publication is separate from course submission.

Until the Tableau deliverable is available and verified, `python tools/package_submission.py --python-only` produces a clearly labeled **Python deliverables ZIP**; it is not the complete assignment submission.
