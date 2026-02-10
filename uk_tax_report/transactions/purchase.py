"""Definition of the Purchase class."""

from .credit_debit import DebitTransaction


class Purchase(DebitTransaction):
    """Transaction where a security is bought."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type: str = "Bought"
