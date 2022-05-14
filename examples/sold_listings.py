import plotly.graph_objects as go

from booli_crawler.sold_listings import City, get_sold_listings, PropertyType

CITY = City.Linkoping
MAX_PAGES = 10


def main():
    sold_listings = get_sold_listings(city=CITY, max_pages=MAX_PAGES, show_progress_bar=True)

    fig = go.Figure()

    for property_type in PropertyType:
        use_indices = sold_listings.property_type == property_type
        fig.add_traces(go.Scatter(x=sold_listings.date_sold[use_indices],
                                  y=sold_listings.price_sek[use_indices],
                                  mode='markers',
                                  name=property_type.name))

    fig.update_layout(
        title=f"Sold {PropertyType.Vila} in {CITY.name} (from booli.se)",
        xaxis_title="date sold [-]",
        yaxis_title="price [sek]"
    )

    fig.update_traces(customdata=sold_listings.href,
                      hovertemplate="date sold: %{x}<br>" +
                                    "price: %{y}<br>" +
                                    "href: %{customdata: .1f}")

    fig.show()


if __name__ == '__main__':
    main()
