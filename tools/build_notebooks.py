"""Build notebooks 02–05; 01 is a standalone executed analysis with embedded code."""
from pathlib import Path
import nbformat as n

ROOT=Path(__file__).resolve().parents[1]
bootstrap='''%matplotlib inline
from pathlib import Path
import sys
import matplotlib.pyplot as plt
from IPython.display import display
ROOT = Path.cwd() if (Path.cwd() / 'config').is_dir() else Path.cwd().parent
assert (ROOT / 'config/assignment.json').is_file(), 'Open from the repository or notebooks directory.'
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from dv_assignment.data import config
'''


def write(stem,cells,pending=False):
    nb=n.v4.new_notebook(cells=cells,metadata={
        'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},
        'language_info':{'name':'python'},
        'assignment':{'course_data_execution':'pending' if pending else 'requires_execution'}})
    n.validate(nb); n.write(nb,ROOT/'notebooks'/f'{stem}.ipynb')


def covid(county,number):
    is_pasco=county=='Pasco'
    form='two lines' if is_pasco else 'moving-average columns and a daily-cases line'
    stem=f'{number}_{county.lower()}_covid'
    write(stem,[
        n.v4.new_markdown_cell(f'''# {number} · {county} COVID cases

**Requirement {2 if is_pasco else 3} · 5 points · {form}**

The daily series reveals short-term variation; the moving average makes the longer trend easier to follow. {'Two lines show how smoothing changes the signal.' if is_pasco else 'Columns show the supplied moving average, with daily cases overlaid as the required line.'} Both series use one cases-per-day axis; a second axis would give identical units different visual scales.

**Source:** `data/Combined.xlsx`, `{county}` worksheet. Dates are event dates, not download dates. These are raw case counts, not population-adjusted comparisons.

**Source-specific detail:** the supplied average reproduces an **8-observation trailing mean**, current observation included, with partial initial windows. Hillsborough matches exactly; Pasco differs by no more than 0.05 because of displayed one-decimal rounding. It is not relabeled as a 7-day average.

Daily dates absent from the sheet are reintroduced as **missing**, not zero. The original supplied average stays unchanged; the displayed lines have gaps for unlisted dates.'''),
        n.v4.new_code_cell(bootstrap+'''from dv_assignment.data import course_county, audit_daily_series, daily_preview
from dv_assignment import charts
'''),
        n.v4.new_markdown_cell('''## Load and validate the actual course worksheet

The loader checks dates, duplicate keys, numeric values, and every supplied moving average against its observed source formula. The code is in `dv_assignment/data.py`; the plotting code is in `dv_assignment/charts.py`.'''),
        n.v4.new_code_cell(f'''data = course_county(config()['covid'], '{county}')
print({{key: value for key, value in data.attrs.items() if key != 'unlisted_dates'}})
display(daily_preview(data))
print(f"Observed days: {{data.daily_cases.notna().sum():,}}")
print(f"Cases across listed dates: {{data.daily_cases.sum():,.0f}}")
print(f"Unlisted calendar dates: {{data.attrs['missing_calendar_days']}}")'''),
        n.v4.new_markdown_cell('''## Missing-value check and treatment

`isna()` checks NaN, None and pandas NA. The audit separates null values on original observed dates from the additional calendar dates inserted for display. There are no missing case counts or supplied means on the original worksheet rows. The table preview labels inserted gaps **Not listed**; the underlying values remain missing. We do not replace them with zero, interpolate counts, or carry a previous mean into an unlisted date.'''),
        n.v4.new_code_cell('''null_audit, unlisted_dates = audit_daily_series(data)
display(null_audit)
display(unlisted_dates)
assert null_audit.nulls_on_observed_dates.eq(0).all()
(ROOT / 'reports').mkdir(exist_ok=True)
null_audit.to_csv(ROOT / 'reports' / f"{data.attrs['county'].lower()}_null_audit.csv", index=False)'''),
        n.v4.new_markdown_cell('''## Required visualization

Blue and orange separate the series with strong contrast. The source note defines the moving average, the y-axis starts at zero, and date ticks remain readable across the complete period.'''),
        n.v4.new_code_cell(f'''fig = charts.{'pasco' if is_pasco else 'hillsborough'}(data)
charts.export(fig, ROOT / 'figures', '{stem}')
plt.show()'''),
        n.v4.new_markdown_cell('''## Read the result

Use the table below to verify the highest recorded day and peak supplied average. The moving average smooths recorded variation; it is not a forecast. Missing dates are not evidence of zero cases. Changes in testing and case recording can affect the daily series.'''),
        n.v4.new_code_cell('''print(f"Highest recorded daily count: {data.daily_cases.max():,.0f} on {data.daily_cases.idxmax():%d %b %Y}")
print(f"Highest supplied moving average: {data.moving_average.max():,.1f} on {data.moving_average.idxmax():%d %b %Y}")''')
    ])


