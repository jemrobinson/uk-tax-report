"""General utility functions for converting between types"""

import datetime
from contextlib import suppress
from decimal import Decimal, InvalidOperation
from math import isnan
from typing import Any, Union

from dateutil.parser import parse
from moneyed import Currency, CurrencyDoesNotExist, Money, format_money, get_currency


def abs_divide(money: Money, number: Union[float, Decimal]) -> Money:
    """
    The absolute value of dividing Money by a number.
    Returns 0 if there is an invalid division.
    """
    try:
        result = abs(money / float(number))
    except (ZeroDivisionError, InvalidOperation):
        result = Money(0, money.currency)
    return result


def as_currency(data: Any) -> Currency:
    """Convert arbitrary data into Currency"""
    if isinstance(data, Currency):
        return data
    with suppress(CurrencyDoesNotExist):
        return get_currency(code=data)
    with suppress(CurrencyDoesNotExist):
        return get_currency(iso=data)
    raise CurrencyDoesNotExist(data)


def as_datetime(data: Any) -> datetime.datetime:
    """Convert arbitrary data into a datetime"""
    if isinstance(data, datetime.datetime):
        return data
    return parse(data)


def as_fractional_money(money: Money) -> str:
    """Convert Money to a formatted string"""
    return format_money(money, format="\xa4#.####", currency_digits=False)


def as_money(data: Any, currency: Currency) -> Money:
    """Convert arbitrary data into Money"""
    if isinstance(data, Money):
        return data
    if isnan(float(data)):
        return Money(0, currency)
    return Money(data, currency)
