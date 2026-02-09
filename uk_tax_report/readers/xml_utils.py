"""Utility functions for reading PortfolioPerformance XML files"""

import re
import xml.etree.ElementTree as ET
from collections.abc import Iterable
from contextlib import suppress
from decimal import Decimal
from typing import Optional

import pandas as pd
from defusedxml.ElementTree import parse


def get_accounts(root: ET.Element) -> pd.DataFrame:
    """Get accounts"""
    accounts = []
    for account in (
        root.findall("*//account[uuid]")
        + root.findall("*//accountFrom[uuid]")
        + root.findall("*//accountTo[uuid]")
    ):
        name = get_first(account, "name")
        uuid = get_first(account, "uuid")
        accounts.append({"id": name, "uuid": uuid})
    return pd.DataFrame(accounts).drop_duplicates()


def get_first(node: ET.Element, match: str) -> Optional[str]:
    """Get the full text from the first node containing the requested string"""
    for element in node.findall(match):
        if element.text is not None:
            return element.text
    return None


def get_securities(root: ET.Element):
    """Get securities"""
    securities = []
    for security in iterate_elements(root.findall("securities")):
        if (name := get_first(security, "name")) is None:
            continue
        uuid = get_first(security, "uuid")
        isin = get_first(security, "isin")
        ticker_symbol = get_first(security, "tickerSymbol")
        currency_code = get_first(security, "currencyCode")
        note = get_first(security, "note")
        securities.append(
            {
                "id": name,
                "uuid": uuid,
                "ISIN": isin,
                "Symbol": ticker_symbol,
                "currencyCode": currency_code,
                "note": note,
            }
        )
    return pd.DataFrame(securities).drop_duplicates()


def get_transactions(root: ET.Element, account_id, df_securities):
    """Get transactions"""
    transactions = []
    for transaction in (
        root.findall(
            f"*//account[name='{account_id}']/transactions/account-transaction"
        )
        + root.findall(
            f"*//accountFrom[name='{account_id}']/transactions/account-transaction"
        )
        + root.findall(
            f"*//accountTo[name='{account_id}']/transactions/account-transaction"
        )
        + root.findall(
            f"*//portfolio[name='{account_id}']/transactions/portfolio-transaction"
        )
    ):
        if s_shares := get_first(transaction, "shares") is None:
            continue
        if s_total := get_first(transaction, "amount") is None:
            continue
        date = get_first(transaction, "date")
        shares = Decimal(s_shares) / 100000000
        type_ = get_first(transaction, "type")
        security_id = ref2name(transaction, df_securities)
        fees, taxes = 0, 0
        for charge in transaction.findall("./units/unit"):
            if charge.attrib["type"] == "FEE":
                fees += (
                    Decimal(
                        [c for c in charge if c.tag == "amount"][0].attrib["amount"]
                    )
                    / 100
                )
            if charge.attrib["type"] == "TAX":
                taxes += (
                    Decimal(
                        [c for c in charge if c.tag == "amount"][0].attrib["amount"]
                    )
                    / 100
                )
        total = Decimal(s_total) / 100  # this includes fees and taxes
        if type_ == "BUY":
            total -= fees + taxes
        else:
            total += fees + taxes
        note = get_first(transaction, "note") or ""
        if security_id:
            transactions.append(
                {
                    "Date": date,
                    "Type": type_,
                    "Security": security_id,
                    "Shares": shares,
                    "Amount": abs(total),
                    "Fees": abs(fees),
                    "Taxes": abs(taxes),
                    "Cash Account": account_id,
                    "Note": note,
                }
            )
    return pd.DataFrame(transactions).drop_duplicates()


def iterate_elements(element_list: list[ET.Element]) -> Iterable[ET.Element]:
    """Iterate through a list of XML elements, yielding all sub-elements"""
    for element in element_list:
        yield from element


def read_xml(file_name: str) -> pd.DataFrame:
    """Read a PortfolioPerformance XML file into a Pandas dataframe"""
    # Read all XML entries with a valid symbol and security
    tree = parse(file_name)
    if (root := tree.getroot()) is None:
        msg = f"Could not read XML file {file_name}"
        raise OSError(msg)

    # Read securities, accounts and transactions and set datatypes
    df_securities = get_securities(root)
    df_accounts = get_accounts(root)
    df_transactions = pd.concat(
        [
            get_transactions(root, account_name, df_securities)
            for account_name in df_accounts["id"].unique()
        ]
    )

    # Merge transactions with securities, dropping invalid rows
    df_all = pd.merge(
        df_transactions, df_securities, how="outer", left_on="Security", right_on="id"
    )
    return df_all


def ref2name(transaction: ET.Element, df_securities: pd.DataFrame) -> Optional[str]:
    """Find the security name corresponding to a given reference"""
    index = None
    if not (
        references := [
            elem.attrib["reference"] for elem in transaction.findall("security")
        ]
    ):
        return None
    if references[0].endswith("securities/security"):
        index = 0
    else:
        regex_ = r".*/security\[(\d+)\]"
        if result := re.search(regex_, references[0], re.IGNORECASE):
            index = int(result.group(1)) - 1
    if index is not None:
        with suppress(IndexError, AttributeError):
            return df_securities.iloc[index]["id"]
    return None
