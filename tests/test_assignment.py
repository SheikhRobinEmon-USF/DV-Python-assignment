"""Behavior checks against actual supplied data, plus explicit edge-case fixtures."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from dv_assignment.data import ROOT, InputError, config, course_county, course_sales, rebuilt_county, compare_sources, audit_daily_series, daily_preview
from dv_assignment.profitability import classify_products, TABLEAU_SCRIPT
from dv_assignment import charts


class ProfitabilityTests(unittest.TestCase):
    def test_inclusive_and_nearby_threshold(self):
        self.assertEqual(classify_products([74.99,75,75.01],[100]*3),['Lucrative','Lucrative','Not lucrative'])

    def test_decimal_boundary(self):
        self.assertEqual(classify_products([.3],[.4]),['Lucrative'])

    def test_zero_boundary_follows_exact_rule(self):
        self.assertEqual(classify_products([0,1],[0,0]),['Lucrative','Not lucrative'])

    def test_invalid_or_missing_is_not_misclassified(self):
        for value in [None,float('nan'),float('inf'),'bad',-1]:
            with self.subTest(value=value),self.assertRaises(ValueError):
                classify_products([value],[100])

    def test_length_mismatch(self):
        with self.assertRaises(ValueError):
            classify_products([75],[])

    def test_tableau_body_has_same_behavior(self):
        namespace={}
        exec('def evaluate(_arg1,_arg2):\n'+'\n'.join('    '+line for line in TABLEAU_SCRIPT.splitlines()),namespace)
        self.assertEqual(namespace['evaluate']([75,75.01,.3],[100,100,.4]),['Lucrative','Not lucrative','Lucrative'])


class CourseDataTests(unittest.TestCase):
    def test_2018_complete_and_required_scatter(self):
        path=ROOT/'scripts/01_unemployment_obesity.py'
        spec=importlib.util.spec_from_file_location('scatter_analysis',path)
        module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        frame=module.load_data(); fig,ax=module.create_figure(frame)
        self.assertEqual(len(frame),52)
        self.assertEqual(len(ax.collections[0].get_offsets()),52)
        np.testing.assert_allclose(ax.collections[0].get_facecolors()[0],[1,1,0,1])
        # A five-point star has ten alternating tips/valleys plus the closing vertex.
        self.assertEqual(len(ax.collections[0].get_paths()[0].vertices),11)
        plt.close(fig)

    def test_pasco_exact_source_total_and_gaps(self):
        frame=course_county(config()['covid'],'Pasco')
        self.assertEqual(frame.daily_cases.notna().sum(),367)
        self.assertEqual(frame.daily_cases.sum(),34047)
        self.assertEqual(frame.daily_cases.isna().sum(),4)
        self.assertEqual(frame.index.min(),pd.Timestamp('2020-03-01'))
        self.assertEqual(frame.index.max(),pd.Timestamp('2021-03-06'))

    def test_hillsborough_exact_source_total_and_gap(self):
        frame=course_county(config()['covid'],'Hillsborough')
        self.assertEqual(frame.daily_cases.notna().sum(),370)
        self.assertEqual(frame.daily_cases.sum(),113597)
        self.assertEqual(frame.daily_cases.isna().sum(),1)

    def test_duplicates_do_not_silently_aggregate(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); rows=pd.DataFrame({'when':pd.to_datetime(['2020-01-01']*2),'n':[1,2],'avg':[1,1.5]})
            rows.to_excel(root/'example.xlsx',sheet_name='Pasco',index=False)
            spec={'path':'example.xlsx','sheets':{'Pasco':{'sheet':'Pasco','date':'when','daily_cases':'n','moving_average':'avg'}},'average_window_observations':8}
            with self.assertRaisesRegex(InputError,'Duplicate dates'):
                course_county(spec,'Pasco',root)

    def test_sales_exact_totals_and_country_selection(self):
        totals=course_sales(config()['sales'])
        self.assertEqual(totals.transactions.sum(),259)
        self.assertEqual(set(totals.index),{'United Kingdom','France','Germany'})
        self.assertEqual(totals.loc['United Kingdom','total_sales'],15725000)
        self.assertEqual(totals.loc['France','total_costs'],1496571)
        self.assertEqual(totals.loc['Germany','total_costs'],161461)
        self.assertGreater(totals.loc['Germany','total_costs'],totals.loc['Germany','total_sales'])

    def test_rolling_mean_uses_observed_rows_not_imputed_zeros(self):
        # Synthetic fixture to test the method; never used as submission data.
        frame=pd.DataFrame({'county':['Broward']*3,'state':['Florida']*3,
             'date':pd.to_datetime(['2020-01-01','2020-01-03','2020-01-04']),'daily_cases':[2,4,6]})
        result=rebuilt_county(frame,'Broward',{'basis':'observed_rows','window':2,'min_periods':1})
        self.assertTrue(pd.isna(result.loc['2020-01-02','daily_cases']))
        self.assertEqual(result.loc['2020-01-03','moving_average'],3)
        self.assertEqual(result.loc['2020-01-04','moving_average'],5)

    def test_reconstruction_reconciles_both_original_sources(self):
        audit=json.loads((ROOT/'data/derived/reconstruction_audit.json').read_text())
        source=pd.read_csv(ROOT/'data/derived/reconstructed_covid.csv',parse_dates=['date'])
        self.assertEqual([x['case_records'] for x in audit],[1341647,938226])
        self.assertEqual(source.daily_cases.sum(),2279873)
        self.assertFalse(source.duplicated(['state','county','date']).any())
        self.assertEqual(len(source),27625)
        self.assertEqual(source.loc[source.county.eq('Broward'),'daily_cases'].sum(),241293)
        self.assertEqual(source.loc[source.county.eq('Palm Beach'),'daily_cases'].sum(),144945)
        self.assertEqual(audit[1]['missing_case_flags_retained'],3)

    def test_full_case_source_has_all_original_rows(self):
        total=sum(len(chunk) for chunk in pd.read_csv(ROOT/'data/derived/combined_case_records.csv',usecols=['record_id'],chunksize=200000))
        self.assertEqual(total,2279873)

    def test_cross_source_differences_are_exposed(self):
        source=pd.read_csv(ROOT/'data/derived/reconstructed_covid.csv',parse_dates=['date'])
        comparison=compare_sources(source,config()['covid'])
        self.assertEqual((~comparison.loc[comparison.county.eq('Pasco'),'matches']).sum(),278)
        self.assertEqual((~comparison.loc[comparison.county.eq('Hillsborough'),'matches']).sum(),350)

    def test_required_chart_forms_and_shared_panel_scales(self):
        pasco=course_county(config()['covid'],'Pasco')
        fig=charts.pasco(pasco); self.assertEqual(len(fig.axes[0].lines),2);plt.close(fig)
        hill=course_county(config()['covid'],'Hillsborough')
        fig=charts.hillsborough(hill); self.assertEqual(len(fig.axes[0].lines),1)
        self.assertEqual(len(fig.axes[0].patches),len(hill));plt.close(fig)
        fig=charts.car_sales(course_sales(config()['sales']))
        self.assertEqual(len(fig.axes[0].patches),6)
        self.assertTrue(all(p.get_width()>p.get_height() for p in fig.axes[0].patches));plt.close(fig)
        source=pd.read_csv(ROOT/'data/derived/reconstructed_covid.csv',parse_dates=['date'])
        average=config()['raw_covid']['moving_average']
        a=rebuilt_county(source,'Broward',average);b=rebuilt_county(source,'Palm Beach',average)
        fig=charts.county_panels(a,b)
        self.assertEqual(len(fig.axes),4)
        self.assertEqual(fig.axes[0].get_xlim(),fig.axes[3].get_xlim())
        self.assertEqual(fig.axes[0].get_ylim(),fig.axes[3].get_ylim())
        self.assertIn('Broward',fig.axes[0].get_title(loc='left'))
        self.assertIn('Palm Beach',fig.axes[2].get_title(loc='left'))
        plt.close(fig)


class MissingValueAuditTests(unittest.TestCase):
    def test_audit_attributes_nulls_to_inserted_dates(self):
        settings=config()
        for county,expected in [('Pasco',4),('Hillsborough',1)]:
            frame=course_county(settings['covid'],county)
            summary,gaps=audit_daily_series(frame)
            self.assertTrue(summary.nulls_on_observed_dates.eq(0).all())
            self.assertTrue(summary.total_display_nulls.eq(expected).all())
            self.assertEqual(len(gaps),expected)

    def test_audit_does_not_hide_an_observed_value_null(self):
        frame=course_county(config()['covid'],'Pasco')
        frame.loc['2020-03-01','daily_cases']=np.nan
        summary,_=audit_daily_series(frame)
        self.assertEqual(summary.loc[summary.field.eq('daily_cases'),'nulls_on_observed_dates'].iloc[0],1)

    def test_preview_changes_labels_without_imputation(self):
        frame=course_county(config()['covid'],'Pasco')
        original=frame.copy(deep=True)
        preview=daily_preview(frame)
        self.assertIn('Not listed',preview.to_html())
        pd.testing.assert_frame_equal(frame,original)
        self.assertEqual(frame.daily_cases.isna().sum(),4)


if __name__=='__main__':
    unittest.main(verbosity=2)
