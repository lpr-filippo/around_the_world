import plotly.graph_objects as go
import pandas as pd
from plotly.graph_objs import Figure
from dash import html, dcc, Input, Output, Dash

from main import move_atw
import ids

def create_path(data: pd.DataFrame) -> pd.DataFrame:

    df_path = data.join(
        data.shift(-1),  # map each stop to its next stop
        rsuffix='_next'
    ).dropna(subset=['Latitude_next'])

    return df_path

def get_map(trip: pd.DataFrame) -> Figure:
    trip_path = create_path(trip)

    fig = go.Figure(go.Scattermap())

    for i in range(len(trip_path)):
        lon1 = trip_path['Longitude'][i]
        lon2 = trip_path['Longitude_next'][i]

        if abs(lon1 - lon2) > 180:
            lon2 += 360

        fig.add_trace(
            go.Scattermap(
                lon=[lon1, lon2],
                lat=[trip_path['Latitude'][i], trip_path['Latitude_next'][i],],
                mode='markers+lines',
                hoverinfo='text',
                text=trip_path[ids.PLACE][i],
                line=dict(width=1.5, color='blue'),
                marker=dict(size=5, color='rgb(255, 0, 0)')
            )
        )

    fig.add_trace(go.Scattermap(
        lon = [trip_path['Longitude'].iloc[0]],
        lat = [trip_path['Latitude'].iloc[0]],
        text = trip_path[ids.PLACE].iloc[0],
        marker = dict(
            size = 20,
            color = 'rgb(0, 255, 0)',
        )))

    fig.update_layout(
        title_text='Around The World Map',
        showlegend=False,
    )

    return fig

def render(app: Dash, data: pd.DataFrame, input_city: str) -> html.Div:
    @app.callback(
        Output('map-graph', 'figure'),
        [Input('dropdown', 'value'),]
    )
    def update_map(in_city: str) -> Figure:
        return get_map(move_atw(data, in_city))

    start_map = get_map(move_atw(data, input_city))

    return html.Div(children=[
        dcc.Graph(
            id='map-graph',
            figure = start_map,
            style = {'width': '100%', 'height': '100vh'},
            )]
        )