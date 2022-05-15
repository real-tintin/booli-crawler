from booli_crawler.types import City

BASE_URL = "https://www.booli.se"
SOLD_LISTINGS_URL = BASE_URL + "/slutpriser/{city_name}/{city_code}?page={page}"


def get_city_page_url(city: City, page: int) -> str:
    return SOLD_LISTINGS_URL.format(city_name=city.name.lower(),
                                    city_code=city.value,
                                    page=page)
