"""Requirement 7 Python function, also used in the Tableau SCRIPT_STR expression."""
import _bootstrap
from dv_assignment.profitability import classify_products

if __name__=='__main__':
    # Boundary checks only: these examples are not course product data.
    examples=classify_products([74.99,75,75.01],[100,100,100])
    assert examples==['Lucrative','Lucrative','Not lucrative']
    print('Boundary checks:',examples)
