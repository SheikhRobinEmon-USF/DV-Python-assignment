"""Requirement 4: horizontal grouped bars for sales and purchase-plus-labor costs."""
import _bootstrap
from dv_assignment.workflows import sales

if __name__=='__main__':
    totals,figure=sales()
    print(totals.to_string())
