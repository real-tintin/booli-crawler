import logging
import queue
import re
import threading
import time
from http import HTTPStatus
from typing import Callable

import bs4
import requests

from booli_crawler.page_queue import PageQueue
from booli_crawler.parser import Parser
from booli_crawler.sold_listing_list import SoldListingList
from booli_crawler.url import PageUrl

ONE_MS_IN_S = 0.001

TOO_MANY_REQUESTS_BACKOFF_FACTOR = 1.3

logger = logging.getLogger(__name__)


class Crawler:

    def __init__(self,
                 page_url: PageUrl,
                 page_queue: PageQueue,
                 sold_listings: SoldListingList,
                 page_crawled_cb: Callable):
        """
        Crawls through sold listings at pages given by the
        queue. Appends listings to sold_listings.

        Calls page_crawled_cb every time a new pages has
        been parsed.
        """
        self._page_queue = page_queue
        self._sold_listings = sold_listings
        self._page_url = page_url
        self._page_crawled_cb = page_crawled_cb

        self._parser = Parser()

        self._run = False
        self._thread = threading.Thread(target=self._exec)

    def stop(self):
        self._run = False
        self._thread.join()

    def start(self):
        self._run = True
        self._thread.start()

    def _exec(self):
        while self._run:
            try:
                page = self._page_queue.get(block=False)
            except queue.Empty:
                page = None

            if page is not None:
                response = self._request_with_retry(url=self._page_url(page=page))

                soup = bs4.BeautifulSoup(response.content, 'html.parser')
                listings = soup.find_all('a', {'href': re.compile(r'/bostad/|/annons/')})

                for listing in listings:
                    self._sold_listings.append(self._parser.parse_listing(listing))

                self._page_crawled_cb()
            else:
                time.sleep(ONE_MS_IN_S)

    @staticmethod
    def _request_with_retry(url):
        i_retry = 0
        response = requests.get(url=url)

        while response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            retry_after_s = int(response.headers["Retry-After"])
            sleep_s = retry_after_s * TOO_MANY_REQUESTS_BACKOFF_FACTOR ** i_retry

            logger.debug(f'{threading.get_native_id()}: Too many requests. Sleeping {sleep_s} s.')

            time.sleep(sleep_s)

            response = requests.get(url=url)
            i_retry += 1

        return response
