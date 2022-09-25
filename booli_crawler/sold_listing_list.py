import pickle
import sys
from pathlib import Path
from threading import Lock
from typing import Dict, Any, IO

import pandas as pd

from booli_crawler.types import SoldListing

LARGE_RECURSION_LIMIT = 1000_000


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

    def to_file(self, path: Path):
        with open(path, mode="wb") as file:
            self._pickle_dump_with_large_recursion_limit(self._to_dict(), file)

    def from_file(self, path: Path):
        with open(path, mode="rb") as file:
            self._from_dict(pickle.load(file))

    def to_pd_frame(self) -> pd.DataFrame:
        df = pd.DataFrame(self._to_dict())

        df.index = [pd.Timestamp(ds) for ds in df.date_sold]
        df = df.sort_index(ascending=False)

        return df

    def _to_dict(self) -> Dict:
        return {key: getattr(self, key) for key in self._members}

    def _from_dict(self, sold_listings: Dict):
        for member in self._members:
            values = sold_listings.get(member)
            setattr(self, member, values)

    @staticmethod
    def _pickle_dump_with_large_recursion_limit(data: Any, file: IO):
        default_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(LARGE_RECURSION_LIMIT)

        pickle.dump(data, file)

        sys.setrecursionlimit(default_limit)
