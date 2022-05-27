import logging
import time
from datetime import datetime
from typing import Optional

import pandas as pd
from tqdm import tqdm

from booli_crawler.crawler import Crawler
from booli_crawler.page_queue import PageQueue
from booli_crawler.sold_listing_list import SoldListingList
from booli_crawler.types import City
from booli_crawler.url import get_page_url
from booli_crawler.utils import get_num_of_pages

SLEEP_CHECK_QUEUE_S = 1

logging.basicConfig(level=logging.INFO)


def get(city: City,
        from_date_sold: Optional[datetime] = None,
        to_date_sold: Optional[datetime] = None,
        n_crawlers: int = 1,
        show_progress_bar: bool = False,
        verbose: bool = False) -> pd.DataFrame:
    """
    Crawls and returns the sold listings per page given
    a city.

    :param city: Selected city to crawl.
    :param from_date_sold: From date sold to crawl.
    :param to_date_sold: To date sold to crawl.
    :param n_crawlers: Use to thread the crawling.
    :param show_progress_bar: Set true for progress bar.
    :param verbose: Be more verbose i.e., enable debug logging.

    :return: Sold listings given the city.
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    page_url_kwargs = {}

    if from_date_sold is not None:
        page_url_kwargs.update({'from_date_sold': from_date_sold})

    if to_date_sold is not None:
        page_url_kwargs.update({'to_date_sold': to_date_sold})

    page_url = get_page_url(city=city, **page_url_kwargs)

    num_of_pages = get_num_of_pages(city, url=page_url(page=1))
    pages = list(range(1, num_of_pages + 1))

    sold_listings = SoldListingList()
    page_queue = PageQueue(pages)

    if show_progress_bar:
        progress_bar_cb = tqdm(total=num_of_pages, desc='Crawling booli').update
    else:
        progress_bar_cb = lambda: None

    crawlers = [Crawler(city=city,
                        page_url=page_url,
                        page_queue=page_queue,
                        sold_listings=sold_listings,
                        page_crawled_cb=progress_bar_cb)
                for _ in range(n_crawlers)]

    for crawler in crawlers:
        crawler.start()

    while not page_queue.empty():
        time.sleep(SLEEP_CHECK_QUEUE_S)

    for crawler in crawlers:
        crawler.stop()

    return sold_listings.as_frame()
