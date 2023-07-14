from unittest import mock

import pytest

from booli_crawler.url import get_num_of_pages
from .mock_response import MockResponse

LISTING_INDEX_FORMAT = '<span>Visar sida <!-- -->{listings_per_page}<!-- --> av <!-- -->{n_listings}</span>'


@pytest.mark.parametrize("listings_per_page, n_listings, exp_n_pages", [
    (35, 27545, 787),
    (17, 17, 1),
    (0, 0, 0),
])
def test_get_num_of_pages(listings_per_page, n_listings, exp_n_pages):
    content = LISTING_INDEX_FORMAT.format(listings_per_page=listings_per_page,
                                          n_listings=n_listings)

    with mock.patch('requests.get', return_value=MockResponse(content=content.encode())):
        assert get_num_of_pages(url='not/used') == exp_n_pages
