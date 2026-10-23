"""Requirement 3: supplied moving-average columns and a daily-cases line."""
import _bootstrap
from dv_assignment.workflows import covid

if __name__=='__main__':
    data,figure=covid('Hillsborough')
    print(f'Hillsborough: {data.daily_cases.notna().sum()} observed days; {data.daily_cases.sum():,.0f} cases.')
    print(data.attrs)
