"""Audit source missing values and distinguish calendar gaps without imputing data."""
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import pandas as pd
from dv_assignment.data import config, course_county, rebuilt_county, audit_daily_series


def main():
    source_rows=[]
    for filename in ['2018 Data.xlsx','Combined.xlsx','Simplified Car Sales Data.xlsx']:
        path=ROOT/'data'/filename
        for sheet,frame in pd.read_excel(path,sheet_name=None).items():
            for field,count in frame.isna().sum().items():
                source_rows.append({'file':filename,'sheet':sheet,'field':field,
                                    'rows':len(frame),'pandas_null_values':int(count)})
    for year in [2020,2021]:
        filename=f'{year} Cases only.csv'
        totals=None; rows=0
        for chunk in pd.read_csv(ROOT/'data'/filename,chunksize=100_000,low_memory=False):
            nulls=chunk.isna().sum()
            totals=nulls if totals is None else totals.add(nulls,fill_value=0)
            rows+=len(chunk)
        for field,count in totals.items():
            source_rows.append({'file':filename,'sheet':'CSV','field':field,
                                'rows':rows,'pandas_null_values':int(count)})
    settings=config(); frames=[course_county(settings['covid'],c) for c in ['Pasco','Hillsborough']]
    rebuilt=pd.read_csv(ROOT/'data/derived/reconstructed_covid.csv',parse_dates=['date'])
    frames.extend(rebuilt_county(rebuilt,c,settings['raw_covid']['moving_average']) for c in ['Broward','Palm Beach'])
    summaries=[]; gaps=[]
    for frame in frames:
        summary,dates=audit_daily_series(frame)
        summaries.append(summary);gaps.append(dates)
    destination=ROOT/'reports';destination.mkdir(exist_ok=True)
    pd.DataFrame(source_rows).to_csv(destination/'source_null_audit.csv',index=False)
    summary=pd.concat(summaries,ignore_index=True)
    summary.to_csv(destination/'missing_value_summary.csv',index=False)
    pd.concat(gaps,ignore_index=True).to_csv(destination/'unlisted_calendar_dates.csv',index=False)
    print(summary.to_string(index=False))
    print('\nOriginal required-key nulls:')
    required={'2020 Cases only.csv':['County','EventDate','ObjectId2'],
              '2021 Cases only.csv':['County','EventDate','ObjectId']}
    for row in source_rows:
        if row['field'] in required.get(row['file'],[]):
            print(row['file'],row['field'],row['pandas_null_values'])
    print('Full column audit saved; pandas also interprets source NA tokens as missing.')


if __name__=='__main__':
    main()
