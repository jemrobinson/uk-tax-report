"""Definition of the ScripDividend class"""

from .purchase import Purchase


class ScripDividend(Purchase):
    """Transaction where security pays a dividend in the form of shares"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type: str = "Scrip dividend of"
