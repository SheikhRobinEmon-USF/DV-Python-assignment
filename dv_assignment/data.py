"""Explicit adapters; never replace missing course inputs with fabricated data."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
KEYS = ['state', 'county', 'date']


class InputError(ValueError):
    """A missing or ambiguous course-data prerequisite."""


def config():
    return json.loads((ROOT / 'config/assignment.json').read_text())


def read_table(spec, root=ROOT):
    path = root / spec['path']
    if not path.is_file():
        raise InputError(f'Missing course input: {spec["path"]}. Upload it and update config/assignment.json.')
    if path.suffix.lower() == '.csv':
        return pd.read_csv(path)
    if path.suffix.lower() == '.xlsx':
        return pd.read_excel(path, sheet_name=spec.get('sheet', 0))
    raise InputError(f'Unsupported file type: {path.suffix}; use the original CSV or XLSX.')


def numeric(series, label, allow_missing=True):
    result = pd.to_numeric(series, errors='raise')
    if np.isinf(result.dropna().to_numpy(dtype=float)).any():
        raise InputError(f'{label} contains infinite values.')
    if not allow_missing and result.isna().any():
        raise InputError(f'{label} contains missing values.')
    return result


def parse_dates(series, date_format=None):
    if pd.api.types.is_numeric_dtype(series):
        raise InputError('Numeric dates need explicit conversion from the documented source format.')
    if not pd.api.types.is_datetime64_any_dtype(series) and date_format is None:
        # ISO dates are unambiguous. Day/month text must be configured explicitly.
        text = series.dropna().astype(str)
        if not text.str.match(r'^\d{4}-\d{2}-\d{2}(?:[ T].*)?$').all():
            raise InputError('Set date_format explicitly, e.g. %m/%d/%Y, using the course source definition.')
    parsed = pd.to_datetime(series, format=date_format, errors='raise')
    if parsed.isna().any():
        raise InputError('Missing dates are not permitted.')
    if getattr(parsed.dt, 'tz', None) is not None:
        raise InputError('Convert time zones to the course reporting day before loading.')
    if not parsed.eq(parsed.dt.normalize()).all():
        raise InputError('Expected daily observations; timestamps must be normalized deliberately.')
    return parsed


def course_county(spec, county, root=ROOT):
    """The course Combined.xlsx has one county per sheet, not one long table."""
    if county not in spec['sheets']:
        raise InputError(f'{county} is not in the configured consolidated workbook.')
    mapping = spec['sheets'][county]
    raw = read_table({'path':spec['path'], 'sheet':mapping['sheet']}, root)
    frame = raw[[mapping['date'], mapping['daily_cases'], mapping['moving_average']]].copy()
    frame.columns = ['date', 'daily_cases', 'moving_average']
    if pd.api.types.is_datetime64_any_dtype(frame['date']):
        frame['date'] = parse_dates(frame['date'])
    else:
        frame['date'] = parse_dates(frame['date'], '%B %d, %Y')
    for field in ['daily_cases', 'moving_average']:
        frame[field] = numeric(frame[field], field, allow_missing=False)
        if frame[field].lt(0).any():
            raise InputError(f'Unexpected negative {field} in supplied workbook.')
    if frame['date'].duplicated().any():
        raise InputError('Duplicate dates in county worksheet.')
    frame = frame.set_index('date').sort_index()
    expected = frame['daily_cases'].rolling(spec['average_window_observations'], min_periods=1).mean()
    tolerance = .051 if county == 'Pasco' else 1e-9
    if not np.allclose(expected, frame['moving_average'], atol=tolerance, rtol=0):
        raise InputError('Supplied moving average no longer matches the documented source calculation.')
    dates = pd.date_range(frame.index.min(),frame.index.max(),freq='D',name='date')
    missing = len(dates)-len(frame)
    frame = frame.reindex(dates)  # Visible gaps instead of inventing zero cases.
    frame.attrs.update({'county':county,'state':'Florida',
        'average_definition':f"Supplied {spec['average_window_observations']}-observation trailing average",
        'missing_calendar_days':missing,'average_supplied':True,
        'negative_daily_revisions':0,'source':Path(spec['path']).name,
        'average_validation':'All supplied values reproduced within source rounding precision'})
    return frame


def course_sales(spec, root=ROOT):
    """Transaction totals in the supplied simplified workbook; include labor explicitly."""
    raw = read_table(spec, root)
    names=spec['columns']
    required=['country','total_sales','purchase_cost','labor_cost']
    missing=[names[c] for c in required if names[c] not in raw]
    if missing:
        raise InputError(f'Missing sales fields: {missing}')
    frame=raw[[names[c] for c in required]].copy()
    frame.columns=required
    frame['country']=frame['country'].astype(str).str.strip()
    selected=['United Kingdom','Germany','France']
    frame=frame.loc[frame['country'].isin(selected)].copy()
    if set(frame['country']) != set(selected):
        raise InputError('All three assigned countries must be present.')
    for field in required[1:]:
        frame[field]=numeric(frame[field],field,False)
        if frame[field].lt(0).any():
            raise InputError('Negative transaction amounts need review.')
    if spec['cost_definition'] != 'purchase_plus_labor':
        raise InputError('Expected the documented purchase + labor cost definition.')
    frame['total_costs']=frame['purchase_cost']+frame['labor_cost']
    totals=frame.groupby('country')[['total_sales','purchase_cost','labor_cost','total_costs']].sum().sort_values('total_sales',ascending=False)
    totals['transactions']=frame.groupby('country').size()
    totals.attrs.update({'currency':spec['currency'],'source':Path(spec['path']).name,
                         'source_rows':len(frame), 'cost_definition':'Purchase cost + labor cost'})
    return totals


def rebuild_case_records(raw_spec, root=ROOT):
    """Append original records without sampling, unify the two ID names, then aggregate.

    The original sources are case-only exports. Retain the three rows with missing
    Case_ flags and audit them; all remaining flags are Yes. EventDate (not
    ChartDate or Case1) defines the observation day. Per-source IDs are unique;
    event years are disjoint and explicitly verified.
    """
    if raw_spec.get('mode') != 'append_event_records':
        raise InputError('Expected append_event_records source relationship.')
    counts=[]; audit=[]; expected_years=set()
    derived=root/'data/derived'; derived.mkdir(exist_ok=True,parents=True)
    # Publish the new file only after validation of both complete source files.
    temporary=derived/'combined_case_records.csv.inprogress'
    destination=derived/'combined_case_records.csv'
    header=True; output_columns=None
    try:
        for part in ['first','second']:
            spec=raw_spec[part]; path=root/spec['path']
            if not path.is_file():
                raise InputError(f'Missing {spec["path"]}. Run python tools/prepare_data.py.')
            if not spec.get('schema_verified'):
                raise InputError(f'Inspect {spec["path"]} and configure verified column mappings.')
            columns=spec['columns']; seen=set(); row_count=0; missing_flags=0
            expected_year=spec['expected_year']
            if expected_year in expected_years:
                raise InputError('Annual event-date partitions must have different years.')
            expected_years.add(expected_year)
            for chunk in pd.read_csv(path,chunksize=100_000,low_memory=False):
                id_name=columns['record_id']
                needed=[columns['county'],columns['date'],id_name,columns['case_flag']]
                if chunk[needed[:3]].isna().any().any():
                    raise InputError('Missing county, event date, or source-local case ID.')
                ids=chunk[id_name].astype(str)
                if ids.duplicated().any() or seen.intersection(ids):
                    raise InputError('Duplicate record IDs within a source.')
                seen.update(ids)
                dates=parse_dates(chunk[columns['date']],spec['date_format'])
                if not dates.dt.year.eq(expected_year).all():
                    raise InputError('Source years overlap or contain unexpected event years.')
                flags=chunk[columns['case_flag']]
                missing_flags+=int(flags.isna().sum())
                if not flags.dropna().eq('Yes').all():
                    raise InputError('Unexpected noncase rows in case-only file.')
                county=chunk[columns['county']].astype(str).str.strip()
                if county.eq('').any():
                    raise InputError('Blank county name.')
                daily=pd.DataFrame({'county':county,'date':dates}).groupby(['county','date']).size().rename('daily_cases')
                counts.append(daily)
                # The 2020 OBJECTID field is entirely empty. Drop only after checking.
                if 'OBJECTID' in chunk:
                    if chunk['OBJECTID'].notna().any():
                        raise InputError('Unexpected values in nominally empty 2020 OBJECTID.')
                    chunk=chunk.drop(columns='OBJECTID')
                chunk=chunk.rename(columns={id_name:'record_id'})
                chunk['source_year']=expected_year
                chunk['source_file']=path.name
                if output_columns is None:
                    output_columns=list(chunk.columns)
                elif set(chunk.columns)!=set(output_columns):
                    raise InputError('Yearly source schemas differ after explicit ID normalization.')
                chunk[output_columns].to_csv(temporary,mode='w' if header else 'a',header=header,index=False)
                header=False; row_count+=len(chunk)
            if row_count != spec['expected_rows']:
                raise InputError(f'Row count differs from inspected original: {path.name}')
            audit.append({'source':spec['path'],'case_records':row_count,'source_year':expected_year,
                          'missing_case_flags_retained':missing_flags,'unique_source_record_ids':len(seen)})
        result=pd.concat(counts).groupby(level=['county','date']).sum().reset_index()
        result['state']='Florida'
        if sum(x['case_records'] for x in audit)!=int(result['daily_cases'].sum()):
            raise AssertionError('Case totals changed during reconstruction.')
        result=result[KEYS+['daily_cases']].sort_values(KEYS).reset_index(drop=True)
        if {'Broward','Palm Beach'}-set(result['county']):
            raise InputError('Both required counties must appear.')
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)
    result.attrs['source_audit']=audit
    result.attrs['combined_case_records_path']=str(destination.relative_to(root))
    return result


def rebuilt_county(frame, county, average_spec):
    subset=frame.loc[frame['county'].str.casefold().eq(county.casefold())].copy()
    if subset.empty or subset.duplicated('date').any():
        raise InputError(f'No unique daily case series for {county}.')
    subset=subset.set_index('date').sort_index()
    window=average_spec['window']
    if average_spec['basis']=='observed_rows':
        subset['moving_average']=subset['daily_cases'].rolling(window,min_periods=average_spec['min_periods']).mean()
    else:
        raise InputError('Configure and document an explicit average basis.')
    dates=pd.date_range(subset.index.min(),subset.index.max(),freq='D',name='date')
    missing=len(dates)-len(subset)
    subset=subset.reindex(dates)
    subset.attrs.update({'county':county,'state':'Florida','average_definition':f'{window}-observation trailing mean · partial initial windows',
        'missing_calendar_days':missing,'source':'2020 Cases only.csv + 2021 Cases only.csv',
        'average_supplied':False,'negative_daily_revisions':0})
    return subset


def compare_sources(reconstructed, consolidated_spec):
    comparisons=[]
    for county in ['Pasco','Hillsborough']:
        course=course_county(consolidated_spec,county)
        original=reconstructed.loc[reconstructed['county'].eq(county)].set_index('date')['daily_cases']
        comparison=pd.DataFrame({'supplied':course['daily_cases'],'reconstructed':original}).reindex(course.index)
        comparison=comparison.loc[comparison['supplied'].notna()].copy()
        comparison['county']=county
        comparison['difference']=comparison['reconstructed']-comparison['supplied']
        comparison['matches']=comparison['difference'].eq(0)
        comparisons.append(comparison.reset_index())
    return pd.concat(comparisons,ignore_index=True)
