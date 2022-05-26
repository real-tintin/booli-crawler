from datetime import datetime
from typing import Optional, Protocol

from booli_crawler.types import City

BASE_URL = "https://www.booli.se"

SOLD_LISTINGS_URL = BASE_URL + "/slutpriser/{city_name}/{city_code}?" \
                               "maxSoldDate={to_date_sold}&" \
                               "minSoldDate={from_date_sold}&" \
                               "sort=soldDate" \
                               "&page={page}"

DATETIME_FORMAT = '%Y-%m-%d'


class PageUrl(Protocol):
    def __call__(self, page: int) -> str:
        pass


def get_page_url(city: City,
                 from_date_sold: Optional[datetime] = datetime.fromtimestamp(0),
                 to_date_sold: Optional[datetime] = datetime.now()) -> PageUrl:
    """
    Creates and returns a callable (PageUrl) which in terms returns
    the url given a page number.
    """
    return lambda page: SOLD_LISTINGS_URL.format(city_name=city.name.lower(),
                                                 city_code=city.value,
                                                 page=page,
                                                 from_date_sold=from_date_sold.strftime(DATETIME_FORMAT),
                                                 to_date_sold=to_date_sold.strftime(DATETIME_FORMAT))
