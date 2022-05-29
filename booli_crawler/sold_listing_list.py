from threading import Lock

import pandas as pd

from booli_crawler.types import SoldListing


class SoldListingList:

    def __init__(self):
        self._lock = Lock()
        self._members = SoldListing.__annotations__.keys()

        for member in self._members:
            setattr(self, member, [])

    def append(self, sold_listing: SoldListing):
        with self._lock:
            for member in self._members:
                new_value = getattr(sold_listing, member)
                values = getattr(self, member)

                values.append(new_value)

    def as_frame(self) -> pd.DataFrame:
        df = pd.DataFrame({key: getattr(self, key) for key in self._members})

        df.index = [pd.Timestamp(ds) for ds in df.date_sold]
        df = df.sort_index(ascending=False)

        return df
