"""Requirement 7: inclusive boundary, decimal-safe comparisons, explicit bad-data errors."""
from decimal import Decimal, InvalidOperation


def classify_products(unit_costs,list_prices):
    if len(unit_costs)!=len(list_prices):
        raise ValueError('Cost and price lists must have equal lengths.')
    labels=[]
    for cost,price in zip(unit_costs,list_prices):
        try:
            cost=Decimal(str(cost)); price=Decimal(str(price))
        except (InvalidOperation,ValueError) as error:
            raise ValueError('Unit cost and list price must be numeric and nonmissing.') from error
        if not cost.is_finite() or not price.is_finite() or cost<0 or price<0:
            raise ValueError('Unit cost must be finite and nonnegative; list price must be finite and nonnegative.')
        labels.append('Lucrative' if cost <= Decimal('0.75')*price else 'Not lucrative')
    return labels


# Self-contained SCRIPT_STR body: the Tableau host need not import this repository.
TABLEAU_SCRIPT='''from decimal import Decimal, InvalidOperation
if len(_arg1) != len(_arg2):
    raise ValueError("Mismatched unit cost and list price arrays")
result = []
for c, p in zip(_arg1, _arg2):
    try:
        cost, price = Decimal(str(c)), Decimal(str(p))
    except (InvalidOperation, ValueError):
        raise ValueError("Unit cost and list price must be numeric and nonmissing")
    if not cost.is_finite() or not price.is_finite() or cost < 0 or price < 0:
        raise ValueError("Invalid unit cost or list price; inspect source data")
    result.append("Lucrative" if cost <= Decimal("0.75") * price else "Not lucrative")
return result'''
