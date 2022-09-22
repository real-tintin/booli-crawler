from unittest import mock

from booli_crawler import sold_listings
from booli_crawler.types import City
from .common import RESOURCES_ROOT
from .mock_response import MockResponse

RESOURCE_BOOL_PAGE = RESOURCES_ROOT / 'booli_slutpriser_linkoping.html'

LISTING_INDEX_FORMAT = '<span>Visar <!-- -->{listings_per_page}<!-- --> av <!-- -->{n_listings}</span>'

LISTINGS_EXP_SHAPE = (35, 8)


@mock.patch('requests.get')
def test_get_with_mocked_response(mock_get):
    with open(RESOURCE_BOOL_PAGE, mode='rb') as f:
        mock_get.return_value = MockResponse(content=f.read())

    listings = sold_listings.get(city=City.Linkoping, n_crawlers=1)

    assert listings.isna().values.any() == False
    assert listings.shape == LISTINGS_EXP_SHAPE


def test_get_with_real_response():
    listings = sold_listings.get(city=City.Linkoping, pages=[1], n_crawlers=1)

    assert listings.isna().values.all() == False  # Somewhat relaxed since some filed can be NaN e.g., missing area.
    assert listings.shape == LISTINGS_EXP_SHAPE
