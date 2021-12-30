from .utils import as_money, abs_divide
from .sale import Sale


class Disposal(Sale):
    def __init__(
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
        self.purchase_total = as_money(purchase_total, currency)
        self.purchase_fees = as_money(purchase_fees, currency)
        self.purchase_taxes = as_money(purchase_taxes, currency)
        self.sale_total = as_money(sale_total, currency)
        self.sale_fees = as_money(sale_fees, currency)
        self.sale_taxes = as_money(sale_taxes, currency)

    @property
    def unit_price_sold(self):
        return abs_divide(self.sale_total, self.units)

    @property
    def unit_price_bought(self):
        return abs_divide(self.purchase_total, self.units)

    @property
    def gain(self):
        return self.sale_total - self.purchase_total

    def __str__(self):
        return f"Disposal :: date = {self.date}, units = {self.units}, purchase_total = {self.purchase_total}, sale_total = {self.sale_total}, gain = {self.gain}"
