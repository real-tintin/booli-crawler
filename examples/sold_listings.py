import plotly.graph_objects as go

from booli_crawler import sold_listings
from booli_crawler.types import PropertyType, City

CITY = City.Linkoping


def main():
    listings = sold_listings.get(city=CITY,
                                 max_pages=1000,
                                 n_crawlers=100,
                                 show_progress_bar=True)

    fig = go.Figure()

    for property_type in PropertyType:
        use_indices = listings.property_type == property_type
        fig.add_traces(go.Scatter(x=listings.date_sold[use_indices],
                                  y=listings.price_sek[use_indices],
                                  mode='markers',
                                  name=property_type.name))

    fig.update_layout(
        title=f"Sold {PropertyType.Vila} in {CITY.name} (from booli.se)",
        xaxis_title="date sold [-]",
        yaxis_title="price [sek]"
    )

    fig.update_traces(customdata=listings.href,
                      hovertemplate="date sold: %{x}<br>" +
                                    "price: %{y}<br>" +
                                    "href: %{customdata: .1f}")

    fig.show()


if __name__ == '__main__':
    main()
