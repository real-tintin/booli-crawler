import re
from datetime import datetime
from typing import Optional, Callable

import bs4

from booli_crawler.types import PropertyType, SoldListing
from booli_crawler.url import BASE_URL

PROPERTY_TYPE_MAP = {
    'Villa': PropertyType.Vila,
    'Hus': PropertyType.Vila,
    'Lägenhet': PropertyType.Apartment,
    'Radhus': PropertyType.TownHouse,
    'Kedjehus': PropertyType.TownHouse,
    'Parhus': PropertyType.SemiDetachedHouse,
    'Fritidshus': PropertyType.HolidayCottage,
    'Gård': PropertyType.Ranch,
    'Tomt/Mark': PropertyType.Land,
}


class Parser:

    def __init__(self):
        pass

    def parse_listing(self, listing: bs4.element.Tag) -> SoldListing:
        contents_of_interest = listing.contents[1].contents[0]

        return SoldListing(
            price_sek=self._parse_price_sek(lambda: contents_of_interest.contents[2].contents[0]),

            property_type=self._parse_property_type(lambda: contents_of_interest.contents[1].contents[0]),

            rooms=self._parse_rooms(lambda: contents_of_interest.contents[4].contents[0].contents[0]),
            area_m2=self._parse_area_m2(lambda: contents_of_interest.contents[4].contents[1].contents[0]),

            street=self._parse_street(lambda: contents_of_interest.contents[0].contents[0]),
            district=self._parse_district(lambda: contents_of_interest.contents[1].contents[0]),

            date_sold=self._parse_date_sold(lambda: contents_of_interest.contents[3].contents[0]),

            href=BASE_URL + listing.attrs['href']
        )

    @staticmethod
    def _parse_price_sek(content_cb: Callable[[], str]) -> Optional[int]:
        """
        Expected format: '1 670 000 kr'
        """
        try:
            matches = re.findall(r'(\d+)', content_cb())
            return int(''.join(matches))
        except:
            return None

    @staticmethod
    def _parse_property_type(content_cb: Callable[[], str]) -> PropertyType:
        """
        Expected format: 'Lägenhet, Linköpings Innerstad'
        """
        try:
            property_type_as_str = re.findall(r'(.*), ', content_cb())[0]

            if property_type_as_str in PROPERTY_TYPE_MAP:
                return PROPERTY_TYPE_MAP[property_type_as_str]
            else:
                return PropertyType.Unknown

        except:
            return PropertyType.Unknown

    @staticmethod
    def _parse_street(content_cb: Callable[[], str]) -> Optional[str]:
        """
        Expected format: 'Ågatan 1'
        """
        try:
            return content_cb()
        except:
            return None

    @staticmethod
    def _parse_district(content_cb: Callable[[], str]) -> Optional[str]:
        """
        Expected format: 'Lägenhet, Linköpings Innerstad'
        """
        try:
            return re.findall(r', (.*)', content_cb())[0]
        except:
            return None

    @staticmethod
    def _parse_rooms(content_cb: Callable[[], str]) -> Optional[int]:
        """
        Expected format: '3 rum, 80½ m²' or '125 m²'
        """
        try:
            content = content_cb().replace("½", ".5")
            return int(re.findall(r'(\d+) rum', content)[0])
        except:
            return None

    @staticmethod
    def _parse_area_m2(content_cb: Callable[[], str]) -> Optional[float]:
        """
        Expected format: '3 rum, 80½ m²' or '125 m²'
        """
        try:
            content = content_cb().replace("½", ".5")
            return float(re.findall(r'(\d+\.?\d+) m²', content)[0])
        except:
            return None

    @staticmethod
    def _parse_date_sold(content_cb: Callable[[], str]) -> Optional[datetime]:
        """
        Expected format: '2022-04-23'
        """
        try:
            return datetime.strptime(content_cb(), '%Y-%m-%d')
        except:
            return None
