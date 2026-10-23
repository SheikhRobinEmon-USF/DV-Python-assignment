"""Shared script/notebook workflows, with relative paths and auditable outputs."""
import json

from . import charts
from .data import ROOT, config, course_county, course_sales, rebuild_case_records, rebuilt_county


def covid(county):
    settings=config()
    data=course_county(settings['covid'],county)
    figure=charts.pasco(data) if county=='Pasco' else charts.hillsborough(data)
    stem='02_pasco_covid' if county=='Pasco' else '03_hillsborough_covid'
    charts.export(figure,ROOT/'figures',stem)
    return data,figure


def sales():
    data=course_sales(config()['sales'])
    figure=charts.car_sales(data)
    charts.export(figure,ROOT/'figures','04_european_car_sales')
    return data,figure


def reconstruction():
    settings=config()['raw_covid']
    data=rebuild_case_records(settings)
    destination=ROOT/'data/derived'; destination.mkdir(exist_ok=True,parents=True)
    data.to_csv(destination/'reconstructed_covid.csv',index=False,date_format='%Y-%m-%d')
    (destination/'reconstruction_audit.json').write_text(json.dumps(data.attrs['source_audit'],indent=2)+'\n')
    broward=rebuilt_county(data,'Broward',settings['moving_average'])
    palm=rebuilt_county(data,'Palm Beach',settings['moving_average'])
    figure=charts.county_panels(broward,palm)
    charts.export(figure,ROOT/'figures','05_broward_palm_beach')
    return data,broward,palm,figure
