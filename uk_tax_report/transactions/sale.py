"""Definition of the Sale class"""

# Third-party imports
from moneyed import Money

# Local imports
from .credit_debit import CreditTransaction


class Sale(CreditTransaction):
    """Transaction where a security is sold"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type: str = "Sold"
