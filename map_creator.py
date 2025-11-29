import plotly.graph_objects as go
import pandas as pd
from aio import ThemeSwitchAIO
from plotly.graph_objs import Figure
from dash import html, dcc, Input, Output, Dash

import ids

# Build origin–destination pairs for each step of the trip
def create_path(data: pd.DataFrame) -> pd.DataFrame:
    """
    Build a DataFrame representing all steps of the trip by pairing each city
    with the following one in the route.

    This function assumes that the input DataFrame contains one row per visited
    city in chronological order. It shifts the DataFrame by one row to align each
    city with the next destination, allowing the map to draw line segments
    between sequential stops. The final row is dropped because it has no next city.

    Args:
        data (pd.DataFrame): A DataFrame containing the ordered list of visited cities.
            It must include at least the columns "Latitude" and "Longitude".

    Returns:
        pd.DataFrame: A DataFrame where each row represents one leg of the trip.
            Columns from the original DataFrame are preserved, and the corresponding
            "next" city columns are suffixed with "_next".
    """
    # Align each row with the next city
    df_path = data.join(
        data.shift(-1),  # map each stop to its next stop
        rsuffix='_next'
    ).dropna(subset=['Latitude_next']) # Remove last row (no next city)

    return df_path

def get_map(trip: list[dict], toggle: bool) -> Figure:
    """
    Generate the Plotly map displaying the trip route and visited cities.

    This function converts the trip information into a DataFrame, constructs the
    path using consecutive origin–destination pairs, and draws both the route lines
    and city markers. Line and marker colors are selected dynamically based on the
    active UI theme, allowing the visualization to remain readable in both light
    and dark modes.

    Args:
        trip (list[dict]): A list of dictionaries where each dictionary represents
            a visited city and must include "Latitude", "Longitude", and identifying
            fields such as name or country.
        toggle (bool): The current theme value from ThemeSwitchAIO.

    Returns:
        go.Figure: A Plotly Geo figure containing the full visualization of the route,
        including all line segments and city markers.
    """
    # Convert trip data to DataFrame and build path segments
    trip_path = create_path(pd.DataFrame.from_records(trip))

    # Select colors based on theme
    line_color = 'rgb(0, 92, 175)' if toggle else 'rgb(0, 180, 255)'
    points_color = 'rgb(255, 140, 0)' if toggle else 'rgb(255, 215, 0)'
    first_color = 'rgb(46, 164, 79)' if toggle else 'rgb(0, 255, 155)'

    # Initialize empty figure
    fig = go.Figure(go.Scattermap())

    for i in range(len(trip_path)):
        lon1 = trip_path['Longitude'][i]
        lon2 = trip_path['Longitude_next'][i]

        # Adjust for 180° longitude wrap
        if abs(lon1 - lon2) > 180:
            lon2 += 360

        # Add line segment and markers
        fig.add_trace(
            go.Scattermap(
                lon=[lon1, lon2],
                lat=[trip_path['Latitude'][i], trip_path['Latitude_next'][i],],
                mode='markers+lines',
                hoverinfo='text',
                text=trip_path[ids.PLACE][i],
                line=dict(width = 1.5, color = line_color),
                marker=dict(size = 5, color = points_color),
            )
        )

    # Start city marker
    fig.add_trace(go.Scattermap(
        lon = [trip_path['Longitude'].iloc[0]],
        lat = [trip_path['Latitude'].iloc[0]],
        text = trip_path[ids.PLACE].iloc[0],
        hoverinfo='text',
        marker = dict(
            size = 10,
            color = first_color,
        )))

    map_style = 'carto-positron' if toggle else 'carto-darkmatter'

    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        map_style=map_style
    )

    return fig

def render(app: Dash) -> html.Div:
    """
    Register the map callback and return the container element for the map panel.

    This function attaches the callback responsible for generating the map figure
    based on the current trip and theme. It returns the container wrapping the
    Dash Graph component, so it can be included in the application's layout.

    Args:
        app (Dash): The Dash application instance used to register callbacks.

    Returns:
        html.Div: A Div container holding the Graph component that displays the route map.
        """

    # Update map when trip or theme changes
    @app.callback(
        Output('map-graph', 'figure'),
        Input('trip', 'data'),
        Input(ThemeSwitchAIO.ids.switch('theme-switch'), 'value')
    )
    def update_map(trip: list[dict], toggle: bool) -> Figure:
        return get_map(trip, toggle)

    return html.Div(
        className='map-container',
        children=[
            dcc.Graph(
                className="map-class",
                id='map-graph',
                # Render map container
                figure = {},
                )]
        )