from dash import Dash, html, dcc
from dash_bootstrap_components.themes import BOOTSTRAP, YETI, SLATE
from dash_bootstrap_templates import ThemeSwitchAIO

import stats
from import_data import cities_data
from main import move_atw
import map_creator
import ids

# Dash app layout and theme configuration

# External Bootstrap and template styles
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.2/dbc.min.css"
app = Dash(external_stylesheets=[BOOTSTRAP, dbc_css])

app.title = 'Around the World'

# Sorted list of allowed cities for the dropdown
ALLOWED_TYPES = sorted(cities_data[ids.PLACE])

# Dark/Light theme switch component
theme_switch = ThemeSwitchAIO(aio_id='theme-switch', themes=[YETI, SLATE])

# Main application layout
app.layout = html.Div(
    className='dbc app-layout',
    children=[
        dcc.Store(id='trip', data=move_atw('London GB')),
        html.Div(
            className='grid-class',
            children=[

                # Two-column grid: map on the left, tabs + inputs on the right
                html.Div(
                    # Map section with title and rendered Plotly map
                    className='map-container',
                    children=[

                        html.H1(
                            className='title',
                            children='Around the World Map'),

                        map_creator.render(app),]
                ),

                # Tabs for statistics and visited lists
                html.Div([
                    dcc.Tabs(
                        className='tabs-container',
                        children=[

                            dcc.Tab(label='Stats',
                                 children=[stats.stat_render(app)]),

                            dcc.Tab(label='Cities',
                                 children=[
                                     html.H4(className='cities-header',
                                             children="Cities with more than 200'000 pops"),
                                     stats.list_render(app, 'cities')]),

                            dcc.Tab(label='Countries',
                                 children=[stats.list_render(app, 'countries')]),

                        ]
                    ),

                    # City selection dropdown
                    dcc.Dropdown(
                        id='dropdown',
                        className='dropdown-class',
                        options=ALLOWED_TYPES,
                        value='London GB'
                    ),

                    # Theme switch (light/dark)
                    html.Div(className= 'switch', children = [theme_switch])]
                )
            ]
        )
    ]
)

# Run application in debug mode
if __name__ == '__main__':
    app.run()