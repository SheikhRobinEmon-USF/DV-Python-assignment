"""Matplotlib figures with explicit units, source notes, and required chart forms."""
from contextlib import contextmanager
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, StrMethodFormatter, MultipleLocator
from decimal import Decimal, ROUND_HALF_UP
import numpy as np

INK='#16263b'
MUTED='#526174'
BLUE='#0072b2'
ORANGE='#d55e00'
PALE_BLUE='#71abc4'


@contextmanager
def style():
    with plt.rc_context({'font.family':'DejaVu Sans','font.size':11,
        'axes.spines.top':False,'axes.spines.right':False,
        'axes.labelcolor':INK,'xtick.color':MUTED,'ytick.color':MUTED,
        'axes.edgecolor':'#c8d0da','svg.fonttype':'none','figure.facecolor':'white'}):
        yield


def header(fig, category, title, subtitle):
    fig.text(.105,.952,category,fontsize=10,color=MUTED,weight='bold')
    fig.text(.105,.896,title,fontsize=21,color=INK,weight='bold')
    fig.text(.105,.848,subtitle,fontsize=10.5,color=MUTED)


def date_axis(ax, data, bottom=True):
    ax.set_axisbelow(True)
    ax.grid(axis='y',color='#e7ebef',linewidth=.8)
    locator=mdates.AutoDateLocator(minticks=5,maxticks=8)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
    ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
    ax.set_ylabel('Cases per day')
    if bottom:
        ax.set_xlabel('Event date')
    ax.set_xlim(data.index.min(),data.index.max())
    low=min(0,float(data['daily_cases'].min()))
    ax.set_ylim(bottom=low*1.1)
    ax.margins(y=.15)


def _period(data):
    return f"{data.index.min():%d %b %Y} – {data.index.max():%d %b %Y}"


def _covid_notes(fig, data, source):
    fig.text(.105,.092,f"Source: {source}. {data.attrs['average_definition']}.",fontsize=8.5,color=MUTED)
    fig.text(.105,.061,f"{data.attrs['missing_calendar_days']} unlisted calendar date(s) shown as gaps; no zero imputation. Counts describe recorded cases, not infection risk.",fontsize=8.5,color=MUTED)


def pasco(data):
    with style():
        fig,ax=plt.subplots(figsize=(11.5,7.4))
        fig.subplots_adjust(left=.105,right=.96,top=.72,bottom=.21)
        header(fig,'02  /  PASCO COUNTY, FLORIDA','Daily COVID cases and the moving average',_period(data))
        ax.plot(data.index,data['daily_cases'],color=PALE_BLUE,lw=1.1,label='Daily cases',zorder=2)
        ax.plot(data.index,data['moving_average'],color=ORANGE,lw=2.2,label='Supplied moving average',zorder=3)
        ax.legend(loc='lower left',bbox_to_anchor=(0,1.04),ncol=2,frameon=False,borderaxespad=0)
        date_axis(ax,data)
        _covid_notes(fig,data,'Combined.xlsx · Pasco worksheet')
        return fig


def hillsborough(data):
    with style():
        fig,ax=plt.subplots(figsize=(11.5,7.4))
        fig.subplots_adjust(left=.105,right=.96,top=.72,bottom=.21)
        header(fig,'03  /  HILLSBOROUGH COUNTY, FLORIDA','Daily COVID cases against the moving average',_period(data))
        bars=ax.bar(data.index,data['moving_average'],width=.86,color=PALE_BLUE,
                    edgecolor='none',alpha=.8,label='Supplied moving average · columns',zorder=2)
        line,=ax.plot(data.index,data['daily_cases'],color=ORANGE,lw=1.05,
                      label='Daily cases · line',zorder=3)
        ax.legend([bars,line],['Supplied moving average · columns','Daily cases · line'],
                  loc='lower left',bbox_to_anchor=(0,1.04),ncol=2,frameon=False,borderaxespad=0)
        date_axis(ax,data)
        _covid_notes(fig,data,'Combined.xlsx · Hillsborough worksheet')
        return fig


