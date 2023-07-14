import pytest

from booli_crawler.parser import Parser, PropertyType


class TestParser:

    @staticmethod
    @pytest.mark.parametrize("formatted, exp", [
        ('Radhus', PropertyType.TownHouse),
        ('Lägenhet', PropertyType.Apartment),
        ('not valid', PropertyType.Unknown),
    ])
    def test_parse_property_type(formatted, exp):
        assert Parser._parse_property_type(formatted) == exp

    @staticmethod
    @pytest.mark.parametrize("formatted, exp", [
        ('3 rum, 80½ m²', 3),
        ('44 rum, 9 m²', 44),
        ('125 m²', None),
        (None, None),
    ])
    def test_parse_rooms(formatted, exp):
        assert Parser._parse_rooms({'formatted': formatted}) == exp

    @staticmethod
    @pytest.mark.parametrize("formatted, exp", [
        ('3 rum, 80½ m²', 80.5),
        ('125 m²', 125),
        ('pi m²', None),
        (None, None),
    ])
    def test_parse_area_m2(formatted, exp):
        assert Parser._parse_area_m2({'formatted': formatted}) == exp
