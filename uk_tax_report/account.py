"""Definition of the Account class."""

import logging
from datetime import date
from typing import Optional

from .converters import as_currency
from .readers import DataFile
from .security import Security
from .transactions import Transaction

logger = logging.getLogger(__name__)


class Account:
    """Account containing several transactions."""

    def __init__(self, name: str, currency: str, data: Optional[DataFile] = None):
        """Create an Account."""
        self.name = name
        self.currency = as_currency(currency)
        if data:
            self.securities = [
                Security(
                    currency=self.currency,
                    isin=security_tuple.ISIN,
                    name=security_tuple.Security,
                    symbol=security_tuple.Symbol,
                )
                for security_tuple in data.securities[self.name]
            ]
            for security in self.securities:
                security.add_transactions(
                    data.get_transaction_list(self.name, security.name, self.currency),
                )
        else:
            self.securities = []

    def __add__(self, other: "Account") -> "Account":
        if self.currency != other.currency:
            msg = (
                f"Cannot add account '{self.name}' with currency {self.currency} to "
                f"account '{other.name}' with currency {other.currency}"
            )
            raise ValueError(msg)
        output = Account(f"{self.name}-{other.name}", self.currency)
        output.securities = [
            Security(security.symbol, security.name, security.currency, security.isin)
            for security in set(self.securities + other.securities)
        ]
        for security in output.securities:
            for existing_security in self.securities + other.securities:
                if existing_security.name == security.name:
                    security.add_transactions(existing_security.transactions)
        return output

    def __radd__(self, other):
        if not isinstance(other, Account):
            return self
        return other + self

    @property
    def taxable_securities(self) -> list[Security]:
        """List of securities excluding any VCTs."""
        return sorted(
            [s for s in self.securities if "VCT" not in s.name],
            key=lambda s: s.name,
        )

    @property
    def transactions(self) -> list[Transaction]:
        """List of transactions in this account."""
        return [
            transaction
            for security in self.securities
            for transaction in security.transactions
        ]

    def holdings(self, start_date: date, end_date: date) -> list[Security]:
        """List of securities held between these dates."""
        return [
            security
            for security in self.securities
            if security.is_held(start_date, end_date)
        ]

    def report(
        self,
        start_date: date,
        end_date: date,
        *,
        include_non_taxable: bool = False,
    ):
        """Report tax summary for this account."""
        # Restrict to specified accounts
        logger.info(
            "Account '%s' has %d transactions across %d securities",
            self.name,
            len(self.transactions),
            len(self.securities),
        )

        # Holdings
        logger.info(
            "Listing holdings during UK tax year %s-%s...",
            start_date.year,
            end_date.year,
        )
        for security in sorted(self.holdings(start_date, end_date)):
            logger.info(
                "  %s %s %s",
                f"{f'[{security.isin}]':14}",
                f"{f'[{security.symbol}]':15}",
                security.name,
            )
        relevant_securities = (
            sorted(self.securities, key=lambda s: s.name)
            if include_non_taxable
            else self.taxable_securities
        )

        # Capital gains
        logger.info(
            "Looking for capital gains during UK tax year %s-%s...",
            start_date.year,
            end_date.year,
        )
        for security in relevant_securities:
            security.report_capital_gains(start_date, end_date)

        # Dividends and ERIs
        logger.info(
            "Looking for dividends and ERIs during UK tax year %s-%s...",
            start_date.year,
            end_date.year,
        )
        for security in relevant_securities:
            security.report_dividends(start_date, end_date)

    def __str__(self) -> str:
        return f"Account '{self.name}' has {len(self.securities)} securities"
