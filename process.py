#! /usr/bin/env python
"""Process CSV files generated by Portfolio Performance using: All transactions > Export"""
# Standard library imports
import logging
from argparse import ArgumentParser
from datetime import date

# Third party imports
import pandas as pd

# Local imports
from uk_tax_report import Account, read_xml


def load_csv(file_name):
    # Read all CSV entries with a valid symbol and security
    df_transactions = pd.read_csv(file_name)
    df_transactions.dropna(subset=["Symbol", "Security"], inplace=True)

    # Set datatypes
    df_transactions["Date"] = pd.to_datetime(df_transactions["Date"])
    df_transactions["Shares"] = df_transactions["Shares"].str.replace(",", "")
    df_transactions["Amount"] = df_transactions["Amount"].str.replace(",", "")
    logging.debug(f"Processing {df_transactions.shape[0]} transactions...")

    return df_transactions


def load_xml(file_name):
    # Read all XML entries with a valid symbol and security
    df_transactions = read_xml(file_name)
    df_transactions.dropna(subset=["Symbol", "Security"], inplace=True)

    # Set datatypes
    df_transactions["Date"] = pd.to_datetime(df_transactions["Date"])
    logging.debug(f"Processing {df_transactions.shape[0]} transactions...")

    return df_transactions


if __name__ == "__main__":
    # Parse command line arguments
    parser = ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-c", "--csv", type=str, help="CSV file to process")
    group.add_argument("-x", "--xml", type=str, help="XML file to process")
    parser.add_argument(
        "-t",
        "--tax-year",
        metavar="N",
        type=str,
        help="tax year to consider [either YYYY-YY or YYYY-YYYY]",
    )
    parser.add_argument(
        "-n", "--account-names", type=str, nargs="+", help="accounts to consider"
    )
    parser.add_argument(
        "-v", "--verbosity", action="count", default=0, help="increase output verbosity"
    )
    args = parser.parse_args()

    # Set up logging
    log_levels = [logging.INFO, logging.DEBUG]
    logging.basicConfig(
        format=r"%(asctime)s %(levelname)8s: %(message)s",
        datefmt=r"%Y-%m-%d %H:%M:%S",
        level=log_levels[min(len(log_levels) - 1, args.verbosity)],
    )

    # Set start and end dates
    try:
        start_date = date(int(args.tax_year.split("-")[0]), 4, 6)
        end_date = date(int(args.tax_year.split("-")[0]) + 1, 4, 5)
    except AttributeError:
        raise ValueError(
            "Could not interpret '%s' as a UK tax year!"
            % (args.tax_year if args.tax_year else "")
        ) from None
    logging.debug(f"Set start date ({start_date}) and end date ({end_date})")

    if args.csv:
        df_transactions = load_csv(args.csv)

    elif args.xml:
        df_transactions = load_xml(args.xml)

    # Load accounts
    accounts = [
        Account(account, df_transactions)
        for account in set(df_transactions["Cash Account"])
    ]

    # Generate reports
    for account in accounts:
        if (not args.account_names) or (account.name in args.account_names):
            account.report(start_date, end_date)
