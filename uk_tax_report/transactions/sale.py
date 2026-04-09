"""Definition of the Sale class."""

from .credit_debit import CreditTransaction


class Sale(CreditTransaction):
    """Transaction where a security is sold."""

    def __init__(self, *args, **kwargs) -> None:
        """Create a Sale."""
        super().__init__(*args, **kwargs)
        self.type: str = "Sold"
