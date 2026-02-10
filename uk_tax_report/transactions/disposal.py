"""Definition of the Disposal class"""

from moneyed import Money

from uk_tax_report.converters import abs_divide, as_money

from .transaction import Transaction


class Disposal(Transaction):
    """A combined purchase and sale"""

    def __init__(  # type: ignore[too-many-positional-arguments]
        self,
        date_time,
        currency,
        units,
        purchase_total,
        purchase_fees,
        purchase_taxes,
        sale_total,
        sale_fees,
        sale_taxes,
    ):
        super().__init__(date_time=date_time, currency=currency, units=units)
        self.purchase_total: Money = as_money(purchase_total, currency)
        self.purchase_fees: Money = as_money(purchase_fees, currency)
        self.purchase_taxes: Money = as_money(purchase_taxes, currency)
        self.sale_total: Money = as_money(sale_total, currency)
        self.sale_fees: Money = as_money(sale_fees, currency)
        self.sale_taxes: Money = as_money(sale_taxes, currency)
        self.type: str = "Disposal"

    @property
    def subtotal(self) -> Money:
        """Subtotal is not a valid property for this class"""
        msg = "Subtotal is not a valid property for the Disposal class"
        raise NotImplementedError(msg)

    @property
    def total(self) -> Money:
        """Total is not a valid property for this class"""
        msg = "Total is not a valid property for the Disposal class"
        raise NotImplementedError(msg)

    @property
    def unit_price_sold(self) -> Money:
        """The unit price at which the units were sold"""
        return abs_divide(self.sale_total, self.units)

    @property
    def unit_price_bought(self) -> Money:
        """The unit price at which the units were bought"""
        return abs_divide(self.purchase_total, self.units)

    @property
    def gain(self) -> Money:
        """The capital gain made upon sale"""
        return self.sale_total - self.purchase_total

    @property
    def is_null(self) -> bool:
        """Whether this is a null transaction"""
        return (self.sale_total == self.currency.zero) and (
            self.purchase_total == self.currency.zero
        )

    def __str__(self) -> str:
        return (
            f"Transaction: {self.type:8s} date = {self.date}, units = {self.units}, "
            f"purchase_total = {self.purchase_total}, sale_total = {self.sale_total}, "
            f"gain = {self.gain}"
        )
