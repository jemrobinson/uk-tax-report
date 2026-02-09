"""Definition of the Security class"""

import copy
import logging
from datetime import MAXYEAR, MINYEAR, date
from typing import Optional

from moneyed import Currency

from .converters import as_fractional_money
from .reconcile import exchange, reconcile
from .transactions import (
    BedAndBreakfast,
    Disposal,
    Dividend,
    ExcessReportableIncome,
    PooledPurchase,
    Purchase,
    Sale,
    Transaction,
)

logger = logging.getLogger(__name__)


class Security:
    """Representation of a single security and associated transactions"""

    def __init__(self, symbol: str, name: str, currency: Currency, isin: str = ""):
        self.currency = currency
        self.isin = isin
        self.name = name
        self.symbol = symbol
        self.transactions: list[Transaction] = []
        self.events_: list[tuple[Transaction, PooledPurchase]] = []

    def __repr__(self) -> str:
        return f"Security({self.name} [{self.symbol}])"

    def __str__(self) -> str:
        output = repr(self) + "\n"
        for transaction in self.transactions:
            output += f"   {transaction}\n"
        return output

    def __lt__(self, other) -> bool:
        return self.name < other.name

    def add_transactions(self, transactions: list[Transaction]) -> None:
        """Add new transactions then resolve them together with existing transactions"""
        # Add new transactions
        self.transactions += transactions
        # Resolve all transactions
        self.resolve_transactions()

    @property
    def disposals(self) -> list[tuple[Transaction, PooledPurchase]]:
        """List of all disposals"""
        return [e for e in self.events if isinstance(e[0], Disposal)]

    @property
    def events(self) -> list[tuple[Transaction, PooledPurchase]]:
        """Return sorted events"""
        self.events_.sort(key=lambda e: e[0].datetime)
        return self.events_

    def is_held(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> bool:
        """Was this security held between the specified dates (inclusive)?"""
        start_date = start_date or date(MINYEAR, 1, 1)
        end_date = end_date or date(MAXYEAR, 12, 31)
        # Check whether any units were held on the start date
        events_before = [
            event for event in self.events if event[0].datetime.date() < start_date
        ]
        if events_before and events_before[-1][1].units > 0:
            return True
        # Check whether any units were held during the year
        for event in filter(
            lambda e: start_date <= e[0].datetime.date() <= end_date, self.events
        ):
            if event[1].units > 0:
                return True
        return False

    def report_capital_gains(self, start_date: date, end_date: date) -> None:
        """Produce a capital gains report"""
        # If there are no disposals in the time range there can be no capital gains
        if not any(start_date <= d[0].date <= end_date for d in self.disposals):
            return

        # Generate the capital gains report
        logger.info("%s %s", f"{self.name:88s}", f"{f'({self.symbol})':>18s}")
        for transaction, pool in self.events:
            # Ignore any transactions after the end of the tax year
            if transaction.datetime.date() > end_date:
                continue
            date_prefix = f"  {transaction.date}:"
            date_spacing = " " * len(date_prefix)
            logger.debug("Processing event of type %s:", type(transaction).__name__)
            logger.debug("=> %s", transaction)
            if transaction.is_null:
                logger.debug("Skipping transaction %s", transaction)
                continue
            # Transactions involving purchase (including ExcessReportableIncome and ScripDividend)
            if isinstance(transaction, Purchase):
                logger.info(
                    "%s %s %s",
                    date_prefix,
                    f"{f'{transaction.type} {transaction.units} shares @ {transaction.subtotal} plus {transaction.charges} costs':52}",
                    f"{transaction.total!s:>18s}",
                )
            # Transactions involving a disposal
            elif isinstance(transaction, Disposal):
                if isinstance(transaction, BedAndBreakfast):
                    logger.info(
                        "%s %s %s",
                        date_prefix,
                        f"{f'Bought {transaction.units} shares (bed-and-breakfast) @ {transaction.unit_price_bought}':52}",
                        f"{transaction.purchase_total!s:>18}",
                    )
                    logger.info(
                        "%s %s %s",
                        date_spacing,
                        f"{f'Sold {transaction.units} shares (bed-and-breakfast) @ {transaction.unit_price_sold}':52}",
                        f"{transaction.sale_total!s:>18}",
                    )
                else:
                    logger.info(
                        "%s %s %s",
                        date_prefix,
                        f"{f'Sold {transaction.units} shares @ {transaction.unit_price_sold} each':52}",
                        f"{transaction.sale_total!s:>18}",
                    )
                if start_date <= transaction.datetime.date() <= end_date:
                    logger.info(
                        "%s %s %s",
                        date_spacing,
                        f"{'Resulting gain':74}",
                        f"{transaction.gain!s:>18}",
                    )
                else:
                    logger.info(
                        "%s Resulting gain applies to another tax year", date_spacing
                    )
            # Transactions involving a sale
            elif isinstance(transaction, Sale):
                logger.info(
                    "%s %s %s",
                    date_prefix,
                    f"{f'Sold {transaction.units} shares @ {transaction.subtotal} plus {transaction.charges} costs':52}",
                    f"{transaction.total!s:>18s}",
                )
            else:
                msg = f"Unknown event of type {type(transaction).__name__}:\n {transaction}"
                raise TypeError(msg)
            logger.info(
                "%s Pool: %d shares @ %s each, cost %s",
                date_spacing,
                pool.units,
                as_fractional_money(pool.unit_price_inc),
                pool.total,
            )

    def report_dividends(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> None:
        """Produce a dividend and ERI report"""
        # Load all dividend and ERI transactions between the dates
        start_date = start_date or date(MINYEAR, 1, 1)
        end_date = end_date or date(MAXYEAR, 12, 31)
        transactions = [
            t
            for t in self.transactions
            if (start_date <= t.datetime.date() <= end_date)
            and isinstance(t, (Dividend, ExcessReportableIncome))
        ]
        # If there are dividends then log them
        if transactions:
            logger.info("%s %s", f"{self.name:88s}", f"{f'({self.symbol})':>18s}")
            for transaction in transactions:
                logger.info(
                    "  %s: %s %s",
                    transaction.date,
                    f"{f'{transaction.type} for {transaction.units} shares @ {as_fractional_money(transaction.unit_price)} each':52}",
                    f"{transaction.total!s:>18}",
                )

    def resolve_transactions(self) -> None:  # noqa: PLR0915
        """Resolve all transactions in the list"""
        # Sort transactions and separate into purchases and sales
        logger.debug(
            "Resolving %d transactions for %s (%s)",
            len(self.transactions),
            self.name,
            self.symbol,
        )
        sorted_transactions = sorted(self.transactions, key=lambda t: t.datetime)
        purchases = [t for t in sorted_transactions if isinstance(t, Purchase)]
        sales = [t for t in sorted_transactions if isinstance(t, Sale)]
        disposals = []

        # Under HS285 share reorganisations should count the new shares as being bought at the same time as the old shares
        # There may be a small additional capital gain
        for idx_sale, sale in [
            s for s in enumerate(sales) if "exchange" in s[1].note.lower()
        ]:
            logger.debug(
                "Combining sale with previous purchases as this is an exchange under HS285:"
            )
            logger.debug("  %s", sale)
            purchases_ = list(filter(lambda p, d=sale.date: p.date < d, purchases))
            purchase_, sale_, disposal = exchange(purchases_, sale)
            logger.debug("  %s", purchases_)
            sales[idx_sale] = sale_
            disposals.append(disposal)
            logger.debug("Result:")
            logger.debug("  %s", purchase_)
            logger.debug("  %s", sale_)
            logger.debug("  %s", disposal)

        # Consider whether each sale must be reconciled against purchases according to HS284
        # First consider same day purchases followed by bed-and-breakfasting against any purchase within 30 days
        # Date-ordering any purchases between 0 and 30 days following the sale will automatically apply this
        for idx_sale, sale in enumerate(sales):
            for idx_purchase, purchase in filter(
                lambda ptuple, d=sale.date: 0
                <= (ptuple[1].date - d).days
                <= BedAndBreakfast.TIME_LIMIT_DAYS,
                enumerate(purchases),
            ):
                logger.debug("Combining purchase and sale under HS284:")
                logger.debug("  %s", purchase)
                logger.debug("  %s", sale)
                purchase_, sale_, disposal = reconcile(purchase, sale)
                disposals.append(BedAndBreakfast(disposal))
                purchases[idx_purchase] = purchase_
                sales[idx_sale] = sale_
                logger.debug("Result:")
                logger.debug("  %s", purchase_)
                logger.debug("  %s", sale_)
                logger.debug("  %s", disposal)
        transactions = [t for t in purchases + sales + disposals if t]

        # Each remaining sale can be converted into a disposal against the existing pool
        self.events_ = []
        pool = PooledPurchase(self.currency)
        for transaction in sorted(transactions, key=lambda t: t.datetime):
            logger.debug(
                "Starting a transaction with %d shares in the pool", pool.units
            )
            pool = copy.deepcopy(pool)
            if isinstance(transaction, ExcessReportableIncome):
                logger.debug(
                    "=> Found a %s on %s:", type(transaction).__name__, transaction.date
                )
                logger.debug("  %s", transaction)
                pool.add_eri(transaction)
                self.events.append((transaction, pool))
            elif isinstance(transaction, Purchase):
                logger.debug(
                    "=> Found a %s on %s:", type(transaction).__name__, transaction.date
                )
                logger.debug("  %s", transaction)
                pool.add_purchase(transaction)
                self.events.append((transaction, pool))
            elif isinstance(transaction, BedAndBreakfast):
                logger.debug("=> Found a BedAndBreakfast on %s:", transaction.date)
                logger.debug("  %s", transaction)
                pool.add_bed_and_breakfast(transaction)
                self.events_.append((transaction, pool))
            elif isinstance(transaction, Disposal):
                logger.debug("=> Found a Disposal on %s:", transaction.date)
                logger.debug("  %s", transaction)
                pool.add_disposal(transaction)
                self.events_.append((transaction, pool))
            elif isinstance(transaction, Sale):
                logger.debug("=> Found a Sale on %s:", transaction.date)
                logger.debug("  %s", transaction)
                logger.debug("... reconciling against pool to give:")
                purchase, sale, disposal = reconcile(pool, transaction)
                logger.debug("  %s", purchase)
                logger.debug("  %s", sale)
                logger.debug("  %s", disposal)
                if sale.total:
                    msg = f"Found an unexpected Sale {sale}"
                    raise ValueError(msg)
                pool.add_disposal(disposal)
                self.events_.append((disposal, pool))
            else:
                msg = f"Unknown event of type {type(transaction).__name__}:\n {transaction}"
                raise TypeError(msg)
            logger.debug("Ending transaction with %d shares in the pool", pool.units)
