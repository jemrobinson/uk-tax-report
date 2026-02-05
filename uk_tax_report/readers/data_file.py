"""Definition of the Reader class"""

import pandas as pd
from moneyed import Currency

from ..transactions import (
    Dividend,
    ExcessReportableIncome,
    Purchase,
    Sale,
    ScripDividend,
    Transaction,
)


class DataFile:
    """Read a PortfolioPerformance data file"""

    def __init__(self):
        self.df_transactions: pd.DataFrame

    @property
    def account_names(self) -> set[str]:
        """List of account names"""
        return set(self.df_transactions["Cash Account"])

    @property
    def securities(self) -> dict[str, pd.DataFrame]:
        """Dictionary of account_name -> DataFrame where the DataFrame contains unique symbols and names of securities in that account"""
        securities = {}
        for account_name in self.account_names:
            securities[account_name] = sorted(
                set(
                    self.df_transactions.loc[
                        (self.df_transactions["Cash Account"] == account_name)
                    ][["Symbol", "Security", "ISIN"]].itertuples(index=False)
                ),
                key=lambda t: t.Security.lower(),
            )
        return securities

    def get_transaction_list(
        self, account_name: str, security_name: str, currency: Currency
    ) -> list[Transaction]:
        """List of all transactions for a given account and security"""
        transactions = []
        for _, transaction in self.df_transactions.loc[
            (self.df_transactions["Cash Account"] == account_name)
            & (self.df_transactions["Security"] == security_name)
        ].iterrows():
            if transaction.Type.lower() in ["buy", "delivery_inbound"]:
                if (
                    transaction.Note
                    and str(transaction.Note).lower() == "scrip dividend"
                ):
                    bought = ScripDividend(
                        transaction.Date,
                        currency,
                        transaction.Shares,
                        0,
                        transaction.Fees,
                        transaction.Taxes,
                        transaction.Note,
                    )
                else:
                    bought = Purchase(
                        transaction.Date,
                        currency,
                        transaction.Shares,
                        transaction.Amount,
                        transaction.Fees,
                        transaction.Taxes,
                        transaction.Note,
                    )
                transactions.append(bought)
            elif transaction.Type.lower() in [
                "sell",
                "delivery_outbound",
                "transfer_out",
            ]:
                transactions.append(
                    Sale(
                        transaction.Date,
                        currency,
                        transaction.Shares,
                        transaction.Amount,
                        transaction.Fees,
                        transaction.Taxes,
                        transaction.Note,
                    )
                )
            elif (
                transaction.Note
                and str(transaction.Note).lower() == "excess reportable income"
            ):
                # The date here is the ERI distribution date
                transactions.append(
                    ExcessReportableIncome(
                        transaction.Date,
                        currency,
                        transaction.Shares,
                        transaction.Amount,
                    )
                )
            elif transaction.Type.lower() in ["dividend", "dividends"]:
                if not (
                    transaction.Note
                    and str(transaction.Note).lower() == "scrip dividend"
                ):
                    transactions.append(
                        Dividend(
                            transaction.Date,
                            currency,
                            transaction.Shares,
                            transaction.Amount,
                            transaction.Fees,
                            transaction.Taxes,
                            transaction.Note,
                        )
                    )
            elif transaction.Type.lower() in [
                "fees refund",
                "fees_refund",
            ]:
                pass
            else:
                msg = f"Unknown transaction!\n{transaction}"
                raise TypeError(msg)
        return transactions
