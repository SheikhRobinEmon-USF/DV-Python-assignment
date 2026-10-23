"""Requirement 2: two lines, using the actual course workbook's supplied mean."""
import _bootstrap
from dv_assignment.workflows import covid

if __name__=='__main__':
    data,figure=covid('Pasco')
    print(f'Pasco: {data.daily_cases.notna().sum()} observed days; {data.daily_cases.sum():,.0f} cases.')
    print(data.attrs)
