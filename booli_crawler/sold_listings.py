import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from threading import Lock
from typing import Callable
from typing import Optional

import bs4.element
import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

BASE_URL = "https://www.booli.se"
SOLD_LISTINGS_URL = BASE_URL + "/slutpriser/{city_name}/{city_code}?page={page}"


class City(Enum):
    Stockholm = 1
    Linkoping = 393


class PropertyType(Enum):
    Vila = 0
    Apartment = 1
    TownHouse = 2
    SemiDetachedHouse = 3
    HolidayHCottage = 4
    Ranch = 5
    Land = 6
    Unknown = 7


@dataclass
class SoldListing:
    price_sek: int

    property_type: PropertyType

    rooms: int
    area_m2: float

    street: str
    district: str

    date_sold: datetime

    href: str


class SoldListings:

    def __init__(self):
        self._lock = Lock()
        self._members = SoldListing.__annotations__.keys()

        for member in self._members:
            setattr(self, member, [])

    def append(self, sold_listing: SoldListing):
        with self._lock:
            for member in self._members:
                new_value = getattr(sold_listing, member)
                values = getattr(self, member)

                values.append(new_value)

    def as_frame(self) -> pd.DataFrame:
        return pd.DataFrame({key: getattr(self, key) for key in self._members})


class Parser:

    def __init__(self):
        pass

    def parse_listing(self, listing: bs4.element.Tag) -> SoldListing:
        return SoldListing(
            price_sek=self._parse_price_sek(lambda: listing.contents[2].contents[0].contents[0]),

            property_type=self._parse_property_type(lambda: listing.contents[1].contents[2].contents[0]),

            rooms=self._parse_rooms(lambda: listing.contents[1].contents[1].contents[0]),
            area_m2=self._parse_area_m2(lambda: listing.contents[1].contents[1].contents[0]),

            street=self._parse_street(lambda: listing.contents[1].contents[0].contents[0]),
            district=self._parse_district(lambda: listing.contents[1].contents[2].contents[0]),

            date_sold=self._parse_date_sold(lambda: listing.contents[2].contents[2].contents[0]),

            href=BASE_URL + listing.attrs['href']
        )

    @staticmethod
    def _parse_price_sek(content_cb: Callable[[], str]) -> Optional[int]:
        """
        Expected format: '1 670 000 kr'
        """
        try:
            content = content_cb().replace(" ", "")

            start_idx = 0
            end_idx = content.find('kr')

            return int(content[start_idx:end_idx])
        except:
            return None

    @staticmethod
    def _parse_property_type(content_cb: Callable[[], str]) -> PropertyType:
        """
        Expected format: 'Lägenhet, Linköpings Innerstad'
        """
        try:
            content = content_cb().replace(" ", "")

            end_idx = content.find(',')

            property_type_as_str = content[:end_idx]

            if property_type_as_str in PROPERTY_TYPE_MAP:
                return PROPERTY_TYPE_MAP[property_type_as_str]
            else:
                return PropertyType.Unknown

        except:
            return PropertyType.Unknown

    @staticmethod
    def _parse_street(content_cb: Callable[[], str]) -> Optional[str]:
        """
        Expected format: '2022-04-23'
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
            content = content_cb()

            start_idx = content.find(',') + 2

            return content[start_idx:]
        except:
            return None

    @staticmethod
    def _parse_rooms(content_cb: Callable[[], str]) -> Optional[int]:
        """
        Expected format: '3 rum, 80½ m²' or '125 m²'
        """
        try:
            content = content_cb().replace(" ", "")

            start_idx = 0
            end_idx = content.find('rum')

            return int(content[start_idx:end_idx])
        except:
            return None

    @staticmethod
    def _parse_area_m2(content_cb: Callable[[], str]) -> Optional[float]:
        """
        Expected format: '3 rum, 80½ m²' or '125 m²'
        """
        try:
            content = content_cb().replace(" ", "")
            content = content.replace("½", ".5")

            start_idx = content.find('rum,') + 4 if content.find('rum,') > -1 else 0
            end_idx = content.find('m²')

            return float(content[start_idx:end_idx])
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


PROPERTY_TYPE_MAP = {
    'Villa': PropertyType.Vila,
    'Hus': PropertyType.Vila,
    'Lägenhet': PropertyType.Apartment,
    'Radhus': PropertyType.TownHouse,
    'Kedjehus': PropertyType.TownHouse,
    'Parhus': PropertyType.SemiDetachedHouse,
    'Fritidshus': PropertyType.HolidayHCottage,
    'Gård': PropertyType.Ranch,
    'Tomt/Mark': PropertyType.Land,
}


def get_sold_listings(city: City, pages: int = 1, show_progress_bar=False) -> pd.DataFrame:
    # TODO: Find max pages e.g., "Här var det tomt"!
    # TODO: Parallelize the requests in threads/processes push to thread safe data container.
    parser = Parser()
    sold_listings = SoldListings()
    session = requests.Session()

    with tqdm(total=pages,
              desc='Crawling booli',
              disable=(not show_progress_bar)) as progress_bar:
        for page in range(0, pages + 1):
            response = session.get(url=SOLD_LISTINGS_URL.format(city_name=city.name.lower(),
                                                                city_code=city.value,
                                                                page=page))

            soup = BeautifulSoup(response.content, 'html.parser')
            listings = soup.find_all('a', {'href': re.compile(r'/bostad/')})

            for listing in listings:
                sold_listings.append(parser.parse_listing(listing))

            progress_bar.update()

    return sold_listings.as_frame()
