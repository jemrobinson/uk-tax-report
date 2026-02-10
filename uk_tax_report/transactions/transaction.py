"""Definition of the Transaction class"""

from abc import ABC, abstractmethod
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Union

from moneyed import Currency, Money

from uk_tax_report.converters import abs_divide, as_currency, as_datetime, as_money


class Transaction(ABC):
    """Transaction where money is exchanged for a security"""

    def __init__(
        self,
        date_time: Union[str, datetime],
        currency: Union[str, Currency],
        units: int = 0,
        subtotal: Union[float, Money] = 0,
        fees: Union[float, Money] = 0,
        taxes: Union[float, Money] = 0,
        note: str = "",
    ):
        self.datetime: datetime = as_datetime(date_time)
        self.currency: Currency = as_currency(currency)
        self.units: Decimal = Decimal(units)
        self.subtotal_: Money = as_money(subtotal, self.currency)
        self.fees: Money = as_money(fees, self.currency)
        self.taxes: Money = as_money(taxes, self.currency)
        self.note: str = str(note)
        self.type: Optional[str] = None

    @property
    def date(self) -> date:
        """Date of transaction"""
        return self.datetime.date()

    @property
    def unit_price(self) -> Money:
        """Base price paid per unit in this transaction"""
        return abs_divide(self.subtotal, self.units)

    @property
    def unit_fees(self) -> Money:
        """Fees paid per unit in this transaction"""
        return abs_divide(self.fees, self.units)

    @property
    def unit_taxes(self) -> Money:
        """Taxes paid per unit in this transaction"""
        return abs_divide(self.taxes, self.units)

    @property
    def unit_price_inc(self) -> Money:
        """Total price paid per unit in this transaction"""
        return abs_divide(self.total, self.units)

    @property
    def charges(self) -> Money:
        """Total charges paid in this transaction"""
        return self.fees + self.taxes

    @property
    def subtotal(self) -> Money:
        """Subtotal in this transaction before fees, taxes etc."""
        return self.subtotal_

    @property
    @abstractmethod
    def total(self) -> Money:
        """Total must be implemented by child classes"""
        ...

    @property
    def is_null(self) -> bool:
        """Whether this is a null transaction"""
        return (self.total == self.currency.zero) and (self.units == 0)

    def __str__(self) -> str:
        return (
            f"Transaction: {self.type:8s} date = {self.date}, units = {self.units}, "
            f"unit_price = {self.unit_price}, subtotal = {self.subtotal}, "
            f"fees = {self.fees}, taxes = {self.taxes}, total = {self.total}"
        )
