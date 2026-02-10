"""Definition of the BedAndBreakfast class."""

from .disposal import Disposal


class BedAndBreakfast(Disposal):
    """A disposal where the buying/selling are within 30 days."""

    TIME_LIMIT_DAYS = 30

    def __init__(self, disposal: Disposal):
        super().__init__(
            disposal.datetime,
            disposal.currency,
            disposal.units,
            disposal.purchase_total,
            disposal.purchase_fees,
            disposal.purchase_taxes,
            disposal.sale_total,
            disposal.sale_fees,
            disposal.sale_taxes,
        )
        self.type: str = "Bed-and-breakfast"
