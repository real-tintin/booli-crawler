import re
import time
from typing import Optional

import numpy as np
import pandas as pd
import requests
from tqdm import tqdm

from booli_crawler.crawler import Crawler
from booli_crawler.page_queue import PageQueue
from booli_crawler.sold_listing_list import SoldListingList
from booli_crawler.types import City
from booli_crawler.url import get_city_page_url


def get(city: City,
        max_pages: Optional[int] = None,
        n_crawlers: int = 1,
        show_progress_bar: bool = False) -> pd.DataFrame:
    """
    Crawls and returns the sold listings per page given
    a city.

    :param city: Selected city to crawl.
    :param max_pages: Limit pages to crawl.
    :param n_crawlers: Use to thread the crawling.
    :param show_progress_bar: Set true for progress bar.

    :return: Sold listings given the city.
    """
    if max_pages is None:
        n_pages = _find_n_pages(city)
    else:
        n_pages = min(max_pages, _find_n_pages(city))

    sold_listings = SoldListingList()
    page_queue = PageQueue(pages=list(range(1, n_pages + 1)))

    if show_progress_bar:
        progress_bar_cb = tqdm(total=n_pages, desc='Crawling booli').update
    else:
        progress_bar_cb = lambda: None

    crawlers = [Crawler(city=city,
                        page_queue=page_queue,
                        sold_listings=sold_listings,
                        page_parsed_cb=progress_bar_cb)
                for _ in range(n_crawlers)]

    for crawler in crawlers:
        crawler.start()

    while page_queue.empty() is not True:
        time.sleep(1)

    for crawler in crawlers:
        crawler.stop()

    return sold_listings.as_frame()


def _find_n_pages(city: City) -> int:
    """
    Find n pages given a city by parsing the listing
    index e.g., 'Visar <!-- -->35<!-- --> av <!-- -->27545'
    """
    response = requests.get(url=get_city_page_url(city=city, page=1))

    matches = re.search(r'Visar <!-- -->(\d+)<!-- --> av <!-- -->(\d+)', response.content.decode())

    listings_per_page = int(matches.group(1))
    n_listings = int(matches.group(2))

    if listings_per_page > 0:
        return int(np.ceil(n_listings / listings_per_page))
    else:
        return 0
