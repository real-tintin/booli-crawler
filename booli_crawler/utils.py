import re

import numpy as np
import requests

from booli_crawler.types import City


def get_num_of_pages(city: City, url: str) -> int:
    """
    Find number of pages given a city by parsing the listing
    index e.g., 'Visar <!-- -->35<!-- --> av <!-- -->27545'
    """
    response = requests.get(url=url)

    matches = re.search(pattern=r'Visar <!-- -->(\d+)<!-- --> av <!-- -->(\d+)',
                        string=response.content.decode())

    listings_per_page = int(matches.group(1))
    n_listings = int(matches.group(2))

    if listings_per_page > 0:
        return int(np.ceil(n_listings / listings_per_page))
    else:
        return 0
