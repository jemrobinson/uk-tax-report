"""Definition of the ExcessReportableIncome class."""

from datetime import datetime

from moneyed import Currency
from pandas import DateOffset

from .purchase import Purchase


class ExcessReportableIncome(Purchase):
    """Excess reportable income from accumulation shares.

    This is treated as a purchase of 0 additional shares.
    """

    def __init__(
        self,
        date_time: datetime,
        currency: Currency,
        units: int,
        amount: float,
        **kwargs,
    ) -> None:
        super().__init__(
            date_time=date_time,
            currency=currency,
            subtotal=amount,
            units=units,
            fees=0,
            taxes=0,
            **kwargs,
        )
        self.type = "ERI"
        # Note that ERIs are reported (and based on holdings from) six months before
        # they are booked as income
        self.date_reported = date_time - DateOffset(months=6)
