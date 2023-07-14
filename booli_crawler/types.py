from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class City(Enum):
    Stockholm = 1
    Linkoping = 393


class PropertyType(Enum):
    Vila = 0
    Apartment = 1
    TownHouse = 2
    SemiDetachedHouse = 3
    HolidayCottage = 4
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

    url: str
