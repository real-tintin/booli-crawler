import re
from datetime import datetime
from queue import Queue
from typing import Protocol

import numpy as np
import requests

from booli_crawler.types import City

BASE_URL = "https://www.booli.se"

SOLD_LISTINGS_URL = BASE_URL + "/slutpriser/{city_name}/{city_code}?" \
                               "maxSoldDate={to_date_sold}&" \
                               "minSoldDate={from_date_sold}&" \
                               "sort=soldDate" \
                               "&page={page}"

DATETIME_FORMAT = '%Y-%m-%d'

Url = str


class UrlQueue(Queue, object):

    def __init__(self, urls: [Url]):
        super(UrlQueue, self).__init__()

        for url in urls:
            self.put(url)


class PageUrl(Protocol):
    def __call__(self, page: int) -> str:
        pass


def get_page_url(city: City,
                 from_date_sold: datetime,
                 to_date_sold: datetime) -> PageUrl:
    """
    Creates and returns a callable (PageUrl) which in terms returns
    the url given a page number.
    """
    return lambda page: SOLD_LISTINGS_URL.format(city_name=city.name.lower(),
                                                 city_code=city.value,
                                                 page=page,
                                                 from_date_sold=from_date_sold.strftime(DATETIME_FORMAT),
                                                 to_date_sold=to_date_sold.strftime(DATETIME_FORMAT))


def get_num_of_pages(url: Url) -> int:
    """
    Find number of pages given the url by parsing the listing
    index e.g., 'Visar sida <!-- -->35<!-- --> av <!-- -->27545'
    """
    response = requests.get(url=url)

    matches = re.search(pattern=r'Visar sida <!-- -->(\d+)<!-- --> av <!-- -->(\d+)',
                        string=response.content.decode())

    listings_per_page = int(matches.group(1))
    n_listings = int(matches.group(2))

    if listings_per_page > 0:
        return int(np.ceil(n_listings / listings_per_page))
    else:
        return 0
