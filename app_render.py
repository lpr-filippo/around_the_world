from dash import Dash, html, dcc
from dash_bootstrap_components.themes import BOOTSTRAP

from import_data import cities_data
import map_creator
import ids

app = Dash(external_stylesheets=[BOOTSTRAP])

app.title = 'Around the World'

ALLOWED_TYPES = sorted(cities_data[ids.PLACE])

app.layout = html.Div(
    className='app-layout',
    children=[
        dcc.Dropdown(
            id='dropdown',
            className='dropdown-class',
            options=ALLOWED_TYPES,
        ),
        map_creator.render(app, cities_data, 'London GB'),
        html.Div(

        )
    ]
)

if __name__ == '__main__':
    app.run()