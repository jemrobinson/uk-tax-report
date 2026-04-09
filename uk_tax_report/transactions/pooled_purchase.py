"""Definition of the PooledPurchase class."""

from typing import Any

from moneyed import Currency

from .bed_and_breakfast import BedAndBreakfast
from .disposal import Disposal
from .excess_reportable_income import ExcessReportableIncome
from .purchase import Purchase


class PooledPurchase(Purchase):
    """Combination of several transactions."""

    def __init__(self, currency: Currency, **kwargs: Any) -> None:
        """Create a PooledPurchase."""
        kwargs["date_time"] = kwargs.get("date_time", "0001-01-01")
        super().__init__(currency=currency, **kwargs)
        self.type: str = "Pool"

    @classmethod
    def from_purchase(cls, purchase: Purchase, currency: Currency) -> "PooledPurchase":
        """Create a PooledPurchase from a Purchase."""
        if not purchase:
            return cls(currency)
        return cls(
            date_time=purchase.datetime,
            currency=currency,
            units=purchase.units,
            subtotal=purchase.subtotal,
            fees=purchase.fees,
            taxes=purchase.taxes,
        )

    def add_bed_and_breakfast(self, bed_and_breakfast: BedAndBreakfast) -> None:
        """Add a bed-and-breakfast to the pool."""
        if not isinstance(bed_and_breakfast, BedAndBreakfast):
            msg = f"{bed_and_breakfast} is not a valid BedAndBreakfast!"
            raise TypeError(msg)
        self.datetime = max([self.datetime, bed_and_breakfast.datetime])
        self.subtotal_ = self.subtotal + bed_and_breakfast.gain

    def add_disposal(self, disposal: Disposal) -> None:
        """Add a disposal to the pool."""
        if not isinstance(disposal, Disposal):
            msg = f"{disposal} is not a valid Purchase!"
            raise TypeError(msg)
        self.datetime = max([self.datetime, disposal.datetime])
        self.units = self.units - disposal.units
        self.subtotal_ = self.subtotal - disposal.purchase_total
        self.fees = self.fees + disposal.fees
        self.taxes = self.taxes + disposal.taxes

    def add_eri(self, purchase: ExcessReportableIncome) -> None:
        """Add excess reportable income to the pool."""
        if not isinstance(purchase, ExcessReportableIncome):
            msg = f"{purchase} is not a valid ExcessReportableIncome!"
            raise TypeError(msg)
        self.datetime = max([self.datetime, purchase.datetime])
        # NB. We do not change the number of units owned
        self.subtotal_ = self.subtotal + purchase.subtotal
        self.fees = self.fees + purchase.fees
        self.taxes = self.taxes + purchase.taxes

    def add_purchase(self, purchase: Purchase) -> None:
        """Add a purchase to the pool."""
        if not isinstance(purchase, Purchase):
            msg = f"{purchase} is not a valid Purchase!"
            raise TypeError(msg)
        self.datetime = max([self.datetime, purchase.datetime])
        self.units = self.units + purchase.units
        self.subtotal_ = self.subtotal + purchase.subtotal
        self.fees = self.fees + purchase.fees
        self.taxes = self.taxes + purchase.taxes
