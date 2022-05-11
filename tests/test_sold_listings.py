from dataclasses import dataclass
from datetime import datetime
from unittest import mock

import pytest
from requests import Session

from booli_crawler.sold_listings import get_sold_listings, City, PropertyType, Parser

RESOURCE_BOOL_PAGE = './resources/booli_slutpriser_linkoping.html'


@dataclass
class MockResponse:
    content: bytes


@mock.patch.object(Session, 'get')
def test_get_sold_listings(mock_get):
    with open(RESOURCE_BOOL_PAGE, mode='rb') as f:
        mock_get.return_value = MockResponse(content=f.read())

    listings = get_sold_listings(city=City.Linkoping)

    assert listings.shape == (44, 8)


class TestParser:

    @staticmethod
    @pytest.mark.parametrize("content, exp", [
        ('1 670 000 kr', 1670000),
        ('not valid', None),
        (None, None),
    ])
    def test_parse_price_sek(content, exp):
        assert Parser._parse_price_sek(lambda: content) == exp

    @staticmethod
    @pytest.mark.parametrize("content, exp", [
        ('Lägenhet, Linköpings Innerstad', PropertyType.Apartment),
        ('not valid', PropertyType.Unknown),
    ])
    def test_parse_property_type(content, exp):
        assert Parser._parse_property_type(lambda: content) == exp

    @staticmethod
    @pytest.mark.parametrize("content, exp", [
        ('Lägenhet, Linköpings Innerstad', 'Linköpings Innerstad'),
        ('Something, This is valid', 'This is valid'),
        (None, None),
    ])
    def test_parse_district(content, exp):
        assert Parser._parse_district(lambda: content) == exp

    @staticmethod
    @pytest.mark.parametrize("content, exp", [
        ('3 rum, 80½ m²', 3),
        ('125 m²', None),
        (None, None),
    ])
    def test_parse_district(content, exp):
        assert Parser._parse_rooms(lambda: content) == exp

    @staticmethod
    @pytest.mark.parametrize("content, exp", [
        ('3 rum, 80½ m²', 80.5),
        ('125 m²', 125),
        ('pi m²', None),
        (None, None),
    ])
    def test_parse_district(content, exp):
        assert Parser._parse_area_m2(lambda: content) == exp

    @staticmethod
    @pytest.mark.parametrize("content, exp", [
        ('2022-04-23', datetime.strptime('2022-04-23', '%Y-%m-%d')),
        ('not a valid date', None),
        (None, None),
    ])
    def test_parse_district(content, exp):
        assert Parser._parse_date_sold(lambda: content) == exp

    @staticmethod
    @pytest.mark.parametrize("content, exp", [
        ('This is a street', 'This is a street'),
        ('', ''),
        (None, None),
    ])
    def test_parse_street(content, exp):
        assert Parser._parse_street(lambda: content) == exp
