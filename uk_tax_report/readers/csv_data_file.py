"""Definition of the CsvReader class"""

# Standard library imports
import logging

# Third-party imports
import pandas as pd

# Local imports
from .data_file import DataFile


class CsvDataFile(DataFile):
    """Read a PortfolioPerformance CSV file"""

    def __init__(self, file_name: str):
        super().__init__()

        # Read all CSV entries with a valid symbol and security
        self.df_transactions = pd.read_csv(file_name)
        self.df_transactions.dropna(subset=["Symbol", "Security"], inplace=True)

        # Set datatypes
        self.df_transactions["Date"] = pd.to_datetime(self.df_transactions["Date"])
        self.df_transactions["Shares"] = self.df_transactions["Shares"].str.replace(
            ",", ""
        )
        self.df_transactions["Amount"] = self.df_transactions["Amount"].str.replace(
            ",", ""
        )
        logging.debug(f"Processing {self.df_transactions.shape[0]} transactions...")
