"""Definition of the Purchase class."""

from typing import Any

from .credit_debit import DebitTransaction


class Purchase(DebitTransaction):
    """Transaction where a security is bought."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Create a Purchase."""
        super().__init__(*args, **kwargs)
        self.type: str = "Bought"
