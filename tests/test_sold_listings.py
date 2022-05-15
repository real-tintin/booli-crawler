from dataclasses import dataclass
from unittest import mock

import pytest
from requests import Session

from booli_crawler import sold_listings
from booli_crawler.types import City

RESOURCE_BOOL_PAGE = './resources/booli_slutpriser_linkoping.html'

LISTING_INDEX_FORMAT = '<span>Visar <!-- -->{listings_per_page}<!-- --> av <!-- -->{n_listings}</span>'
DUMMY_CITY = City.Stockholm


@dataclass
class MockResponse:
    content: bytes


@mock.patch.object(Session, 'get')
def test_get(mock_get):
    with open(RESOURCE_BOOL_PAGE, mode='rb') as f:
        mock_get.return_value = MockResponse(content=f.read())

    listings = sold_listings.get(city=City.Linkoping, max_pages=1, n_crawlers=1)

    assert listings.shape == (22, 8)


@pytest.mark.parametrize("listings_per_page, n_listings, exp_n_pages", [
    (35, 27545, 787),
    (17, 17, 1),
    (0, 0, 0),
])
def test_find_n_pages(listings_per_page, n_listings, exp_n_pages):
    content = LISTING_INDEX_FORMAT.format(listings_per_page=listings_per_page,
                                          n_listings=n_listings)

    with mock.patch('requests.get', return_value=MockResponse(content=content.encode())):
        assert sold_listings._find_n_pages(city=DUMMY_CITY) == exp_n_pages
