import pandas as pd
from dash import html, Input, Output, Dash

def compute_stats(trip: list[dict]) -> dict:
    """
    Compute summary statistics for the trip.

    This function calculates total distance, total travel time and average speed
    from the ordered list of visited locations. The input must contain all stops
    with the fields required for distance and time computation.

    Args:
        trip (list[dict]): Trip data as a list of dictionaries, each representing
            a visited city with distance, time and country fields.

    Returns:
        dict: A dictionary containing all computed summary statistics.
    """

    # Convert trip list to DataFrame
    trip = pd.DataFrame.from_records(trip)

    n_cities = trip.shape[0] - 1

    n_countries = trip["Country"].nunique()

    total_time_hours = trip["Time"].sum()
    total_time_days = round(total_time_hours/24, 2)

    total_distance = round(trip["Distance_km"].sum(), 2)

    average_speed = round(total_distance/total_time_hours, 2)

    return {
        "Visited cities": n_cities,
        "Visited countries": n_countries,
        "Total time in hours": total_time_hours,
        "Total time in days": total_time_days,
        "Total distance in km": total_distance,
        "Average longitudinal speed (degrees/hours)": average_speed
    }

def stat_render(app: Dash) -> html.Div:
    """
    Create the statistics panel and register the callback that updates it.

    The callback uses `compute_stats` to format the trip metrics and renders
    them inside the stats grid layout.

    Args:
        app (Dash): The Dash application instance used to register callbacks.

    Returns:
        html.Div: Container holding the stats section layout.
    """

    # Update stats when trip changes
    @app.callback(
        Output('stats-output', 'children'),
        [Input('trip', 'data'),]
    )
    def update_stats(trip: list[dict]) -> html.Div:
       # Compute summary statistics
       stats = compute_stats(trip)
       # Format stats as a grid of cards
       return html.Div(
           className="stats-container",
           children=html.Div(
               className="stats-grid",
               children=[
                   html.Div([
                       html.Div(k, className="stat-title"),
                       html.Div(v, className="stat-value")
                    ], className="stat-card")
                    for k, v in stats.items()]
           )
       )

    # Initial empty stats layout
    return html.Div(
       id='stats-output',
       className="stats-section",
       children=[html.Div(
           className="stats-container",
           children=html.Div(
               className="stats-grid",
               children=[
                   html.Div(
                       className="stat-card")]
           )
       )]
    )


def list_render(app: Dash, mode: str) -> html.Div:
    """
        Render and update a list based on the selected mode.

        Supported modes:
        - "cities": list of visited cities with population ≥ 200k
        - "countries": list of visited countries

        The callback reads the trip, extracts the appropriate items, and returns
        the formatted HTML list.

        Args:
            app (Dash): Dash application instance for callback registration.
            mode (str): Determines which list is displayed ("cities" or "countries").

        Returns:
            html.Div: Container that will display the dynamically updated list.
    """
    @app.callback(
        Output(f'list-output-{mode}', 'children'),
        Input('trip', 'data'),
    )
    def update_list(trip: list[dict]) -> html.Div:
        # Convert trip to DataFrame
        trip = pd.DataFrame.from_records(trip)

        if mode == "cities":
            items = list(trip.loc[trip["Population"] >= 200_000]["City_Country"].unique()) # Cities with population ≥ 200k
        elif mode == "countries":
            items = list(trip["Country name"].unique()) # List of visited countries
        else:
            raise ValueError(f"Invalid mode: {mode}. Valid modes are 'cities' and 'countries'.")

        # Render list items
        return html.Div(
            className="list-container",
            children=html.Ul(
                children=[html.Li(x) for x in items],
                className="list-ul"
            )
        )

    # Initial empty list container
    return html.Div(
        id=f'list-output-{mode}',
        className="list-section",
        children=[
            html.Div(
                className="list-container",
                children=html.Ul(
                    children=[],
                    className="list-ul"
                )
            )
        ]
    )