import collections
from datetime import datetime
from unittest import mock

import pytest

from booli_crawler.sold_listings import PagesNotUnique, PagesExceedsMax
from booli_crawler.sold_listings import get as sold_listings_get
from booli_crawler.types import City, SoldListing
from .common import RESOURCES_ROOT
from .mock_response import MockResponse

RESOURCE_BOOLI_PAGE = RESOURCES_ROOT / 'booli_slutpriser_linkoping.html'
RESOURCE_BOOLI_CITY = City.Linkoping
RESOURCE_BOOLI_MIN_DATE_SOLD = datetime.strptime("2023-06-20", '%Y-%m-%d')
RESOURCE_BOOLI_MAX_DATE_SOLD = datetime.strptime("2023-06-27", '%Y-%m-%d')

TEST_CACHE_NAME = "test_cache"

LISTINGS_EXP_SHAPE = (35, 8)

LocalResponse = collections.namedtuple('LocalResponse', ['sold_listings_get', 'mocked_requests_get'])


@pytest.fixture
def local_response():
    with mock.patch('requests.get') as mocked_requests_get:
        with open(RESOURCE_BOOLI_PAGE, mode='rb') as f:
            mocked_requests_get.return_value = MockResponse(content=f.read())
            yield LocalResponse(sold_listings_get, mocked_requests_get)


@pytest.fixture
def tmp_cache_path(tmp_path):
    yield tmp_path / TEST_CACHE_NAME


def assert_listings_integrity(listings):
    for member in SoldListing.__annotations__:
        assert not getattr(listings, member).isna().values.all()

    assert listings.shape == LISTINGS_EXP_SHAPE


def test_get_with_local_response(local_response):
    listings = local_response.sold_listings_get(city=RESOURCE_BOOLI_CITY, use_cache=False)

    assert_listings_integrity(listings)


def test_get_with_remote_response():
    listings = sold_listings_get(city=City.Linkoping, pages=[1], use_cache=False)

    assert_listings_integrity(listings)


def test_get_with_cache_assert_calls_to_requests(local_response, tmp_cache_path):
    local_response.sold_listings_get(city=RESOURCE_BOOLI_CITY,
                                     use_cache=True,
                                     cache_path=tmp_cache_path,
                                     from_date_sold=RESOURCE_BOOLI_MIN_DATE_SOLD,
                                     to_date_sold=RESOURCE_BOOLI_MAX_DATE_SOLD)

    requests_get_call_count = local_response.mocked_requests_get.call_count

    local_response.sold_listings_get(city=RESOURCE_BOOLI_CITY,
                                     use_cache=True,
                                     cache_path=tmp_cache_path,
                                     from_date_sold=RESOURCE_BOOLI_MIN_DATE_SOLD,
                                     to_date_sold=RESOURCE_BOOLI_MAX_DATE_SOLD)

    assert local_response.mocked_requests_get.call_count == requests_get_call_count


def test_get_with_cache_date_sold_broad_to_narrow_and_back(local_response, tmp_cache_path):
    sold_listings_broad = local_response.sold_listings_get(city=RESOURCE_BOOLI_CITY,
                                                           use_cache=True,
                                                           cache_path=tmp_cache_path,
                                                           from_date_sold=RESOURCE_BOOLI_MIN_DATE_SOLD,
                                                           to_date_sold=RESOURCE_BOOLI_MAX_DATE_SOLD)

    assert min(sold_listings_broad.date_sold) == RESOURCE_BOOLI_MIN_DATE_SOLD
    assert max(sold_listings_broad.date_sold) == RESOURCE_BOOLI_MAX_DATE_SOLD
    requests_get_call_count = local_response.mocked_requests_get.call_count

    sold_listings_narrow = local_response.sold_listings_get(city=RESOURCE_BOOLI_CITY,
                                                            use_cache=True,
                                                            cache_path=tmp_cache_path,
                                                            from_date_sold=RESOURCE_BOOLI_MIN_DATE_SOLD,
                                                            to_date_sold=RESOURCE_BOOLI_MIN_DATE_SOLD)

    assert min(sold_listings_narrow.date_sold) == RESOURCE_BOOLI_MIN_DATE_SOLD
    assert max(sold_listings_narrow.date_sold) == RESOURCE_BOOLI_MIN_DATE_SOLD
    assert local_response.mocked_requests_get.call_count == requests_get_call_count

    sold_listings_broad = local_response.sold_listings_get(city=RESOURCE_BOOLI_CITY,
                                                           use_cache=True,
                                                           cache_path=tmp_cache_path,
                                                           from_date_sold=RESOURCE_BOOLI_MIN_DATE_SOLD,
                                                           to_date_sold=RESOURCE_BOOLI_MAX_DATE_SOLD)

    assert min(sold_listings_broad.date_sold) == RESOURCE_BOOLI_MIN_DATE_SOLD
    assert max(sold_listings_broad.date_sold) == RESOURCE_BOOLI_MAX_DATE_SOLD
    assert local_response.mocked_requests_get.call_count == requests_get_call_count


def test_get_pages_not_unique(local_response):
    with pytest.raises(PagesNotUnique):
        local_response.sold_listings_get(city=RESOURCE_BOOLI_CITY, use_cache=False, pages=[1, 2, 3, 3])


def test_get_pages_exceeds_max(local_response):
    with pytest.raises(PagesExceedsMax):
        local_response.sold_listings_get(city=RESOURCE_BOOLI_CITY, use_cache=False, pages=[100_000])
