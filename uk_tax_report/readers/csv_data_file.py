"""Definition of the CsvReader class"""

import logging

import pandas as pd

from .data_file import DataFile

logger = logging.getLogger(__name__)


class CsvDataFile(DataFile):
    """Read a PortfolioPerformance CSV file"""

    def __init__(self, file_name: str):
        super().__init__()

        # Read all CSV entries with a valid symbol and security
        self.df_transactions = pd.read_csv(file_name).dropna(
            subset=["Symbol", "Security"]
        )

        # Set datatypes
        self.df_transactions["Date"] = pd.to_datetime(self.df_transactions["Date"])
        self.df_transactions["Shares"] = self.df_transactions["Shares"].str.replace(
            ",", ""
        )
        self.df_transactions["Amount"] = self.df_transactions["Amount"].str.replace(
            ",", ""
        )
        logger.debug("Processing %d transactions...", self.df_transactions.shape[0])
