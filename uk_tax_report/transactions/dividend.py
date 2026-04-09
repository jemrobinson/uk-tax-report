"""Definition of the Dividend class."""

from typing import Any

from .credit_debit import CreditTransaction


class Dividend(CreditTransaction):
    """Transaction where a dividend is paid by a security."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Create a Dividend."""
        super().__init__(*args, **kwargs)
        self.type: str = "Dividend"
