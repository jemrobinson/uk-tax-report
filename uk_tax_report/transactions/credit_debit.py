"""Definition of the CreditTransaction and DebitTransaction classes"""

# Third-party imports
from moneyed import Money

# Local imports
from .transaction import Transaction


class CreditTransaction(Transaction):
    """Transaction where money is received"""

    @property
    def total(self) -> Money:
        """Total value received in this transaction"""
        return self.subtotal - self.charges


class DebitTransaction(Transaction):
    """Transaction where money is paid"""

    @property
    def total(self) -> Money:
        """Total value paid in this transaction"""
        return self.subtotal + self.charges
