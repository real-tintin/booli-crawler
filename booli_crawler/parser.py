import re
from datetime import datetime
from typing import Optional, Dict

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

    def parse_listing(self, listing: Dict) -> SoldListing:
        return SoldListing(
            price_sek=listing['soldPrice']['raw'],

            property_type=self._parse_property_type(listing['objectType']),

            rooms=self._parse_rooms(listing['rooms']),
            area_m2=self._parse_area_m2(listing['livingArea']),

            street=listing['streetAddress'],
            district=listing['descriptiveAreaName'],

            date_sold=datetime.strptime(listing['soldDate'], '%Y-%m-%d'),

            url=BASE_URL + listing['url']
        )

    @staticmethod
    def _parse_property_type(property_type: str) -> PropertyType:
        try:
            if property_type in PROPERTY_TYPE_MAP:
                return PROPERTY_TYPE_MAP[property_type]
            else:
                return PropertyType.Unknown
        except:
            return PropertyType.Unknown

    @staticmethod
    def _parse_rooms(rooms: Dict) -> Optional[int]:
        """
        Expected format: '3 rum' or other
        delimiter e.g., '1\xa0rum'
        """
        try:
            rooms_as_str = rooms['formatted'].replace("½", ".5")
            rooms_as_int = int(re.findall(r'(\d+).rum', rooms_as_str)[0])

            return rooms_as_int
        except:
            return None

    @staticmethod
    def _parse_area_m2(area: Dict) -> Optional[float]:
        """
        Expected format: '80½ m²' or '125 m²' or other
        delimiter e.g., '48\xa0m²'
        """
        try:
            area_as_str = area['formatted'].replace("½", ".5")
            area_as_float = float(re.findall(r'(\d+\.?\d+).m²', area_as_str)[0])

            return area_as_float
        except:
            return None
