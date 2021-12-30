#! /usr/bin/env python
"""Process CSV files generated by File > Export > Account Transactions"""
from
from pandas import read_csv, to_datetime
from numpy import datetime64
from capital_gains_calculator import Security

def main():
    # file_name = "../2021-12-22_all_transactions.csv"
    # tax_year = "2020-21"
    # account_names = ["Direct", "HL Fund & Share"]

    start_date = datetime64(f"{tax_year.split('-')[0]}-04-06")
    end_date = datetime64(f"{int(tax_year.split('-')[0]) + 1}-04-05")

    # Read all CSV entries with a valid symbol and security
    df_all = read_csv(file_name)
    df_all.dropna(subset=["Symbol", "Security"], inplace=True)

    # Set datatypes
    df_all["Date"] = to_datetime(df_all["Date"])
    df_all["Shares"] = df_all["Shares"].str.replace(",", "")
    df_all["Amount"] = df_all["Amount"].str.replace(",", "")

    # Restrict to specified accounts
    df_all = df_all.loc[(df_all["Cash Account"].isin(account_names))]
    df_securities = df_all[["ISIN", "Symbol", "Security"]].drop_duplicates()

    for idx, transaction in df_securities.iterrows():
        security = Security(symbol=transaction[1], name=transaction[2])
        security.add_transactions(df_all.loc[(df_all["Security"] == security.name)])
        if any([start_date <= d.date <= end_date for d in security.disposals]):
            security.report()



if __name__ == "__main__":
parser = argparse.ArgumentParser()
parser.add_argument("square", type=int,
                    help="display a square of a given number")
parser.add_argument("-v", "--verbosity", action="count", default=0,
                    help="increase output verbosity")
args = parser.parse_args()

