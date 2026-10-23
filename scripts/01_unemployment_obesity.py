"""Requirement 1: plot the supplied 2018 observations without changing the data."""
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter, MultipleLocator
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def load_data():
    frame = pd.read_excel(ROOT / 'data' / '2018 Data.xlsx', sheet_name='2018 Data')
    columns = ['NAME', 'Unemployment Rate', 'Obesity Rates']
    frame = frame.loc[:, columns].copy()
    if frame['NAME'].isna().any() or frame['NAME'].duplicated().any():
        raise ValueError('Each observation must have a unique, nonmissing geographic name.')
    for column in columns[1:]:
        frame[column] = pd.to_numeric(frame[column], errors='raise')
        if not frame[column].between(0, 100).all():
            raise ValueError(f'{column}: missing or invalid percentage.')
    return frame


def create_figure(frame):
    with plt.rc_context({'font.family': 'DejaVu Sans', 'font.size': 11,
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'axes.labelcolor': '#243247', 'xtick.color': '#526174',
                         'ytick.color': '#526174', 'svg.fonttype': 'none'}):
        fig, ax = plt.subplots(figsize=(10.5, 7.2), facecolor='white')
        fig.subplots_adjust(left=.11, right=.96, top=.79, bottom=.19)
        fig.text(.11, .94, '2018  /  ECONOMY & HEALTH', fontsize=10,
                 color='#526174', weight='bold')
        fig.text(.11, .88, 'Unemployment and obesity across U.S. jurisdictions',
                 fontsize=19, weight='bold', color='#16263b')
        fig.text(.11, .835, f'{len(frame)} observations · 50 states, Washington, D.C., and Puerto Rico',
                 fontsize=11, color='#526174')
        ax.set_axisbelow(True)
        ax.grid(axis='both', color='#e7ebef', linewidth=.8)
        ax.scatter(frame['Obesity Rates'], frame['Unemployment Rate'],
                   color='yellow', marker='*', s=155, edgecolors='#665500',
                   linewidths=.8, alpha=1, zorder=3)
        ax.set(xlabel='Obesity rate (%)', ylabel='Unemployment rate (%)',
               xlim=(20, 42), ylim=(0, 17))
        ax.xaxis.set_major_formatter(PercentFormatter(xmax=100, decimals=0))
        ax.yaxis.set_major_formatter(PercentFormatter(xmax=100, decimals=0))
        ax.xaxis.set_major_locator(MultipleLocator(5))
        ax.yaxis.set_major_locator(MultipleLocator(2))
        ax.spines['left'].set_color('#c8d0da')
        ax.spines['bottom'].set_color('#c8d0da')
        # Label a few geographic reference points; retain every observation.
        for name, offset in [('Puerto Rico', (-12, 10)), ('Colorado', (10, -17)),
                             ('Mississippi', (-12, 10))]:
            row = frame.loc[frame['NAME'].eq(name)].iloc[0]
            ax.annotate(name, (row['Obesity Rates'], row['Unemployment Rate']),
                        xytext=offset, textcoords='offset points',
                        ha='right' if offset[0] < 0 else 'left', fontsize=9,
                        color='#36465a')
        fig.text(.11, .095, 'Each yellow star represents one jurisdiction. Rates are percentage values as supplied.',
                 fontsize=9, color='#526174')
        fig.text(.11, .065, 'Source: 2018 Data.xlsx, “2018 Data” sheet. Association does not establish causation.',
                 fontsize=9, color='#526174')
        return fig, ax


def main():
    frame = load_data()
    fig, _ = create_figure(frame)
    destination = ROOT / 'figures'
    destination.mkdir(exist_ok=True)
    for extension in ['png', 'svg', 'pdf']:
        fig.savefig(destination / f'01_unemployment_obesity.{extension}', dpi=300,
                    facecolor='white')
    print(f'Plotted all {len(frame)} observations; exported PNG, SVG, and PDF.')
    return frame, fig


if __name__ == '__main__':
    main()
