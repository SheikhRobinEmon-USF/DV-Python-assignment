# Requirement 7: finish the Tableau workbook

The Python function and a real TabPy `/evaluate` request have been tested. This is not yet evidence of a Tableau Desktop connection: your Module 3 `.twbx` and its source fields are still required. No substitute or empty workbook is included.

## A. Provide the Module 3 workbook

1. Open **Tableau Desktop** on your computer.
2. Open the workbook you submitted for Module 3.
3. Choose **File → Save As** and select **Tableau Packaged Workbook (*.twbx)**. Keep the Module 3 sheets and data.
4. Upload that `.twbx` in this chat. If you do not have the original workbook, upload the Module 3 source dataset and instructions. The simplified car-sales file has no unit-cost or list-price fields and is insufficient for this requirement.

## B. Start the tested Python server on the same computer as Tableau

Download or clone this repository. Open a terminal **in its root folder**.

Windows:

```powershell
py -3.12 -m venv .venv-tabpy
.venv-tabpy\Scripts\python -m pip install -r tableau/requirements.txt
.venv-tabpy\Scripts\python tableau/start_local_tabpy.py
```

macOS/Linux:

```bash
python3.12 -m venv .venv-tabpy
.venv-tabpy/bin/python -m pip install -r tableau/requirements.txt
.venv-tabpy/bin/python tableau/start_local_tabpy.py
```

Leave the terminal running. It should print that TabPy is ready on `127.0.0.1:9004`. The launcher binds to this computer only. The cloud server tested during development cannot be reached through your computer's localhost address.

## C. Connect Tableau Desktop

1. Open **Help → Settings and Performance → Manage Analytics Extension Connection**. Some versions label this **Manage External Service Connection**.
2. Choose **TabPy / External API**.
3. Enter server **127.0.0.1** and port **9004**.
4. For this local launcher, leave authentication and SSL unchecked.
5. Click **Test Connection**. It must succeed. Click **OK**.

Official references: [TabPy](https://github.com/tableau/TabPy) and [Tableau SCRIPT_STR](https://help.tableau.com/current/pro/desktop/en-us/functions_functions_tablecalculation.htm#script_str).

## D. Validate the real product data

1. In the Module 3 source, identify the exact **Product**, **Unit Cost**, and **List Price** fields. Names may differ; do not substitute transaction cost or selling price without verifying their meaning.
2. Create a temporary worksheet with Product on Rows. Inspect `MIN(Unit Cost)`, `MAX(Unit Cost)`, `MIN(List Price)`, and `MAX(List Price)`.
3. For each product, each minimum must equal its corresponding maximum. Check nonmissing numeric values, with no negative amounts. Resolve inconsistent prices by choosing the correct product grain from the source; do not sum unit prices across duplicate transaction rows.

## E. Add the Python calculation

1. Choose **Analysis → Create Calculated Field**.
2. Name it **Profitability (Python)**.
3. Paste the contents of `tableau/lucrative_calculation.txt`. Replace `[Unit Cost]` and `[List Price]` only if your actual fields have different names.
4. Keep `ATTR` for the unit fields. It prevents repeated transaction rows from inflating a product's unit values and exposes inconsistent values.
5. Confirm the calculated field is valid and save it.

The script returns **Lucrative** when unit cost is at most 75% of list price, including equality, otherwise **Not lucrative**. It uses decimal arithmetic to avoid a float-rounding error at boundaries such as 0.30 versus 0.40. Invalid values raise an error rather than silently assigning a status.

## F. Build the visualization

1. Create a sheet named **Product economics**.
2. Drag **Product** to Rows.
3. Drag **Measure Names** to Rows, after Product.
4. Drag **Measure Values** to Columns.
5. In Measure Values, remove everything except **ATTR(Unit Cost)** and **ATTR(List Price)**. If Tableau added SUM, change the aggregation to **Attribute** after the uniqueness checks above.
6. Set the Marks type to **Bar**. Drag **Measure Names** to Color; use blue `#0072B2` for list price and orange `#D55E00` for unit cost. Keep the measure legend visible.
7. Format both as **USD** only if confirmed for the Module 3 source. Your USD confirmation applies to the simplified sales workbook; verify the Module 3 dataset separately if its documentation differs.
8. Edit the horizontal axis to start at **0**. Add value labels with sensible precision. Keep long product labels readable, even if that requires a taller sheet.
9. Drag **Profitability (Python)** to Tooltip. Right-click it → **Edit Table Calculation** → **Specific Dimensions**. Address **Product** and partition by **Measure Names**, so each product has one result in each measure's partition. Verify that each visible product shows the same status for its two bars.
10. Add the status visibly: create another worksheet named **Product status**, put Product on Rows and Profitability (Python) on Text, and configure its calculation to address Product. Sort both sheets identically and align them side by side in a dashboard. This keeps the bar colors dedicated to cost versus price and makes the Python result visible without hovering.
11. Add a title such as **Which products meet the 75% cost threshold?** and a caption: **Lucrative means unit cost ≤ 75% of list price. Status calculated in Python via TabPy.**
12. Check product by product that labels, alignment, and statuses are correct. Do not hide errors with a static spreadsheet status or a Tableau-only replacement for the Python calculation.

## G. Verify, package, and send it back

1. Keep TabPy running. Verify several products manually using `cost <= 0.75 × price`. Test an exact boundary if the source contains one; the Python server's test covers that boundary independently.
2. Use Tableau's **Test Connection** again and confirm the chart recalculates without script errors.
3. Save as **tableau/07_product_profitability.twbx**.
4. Close and reopen it. Confirm the data loads and the Python result still calculates while TabPy runs.
5. Upload the workbook here. Also confirm that Test Connection succeeded and the reopened workbook calculated correctly. A screenshot of the final dashboard and successful connection is useful visual evidence.
6. After this actual check, record it in `config/assignment.json`: `tableau.desktop_verified=true` and a brief `verification_notes` description. Do not mark this true before testing.

A `.twbx` contains workbook/data assets, not the running Python service. The grader must start TabPy as described above to recalculate Python results.