def car_sales(totals):
    with style():
        fig,ax=plt.subplots(figsize=(11.5,7.4))
        fig.subplots_adjust(left=.2,right=.91,top=.73,bottom=.23)
        header(fig,'04  /  EUROPEAN CAR SALES','Sales and costs in three European markets',
               f"{totals.attrs['source_rows']:,} transactions · countries ordered by total sales")
        y=np.arange(len(totals)); height=.29
        sales=ax.barh(y-height/2,totals['total_sales'],height,color=BLUE,label='Total sales')
        costs=ax.barh(y+height/2,totals['total_costs'],height,color=ORANGE,label='Total costs · purchase + labor')
        ax.set_yticks(y,totals.index)
        ax.invert_yaxis()
        ax.set_xlim(0,float(totals[['total_sales','total_costs']].max().max())*1.18)
        ax.set_axisbelow(True); ax.grid(axis='x',color='#e7ebef',lw=.8)
        ax.spines['left'].set_visible(False)
        ax.tick_params(axis='y',length=0,pad=12)
        ax.xaxis.set_major_formatter(FuncFormatter(lambda value,_:f'{value/1_000_000:,.0f}'))
        ax.xaxis.set_major_locator(MultipleLocator(5_000_000))
        ax.set_xlabel(f"Millions of {totals.attrs['currency']}")
        for container in [sales,costs]:
            ax.bar_label(container,labels=[str((Decimal(str(bar.get_width()))/Decimal('1000000')).quantize(Decimal('.01'),rounding=ROUND_HALF_UP))+'M' for bar in container],
                         padding=6,fontsize=10,color=INK)
        ax.legend(loc='lower left',bbox_to_anchor=(0,1.03),ncol=2,frameon=False,borderaxespad=0)
        fig.text(.105,.11,'Source: Simplified Car Sales Data.xlsx · CarSalesData worksheet. Sales = sum(SalePrice).',fontsize=9,color=MUTED)
        fig.text(.105,.079,'Total costs = sum(CostPrice + LaborCost). Purchase cost and labor are itemized in the notebook.',fontsize=9,color=MUTED)
        fig.text(.105,.048,'Currency: USD, as confirmed by the student; no currency conversion has been applied.',fontsize=9,color=MUTED)
        return fig


def county_panels(broward,palm_beach):
    with style():
        fig,axes=plt.subplots(2,2,figsize=(13,9.4),sharex=True,sharey=True)
        fig.subplots_adjust(left=.095,right=.965,top=.77,bottom=.19,hspace=.36,wspace=.16)
        header(fig,'05  /  RECONSTRUCTED COVID SOURCE','Broward and Palm Beach: daily cases and trend',
               'Rows identify counties · columns separate the daily signal from its moving average')
        for row,data in enumerate([broward,palm_beach]):
            for col,field,color,label in [(0,'daily_cases',BLUE,'Daily cases'),(1,'moving_average',ORANGE,'Moving average')]:
                ax=axes[row,col]
                ax.plot(data.index,data[field],color=color,lw=1.2 if col==0 else 2)
                ax.set_title(f"{data.attrs['county']} · {label}",loc='left',fontsize=12,color=INK,pad=10)
                date_axis(ax,data,bottom=(row==1))
                if col==1:
                    ax.set_ylabel('')
        start=min(broward.index.min(),palm_beach.index.min()); end=max(broward.index.max(),palm_beach.index.max())
        for ax in axes.flat:
            ax.set_xlim(start,end)
        fig.text(.095,.105,'Source: reconstructed daily counts from both yearly course CSVs; identical date and case scales in all panels.',fontsize=9,color=MUTED)
        fig.text(.095,.074,broward.attrs['average_definition']+'. Definition follows the supplied consolidated workbook.',fontsize=9,color=MUTED)
        fig.text(.095,.043,'Unlisted dates remain gaps; record counts are not population-adjusted rates. See notebook for source reconciliation.',fontsize=9,color=MUTED)
        return fig


def export(fig,destination,stem):
    destination=Path(destination); destination.mkdir(parents=True,exist_ok=True)
    for suffix in ['png','svg','pdf']:
        fig.savefig(destination/f'{stem}.{suffix}',dpi=300,facecolor='white')
