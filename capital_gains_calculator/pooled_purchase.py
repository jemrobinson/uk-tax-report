"""Definition of the PooledPurchase class"""
# Local imports
from .disposal import Disposal, BedAndBreakfast
from .purchase import Purchase


class PooledPurchase(Purchase):
    """Combination of several transactions"""

    def __init__(self, currency, **kwargs):
        kwargs["date_time"] = kwargs.get("date_time", "0001-01-01")
        super().__init__(currency=currency, **kwargs)
        self.type = "POOL"

    @classmethod
    def from_purchase(cls, purchase, currency):
        """Create a PooledPurchase from a Purchase"""
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

    def add_purchase(self, purchase):
        """Add a purchase to the pool"""
        if not isinstance(purchase, Purchase):
            raise ValueError(f"{purchase} is not a valid Purchase!")
        self.datetime = max([self.datetime, purchase.datetime])
        self.units = self.units + purchase.units
        self.subtotal_ = self.subtotal + purchase.subtotal
        self.fees = self.fees + purchase.fees
        self.taxes = self.taxes + purchase.taxes

    def add_disposal(self, disposal):
        """Add a disposal to the pool"""
        if not isinstance(disposal, Disposal):
            raise ValueError(f"{disposal} is not a valid Purchase!")
        self.datetime = max([self.datetime, disposal.datetime])
        self.units = self.units - disposal.units
        self.subtotal_ = self.subtotal - disposal.purchase_total
        self.fees = self.fees + disposal.fees
        self.taxes = self.taxes + disposal.taxes

    def add_bed_and_breakfast(self, bed_and_breakfast):
        """Add a bed-and-breakfast to the pool"""
        if not isinstance(bed_and_breakfast, BedAndBreakfast):
            raise ValueError(f"{bed_and_breakfast} is not a valid BedAndBreakfast!")
        self.datetime = max([self.datetime, bed_and_breakfast.datetime])
        self.subtotal_ = self.subtotal + bed_and_breakfast.gain
