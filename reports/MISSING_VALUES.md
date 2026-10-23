# Missing-value audit and treatment

The original `Combined.xlsx` worksheets have no null dates, daily counts, or supplied averages. The reconstructed county/day source also has no null counts, and both full original case files have complete County, EventDate, and the nonempty source-local ID fields.

The county loaders add calendar dates absent from their selected sources. That `reindex` operation creates the displayed NaNs; it does not discard case records.

| Notebook | County | Null daily counts on observed dates | Added dates with no listed value | Display nulls in each plotted series |
|---|---|---:|---:|---:|
| 02 | Pasco | 0 | 4 | 4 |
| 03 | Hillsborough | 0 | 1 | 1 |
| 05 | Broward | 0 | 24 | 24 |
| 05 | Palm Beach | 0 | 37 | 37 |

Pasco's unlisted dates are March 3–6, 2020; Hillsborough's is March 2, 2020. Broward and Palm Beach's unlisted dates are in January–February 2020. The complete list is in `unlisted_calendar_dates.csv`.

## Chosen treatment

- Keep the full original data unchanged. No records are sampled, dropped, or rewritten in the original archive.
- Preserve missing calendar values and plot gaps. The worksheet does not establish that each unlisted date represents a zero count. The raw-record aggregate establishes that no matching case records exist on its unlisted dates; treating that as zero reported cases on a complete calendar would be an explicit additional reporting-coverage convention.
- Label missing preview cells **Not listed** using pandas display formatting. The underlying columns remain numeric, with NaNs intact. This is a presentation improvement, not imputation.
- Show separate counts for nulls on observed dates and nulls introduced by added calendar dates. Fail the notebook assertion if an observed count or average is unexpectedly null.
- Preserve the supplied moving averages in notebooks 02–03 and the documented eight-observation method in notebook 05.
- Do not interpolate integer cases, forward-fill counts/means, or call `fillna(0)` on the whole table. Those operations can invent values and change the calculation's meaning.

If the module explicitly specifies a complete daily case calendar, construct a separately labeled calendar series with zero counts only for absent dates, then recompute its average using the prescribed calendar-day window. This would be a different average from the supplied observation-window series; report the assumption and keep the originals available.

## Actual missing fields in the raw case exports

These are distinct from the date gaps. `source_null_audit.csv` reports every original column's pandas missing-value count, including source `NA` tokens. Several health/status fields are not populated; they are not used to count cases by county/day. The 2020 `OBJECTID` field is entirely empty, while `ObjectId2` is complete and unique. Three 2021 `Case_` flags are missing; these supplied case-only records are retained and reported in the reconstruction audit. These source fields must not be replaced with zero indiscriminately.

## Reproduce the check

From the project root, after restoring the full CSVs and running notebook 05:

```bash
python tools/audit_missing_values.py
```

Reports: `source_null_audit.csv` (all source fields), `missing_value_summary.csv` (the four plotted county series), and `unlisted_calendar_dates.csv` (every introduced gap). Notebooks 02, 03, and 05 contain the same series audit and readable previews.
