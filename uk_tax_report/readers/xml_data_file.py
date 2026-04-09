"""Definition of the XmlDataFile class."""

import logging

import pandas as pd

from .data_file import DataFile
from .xml_utils import read_xml

logger = logging.getLogger(__name__)


class XmlDataFile(DataFile):
    """Read a PortfolioPerformance XML file."""

    def __init__(self, file_name: str):
        """Create an XmlDataFile."""
        super().__init__()

        # Read all XML entries with a valid symbol and security
        self.df_transactions = read_xml(file_name).dropna(subset=["Security"])

        # Set datatypes
        self.df_transactions["Date"] = pd.to_datetime(self.df_transactions["Date"])
        logger.debug("Processing %d transactions...", self.df_transactions.shape[0])
