import json
import logging
import queue
import re
import threading
import time
from http import HTTPStatus
from typing import Callable, Dict, List

import bs4
import requests

from booli_crawler.parser import Parser
from booli_crawler.sold_listing_list import SoldListingList
from booli_crawler.url import UrlQueue

ONE_MS_IN_S = 0.001

TOO_MANY_REQUESTS_BACKOFF_FACTOR = 1.3

logger = logging.getLogger(__name__)


class Crawler:

    def __init__(self,
                 parser: Parser,
                 url_queue: UrlQueue,
                 sold_listings: SoldListingList,
                 page_crawled_cb: Callable):
        """
        Crawls through sold listings given by urls in the
        queue. Appends listings to sold_listings.

        Calls page_crawled_cb every time a new pages has
        been parsed.
        """
        self._url_queue = url_queue
        self._sold_listings = sold_listings
        self._page_crawled_cb = page_crawled_cb
        self._parser = parser

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
                url = self._url_queue.get(block=False)
            except queue.Empty:
                url = None

            if url is not None:
                response = self._request_with_retry(url=url)

                soup = bs4.BeautifulSoup(response.content, 'html.parser')

                page_data_raw = soup.find(name='script', attrs={'id': re.compile(r'__NEXT_DATA__')})
                page_data_json = json.loads(page_data_raw.string)

                listings = self._find_listings(page_data_json)

                for listing in listings:
                    self._sold_listings.append(self._parser.parse_listing(listing))

                self._page_crawled_cb()
            else:
                time.sleep(ONE_MS_IN_S)

    def _find_listings(self, data: Dict, found_listings: List[Dict] = None) -> List[Dict]:
        if found_listings is None:
            found_listings = []

        regexp = re.compile(r'SoldProperty:\d+')

        for key in data.keys():
            if regexp.search(key):
                found_listings.append(data[key])
            elif isinstance(data[key], Dict):
                self._find_listings(data[key], found_listings)

        return found_listings

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
