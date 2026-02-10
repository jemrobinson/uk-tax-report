"""Definition of the Dividend class."""

from .credit_debit import CreditTransaction


class Dividend(CreditTransaction):
    """Transaction where a dividend is paid by a security."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type: str = "Dividend"
