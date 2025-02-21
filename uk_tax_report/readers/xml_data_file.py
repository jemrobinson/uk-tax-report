"""Definition of the XmlReader class"""

# Standard library imports
import logging

# Third-party imports
import pandas as pd

# Local imports
from .data_file import DataFile
from .xml_utils import read_xml


class XmlDataFile(DataFile):
    """Read a PortfolioPerformance XML file"""

    def __init__(self, file_name: str):
        super().__init__()

        # Read all XML entries with a valid symbol and security
        self.df_transactions = read_xml(file_name)
        self.df_transactions.dropna(subset=["Security"], inplace=True)

        # Set datatypes
        self.df_transactions["Date"] = pd.to_datetime(self.df_transactions["Date"])
        logging.debug(f"Processing {self.df_transactions.shape[0]} transactions...")
