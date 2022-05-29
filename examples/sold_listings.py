import logging
from datetime import datetime

import plotly.graph_objects as go

from booli_crawler import sold_listings
from booli_crawler.types import PropertyType, City

logging.basicConfig(level=logging.INFO)

CITY = City.Linkoping

FROM_DATE_SOLD = datetime.strptime('2015', '%Y')

N_CRAWLERS = 10

MOVING_AVERAGE_H = 24 * 7 * 4  # one month

DEFAULT_VISIBLE_PROPERTY_TYPES = [PropertyType.Vila, PropertyType.Apartment]


def main():
    """
    Plots sold properties over time. Computes and shows a moving average (MA)
    of the normalized price/area.
    """
    listings = sold_listings.get(city=CITY,
                                 from_date_sold=FROM_DATE_SOLD,
                                 n_crawlers=N_CRAWLERS,
                                 show_progress_bar=True)

    price_per_area = listings.price_sek / listings.area_m2

    fig = go.Figure()

    for property_type in PropertyType:
        use_indices = listings.property_type == property_type

        fig.add_trace(go.Scatter(x=price_per_area[use_indices].index,
                                 y=price_per_area[use_indices].rolling(f'{MOVING_AVERAGE_H}H').mean(),
                                 mode='lines',
                                 visible=None if property_type in DEFAULT_VISIBLE_PROPERTY_TYPES else 'legendonly',
                                 name=property_type.name))

    fig.update_layout(
        title=f"Sold listings in {CITY.name} (from booli.se)",
        xaxis_title="date sold [-]",
        yaxis_title="price/area (MA) [sek/m²]",
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                         label="1m",
                         step="month",
                         stepmode="backward"),
                    dict(count=6,
                         label="6m",
                         step="month",
                         stepmode="backward"),
                    dict(count=1,
                         label="YTD",
                         step="year",
                         stepmode="todate"),
                    dict(count=1,
                         label="1y",
                         step="year",
                         stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )
    )

    fig.show()


if __name__ == '__main__':
    main()
