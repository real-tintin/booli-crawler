import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Callable

import pandas as pd
from tqdm import tqdm

from booli_crawler.crawler import Crawler
from booli_crawler.parser import Parser
from booli_crawler.sold_listing_list import SoldListingList
from booli_crawler.types import City
from booli_crawler.url import get_page_url, UrlQueue, Url, get_num_of_pages

SLEEP_CHECK_QUEUE_S = 1

DEFAULT_CACHE_PATH = Path.home() / ".booli_crawler_cache"

DATETIME_ONE_DAY = timedelta(days=1)

Pages = List[int]
Urls = List[Url]

logger = logging.getLogger(__name__)


class PagesNotUnique(Exception):
    """Raised when pages are not unique"""
    pass


class PagesExceedsMax(Exception):
    """Raised when max of pages exceeds number of available pages"""
    pass


def get(city: City,
        from_date_sold: Optional[datetime] = datetime.fromtimestamp(0),
        to_date_sold: Optional[datetime] = datetime.now(),
        pages: Optional[Pages] = None,
        n_crawlers: int = 1,
        use_cache: bool = True,
        cache_path: Path = DEFAULT_CACHE_PATH,
        show_progress_bar: bool = False) -> pd.DataFrame:
    """
    Crawls and returns the sold listings per page given
    a city.

    :param city: Selected city to crawl.
    :param from_date_sold: From date sold to crawl.
    :param to_date_sold: To date sold to crawl.
    :param pages: Explicitly defines pages to parse, between dates sold.
    :param n_crawlers: Use to thread the crawling.
    :param use_cache: Enable to use cache between calls.
    :param cache_path: Path to where the cache is/will be stored.
    :param show_progress_bar: Set true for progress bar.

    :return: Sold listings given the city.
    """
    parser = Parser()
    sold_listings = SoldListingList()

    if use_cache:
        if cache_path.exists():
            logger.debug(f"Cache found at {cache_path}, loading")
            sold_listings.from_file(path=cache_path)
        else:
            logger.debug(f"No cache found at {cache_path}")
    else:
        logger.debug("Skipping caching, not requested")

    url_queue = UrlQueue(urls=_get_urls_based_on_date_sold(city=city,
                                                           from_date_sold=from_date_sold,
                                                           to_date_sold=to_date_sold,
                                                           pages=pages,
                                                           cached_date_sold=sold_listings.date_sold))

    if show_progress_bar:
        progress_bar_cb = tqdm(total=url_queue.qsize(), desc='Crawling booli').update
    else:
        progress_bar_cb = lambda: None

    _crawl_pages(parser=parser,
                 sold_listings=sold_listings,
                 url_queue=url_queue,
                 n_crawlers=n_crawlers,
                 page_crawled_cb=progress_bar_cb)

    if use_cache:
        logger.debug(f"Storing cache to {cache_path}")
        sold_listings.to_file(path=cache_path)

        return _to_pd_frame_and_filter_on_date_sold(sold_listings=sold_listings,
                                                    from_date_sold=from_date_sold,
                                                    to_date_sold=to_date_sold)
    else:
        return sold_listings.to_pd_frame()


def _get_urls_based_on_date_sold(city: City,
                                 from_date_sold: datetime,
                                 to_date_sold: datetime,
                                 pages: List[int],
                                 cached_date_sold: List[datetime]) -> Urls:
    urls = []

    if cached_date_sold:
        if from_date_sold < min(cached_date_sold):
            urls += _get_urls(city=city,
                              from_date_sold=from_date_sold,
                              to_date_sold=min(cached_date_sold),
                              pages=pages)

        if to_date_sold > max(cached_date_sold):
            urls += _get_urls(city=city,
                              from_date_sold=max(cached_date_sold),
                              to_date_sold=to_date_sold,
                              pages=pages)
    else:
        urls += _get_urls(city=city,
                          from_date_sold=from_date_sold,
                          to_date_sold=to_date_sold,
                          pages=pages)

    return urls


def _to_pd_frame_and_filter_on_date_sold(sold_listings: SoldListingList,
                                         from_date_sold: datetime,
                                         to_date_sold: datetime) -> pd.DataFrame:
    pd_frame = sold_listings.to_pd_frame()
    use_indices = (from_date_sold <= pd_frame.date_sold) & (pd_frame.date_sold <= to_date_sold)

    return pd_frame[use_indices]


def _crawl_pages(parser: Parser,
                 sold_listings: SoldListingList,
                 url_queue: UrlQueue,
                 n_crawlers: int,
                 page_crawled_cb: Callable) -> SoldListingList:
    crawlers = [Crawler(parser=parser,
                        url_queue=url_queue,
                        sold_listings=sold_listings,
                        page_crawled_cb=page_crawled_cb)
                for _ in range(n_crawlers)]

    for crawler in crawlers:
        crawler.start()

    while not url_queue.empty():
        time.sleep(SLEEP_CHECK_QUEUE_S)

    for crawler in crawlers:
        crawler.stop()

    return sold_listings


def _get_urls(city: City,
              from_date_sold: datetime,
              to_date_sold: datetime,
              pages: Optional[Pages]) -> Urls:
    page_url = get_page_url(city=city,
                            from_date_sold=from_date_sold,
                            to_date_sold=to_date_sold)

    n_pages = get_num_of_pages(url=page_url(page=1))

    if pages is None:
        pages = range(1, n_pages + 1)

    if len(pages) > len(set(pages)):
        raise PagesNotUnique

    if n_pages < max(pages):
        raise PagesExceedsMax

    return [page_url(page=page) for page in pages]