covid('Pasco','02'); covid('Hillsborough','03')
write('04_european_car_sales',[
 n.v4.new_markdown_cell('''# 04 · European car sales and costs

**Requirement 4 · 10 points · grouped horizontal bar chart**

Compare transaction totals for **United Kingdom, Germany, and France**. Horizontal bars accommodate the long country name, start at zero, and allow direct comparisons. A pie chart would obscure differences between sales and costs.

**Source:** `data/Simplified Car Sales Data.xlsx`, `CarSalesData` worksheet, 457 transactions overall; 259 belong to the three required countries.

**Definitions:** sales = `sum(SalePrice)`; total costs = `sum(CostPrice + LaborCost)`. Both cost components are provided and itemized below. If the module defines “costs” as purchase cost only, that would be a different measure: the notebook exposes it as `purchase_cost` rather than silently mixing definitions. The student confirmed **USD**; amounts are not converted. The source workbook itself has no currency label.'''),
 n.v4.new_code_cell(bootstrap+'''from dv_assignment.data import course_sales
from dv_assignment import charts
'''),
 n.v4.new_markdown_cell('''## Aggregate transactions, not unit prices

There is no quantity field. Each row supplies sale, purchase, and labor amounts. Filter the assigned countries, validate nonmissing numeric values, and sum the transaction amounts. The three countries must all be present.'''),
 n.v4.new_code_cell('''totals = course_sales(config()['sales'])
display(totals.style.format('{:,.0f}'))
assert (totals.total_costs == totals.purchase_cost + totals.labor_cost).all()
print(f"Selected transactions: {totals.transactions.sum():,}")'''),
 n.v4.new_markdown_cell('''## Required horizontal bar chart

Two adjacent horizontal bars per country show sales and total costs on one monetary axis. The ordering follows sales. Direct labels give totals in millions, and the table above retains exact amounts.'''),
 n.v4.new_code_cell('''fig = charts.car_sales(totals)
charts.export(fig, ROOT / 'figures', '04_european_car_sales')
plt.show()'''),
 n.v4.new_markdown_cell('''## Interpretation

The United Kingdom has the highest total sales and the most transactions in this subset. Germany's total costs exceed sales; that is retained rather than corrected away. This chart measures transaction volume and amounts, not profit margin per vehicle. Different transaction counts and vehicle mixes affect the comparison.''')
])
write('05_reconstruct_covid_and_panels',[
 n.v4.new_markdown_cell('''# 05 · Reconstruct COVID data and compare two counties

**Requirements 5 and 6 · 5 + 15 points**

**Sources verified:** both full-size yearly files were extracted from the original `data/2 yearly.zip`. No records were sampled. SHA-256 and byte-size checks reproduce the original inputs. Run `python tools/prepare_data.py` before this notebook in a fresh checkout.

This notebook combines source reconstruction and the required `matplotlib.pyplot` **2 × 2** visualization to satisfy the instruction to submit five notebooks for the six Python requirements.

Inspection confirmed **1,341,647 case records for 2020** and **938,226 for 2021**. `EventDate` falls entirely in the corresponding year, so the partitions do not overlap. Each yearly source has a unique record ID; 2020 calls it `ObjectId2`, and 2021 calls it `ObjectId`. The 2020 `OBJECTID` column is entirely empty and is removed only after checking that fact. All remaining source columns are retained in the combined case-record CSV, with source-file and source-year provenance. String missing-value representations are normalized by pandas; the original byte-for-byte files remain in the archive.'''),
 n.v4.new_code_cell(bootstrap+'''from dv_assignment.data import rebuild_case_records, rebuilt_county, compare_sources, audit_daily_series, daily_preview
from dv_assignment import charts
import json
'''),
 n.v4.new_markdown_cell('''## Rebuild from both originals

The source is Florida case-level data. Use `County`, `EventDate` (`%m/%d/%Y`), and each source-local record ID. `ChartDate` and `Case1` are different fields and are not substituted. The reconstruction checks every source ID, year, and county/date key. The `Unknown` county category is retained in the source and excluded only when selecting a specific named county.

The adapter counts records by county and event day and verifies that all **2,279,873** input records reconcile to the resulting counts. There are **three missing `Case_` flags in 2021**; these rows are retained as supplied in the case-only file and reported in the audit. Every nonmissing case flag is `Yes`. No negative counts, missing event dates, or missing county identifiers are silently removed.'''),
 n.v4.new_code_cell('''settings = config()['raw_covid']
source = rebuild_case_records(settings)
display(source.head())
print(source.attrs['source_audit'])
assert source.daily_cases.sum() == sum(x['case_records'] for x in source.attrs['source_audit'])
output = ROOT / 'data' / 'derived'
output.mkdir(exist_ok=True, parents=True)
source.to_csv(output / 'reconstructed_covid.csv', index=False, date_format='%Y-%m-%d')
(output / 'reconstruction_audit.json').write_text(json.dumps(source.attrs['source_audit'], indent=2))'''),
 n.v4.new_markdown_cell('''## Extract Broward and Palm Beach from that reconstructed source

The average policy is explicit in the configuration: an 8-observation trailing average, including the current observation and partial initial windows, following the supplied consolidated workbook. Confirm any additional module-specific instructions. Calculate over the observed rows, then introduce missing calendar dates as gaps for display. Do not replace missing dates with zero without evidence that the course intends that interpretation.'''),
 n.v4.new_code_cell('''broward = rebuilt_county(source, 'Broward', settings['moving_average'])
palm_beach = rebuilt_county(source, 'Palm Beach', settings['moving_average'])
for county in [broward, palm_beach]:
    print({key: value for key, value in county.attrs.items() if key != 'unlisted_dates'})
    display(daily_preview(county, rows=10))'''),
 n.v4.new_markdown_cell('''## Missing-value check and treatment

Both original case files have complete county, event-date and nonempty record-ID fields. Grouped county/day counts also have no missing counts. The NaNs in the displayed series come from inserting dates with no matching case records. This is separate from the three missing `Case_` flags retained in the input.

The audit below identifies every inserted date and verifies that no observed daily count or calculated mean is null. Previews say **Not listed** rather than displaying NaN. For this submission, preserve gaps and the documented observation-window mean. If the module explicitly guarantees complete case coverage and defines absent dates as zero, an alternative zero-filled daily series must recompute its mean on that calendar and disclose the changed definition; do not use a blanket `fillna(0)` on both columns.'''),
 n.v4.new_code_cell('''import pandas as pd
null_summaries = []
gap_lists = []
for county in [broward, palm_beach]:
    summary, gaps = audit_daily_series(county)
    null_summaries.append(summary)
    gap_lists.append(gaps)
null_audit = pd.concat(null_summaries, ignore_index=True)
unlisted_dates = pd.concat(gap_lists, ignore_index=True)
display(null_audit)
display(unlisted_dates)
assert null_audit.nulls_on_observed_dates.eq(0).all()
(ROOT / 'reports').mkdir(exist_ok=True)
null_audit.to_csv(ROOT / 'reports' / 'reconstructed_counties_null_audit.csv', index=False)
unlisted_dates.to_csv(ROOT / 'reports' / 'reconstructed_counties_unlisted_dates.csv', index=False)'''),
 n.v4.new_markdown_cell('''## Required 2 × 2 figure

| | Left column | Right column |
|---|---|---|
| First row | Broward daily cases | Broward moving average |
| Second row | Palm Beach daily cases | Palm Beach moving average |

The plotting function uses `plt.subplots(2, 2, sharex=True, sharey=True)`. Common date and case scales make the panels comparable. Daily cases use blue; moving averages use orange. Counts are not adjusted for county population.'''),
 n.v4.new_code_cell('''fig = charts.county_panels(broward, palm_beach)
assert len(fig.axes) == 4
charts.export(fig, ROOT / 'figures', '05_broward_palm_beach')
plt.show()'''),
 n.v4.new_markdown_cell('''## Reconciliation with Combined.xlsx

The cell below compares the independently rebuilt counts with the supplied workbook over each workbook's listed dates. These sources **differ**: 278 of Pasco's 367 listed dates and 350 of Hillsborough's 370 listed dates do not match. Neither file records enough provenance to establish the reason. Requirements 2–3 therefore retain the supplied workbook, while requirements 5–6 use the original case records. No adjustments are made to force agreement.'''),
 n.v4.new_code_cell("comparison = compare_sources(source, config()['covid'])\ncomparison.to_csv(ROOT / 'reports' / 'source_crosscheck.csv', index=False)\ndisplay(comparison.groupby('county').agg(listed_dates=('date','size'), differing_dates=('matches',lambda x: (~x).sum()), total_difference=('difference','sum')))")
])
print('Built notebooks 02–05 using the inspected course inputs.')
