import dash
from dash import _dash_renderer, html, dcc, callback, Output, Input, State
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
from dash_iconify import DashIconify
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

_dash_renderer._set_react_version("18.2.0")

# EDA
df = pd.read_csv("https://raw.githubusercontent.com/jmanali1996/Civilian-Conflicts/main/GEDEvent_v24_1.csv", low_memory=False)
df = df.astype({"type_of_violence": 'str'})
df.loc[df['type_of_violence'] == '1', 'type_of_violence'] = "State-based conflict"
df.loc[df['type_of_violence'] == '2', 'type_of_violence'] = "Non-state conflict"
df.loc[df['type_of_violence'] == '3', 'type_of_violence'] = "One-sided violence"
df = df.astype({"active_year": 'str'})
df.loc[df['active_year'] == '0', 'active_year'] = "Under 25 fatalities"
df.loc[df['active_year'] == '1', 'active_year'] = "Over 25 fatalities"
df = df.astype({"where_prec": 'str'})
df.loc[df['where_prec'] == '1', 'where_prec'] = "Exact location"
df.loc[df['where_prec'] == '2', 'where_prec'] = "Within 25 km radius"
df.loc[df['where_prec'] == '3', 'where_prec'] = "Local area"
df.loc[df['where_prec'] == '4', 'where_prec'] = "Region level"
df.loc[df['where_prec'] == '5', 'where_prec'] = "Linear feature"
df.loc[df['where_prec'] == '6', 'where_prec'] = "Country level"
df.loc[df['where_prec'] == '7', 'where_prec'] = "International waters/airspace"
df = df.astype({"date_prec": 'str'})
df.loc[df['date_prec'] == '1', 'date_prec'] = "Exact date"
df.loc[df['date_prec'] == '2', 'date_prec'] = "2-6 day range"
df.loc[df['date_prec'] == '3', 'date_prec'] = "Week known"
df.loc[df['date_prec'] == '4', 'date_prec'] = "Month known"
df.loc[df['date_prec'] == '5', 'date_prec'] = "Year known"
dff_cd = df[['year', 'region', 'country', 'conflict_name', 'date_start', 'date_end', 'where_prec', 'date_prec', 'best']].copy()
dff_cd['date_start'] = pd.to_datetime(dff_cd['date_start'], format='%Y/%m/%d %H:%M:%S')
dff_cd['date_end'] = pd.to_datetime(dff_cd['date_end'], format='%Y/%m/%d %H:%M:%S')
dff_cd['conflict_duration'] = dff_cd['date_end'] - dff_cd['date_start']
dff_cd['conflict_period'] = dff_cd['conflict_duration'].dt.days
dff_cd = dff_cd.sort_values(['conflict_period', 'best'], ascending=[False, False])

app = dash.Dash(__name__, suppress_callback_exceptions=True)

# WORLDWIDE CONFLICTS AND FATALITIES PAGE 
wcf_layout = dmc.MantineProvider(
    children=[
        dmc.Title("Shattered Lives", order=1, style={'textAlign': 'center', 'color': 'red'}),
        #menu and page title
        html.Div([
            html.Div([
                dmc.Menu([
                    dmc.MenuTarget(dmc.Burger()),
                    dmc.MenuDropdown([
                        dmc.MenuItem(dcc.Link("Worldwide Conflicts and Fatalities", href="/worldwide-conflicts-and-fatalities")),
                        dmc.MenuItem(dcc.Link("Fatalities Causation", href="/fatalities-causation")),
                        dmc.MenuItem(dcc.Link("Fatalities Distribution", href="/fatalities-distribution")),
                        dmc.MenuItem(dcc.Link("Conflicts Details", href="/conflicts-details"))
                    ])
                ])
            ], style={'display': 'inline-block', 'marginLeft': 10}),
            html.Div([
                dmc.Text("Worldwide Conflicts and Fatalities", size="xl", fw=700)
            ], style={'display': 'inline-block', 'marginLeft': 5})
        ], style={'display': 'flex', 'alignItems': 'center'}),
        #dropdowns
        html.Div([
            html.Div([
                html.Label(children=['Year:'], style={'color': 'black', 'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='year-variable',
                    options=[{'label':y,'value':y} for y in sorted(df['year'].unique())],
                    value=None,
                    multi=True,
                    searchable=True,
                    placeholder="Select a year",
                    style={'color': 'black', 'width': 276, 'height': 40}
                )
            ], style={'display': 'inline-block', 'marginLeft': 10, 'marginRight': 10, 'marginBottom': 10, 'verticalAlign': 'top'}),
            html.Div([
                html.Label(children=['Region:'], style={'color': 'black', 'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='region-variable',
                    options=[{'label':r,'value':r} for r in sorted(df['region'].unique())],
                    value=None,
                    multi=True,
                    searchable=True,
                    placeholder="Select a region",
                    style={'color': 'black', 'width': 276, 'height': 40}
                )
            ], style={'display': 'inline-block', 'marginRight': 10, 'marginBottom': 10, 'verticalAlign': 'top'}),
            html.Div([
                html.Label(children=['Country:'], style={'color': 'black', 'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='country-variable',
                    options=[{'label':c,'value':c} for c in sorted(df['country'].unique())],
                    value=None,
                    multi=True,
                    searchable=True,
                    placeholder="Select a country",
                    style={'color': 'black', 'width': 276, 'height': 40}
                )
            ], style={'display': 'inline-block', 'marginRight': 10, 'marginBottom': 10, 'verticalAlign': 'top'}),
            html.Div([
                html.Label(children=['Type of violence:'], style={'color': 'black', 'fontWeight': 'bold'}),
                html.Div(
                    children=dmc.Popover(
                        [
                            dmc.PopoverTarget(
                                dmc.ActionIcon(
                                    DashIconify(icon="dashicons:info"),
                                    size="xs"
                                )
                            ),
                            dmc.PopoverDropdown(
                                children=[
                                    dmc.Text(
                                        children=[
                                            html.B("Non-state conflict"), " is armed force between two organized groups, neither of "
                                            "which is a state government, resulting in at least 25 battle-related deaths in a year."
                                        ],
                                    size="sm"
                                    ),
                                    dmc.Text(
                                        children=[
                                            html.B("One-sided violence"), " is the use of armed force by a government or organized group "
                                            "against civilians, resulting in at least 25 deaths, excluding extrajudicial killings in custody."
                                        ],
                                        size="sm"
                                    ),
                                    dmc.Text(
                                        children=[
                                            html.B("State-based armed conflict"), " involves a dispute over government or territory, "
                                            "where armed force between at least one government and another party results in "
                                            "at least 25 battle-related deaths in a year."
                                        ],
                                        size="sm"
                                    ),
                                    dmc.Text(
                                        "source: Uppsala Conflict Data Program (UCDP)",
                                        size="sm",
                                        c="gray"
                                    )
                                ] 
                            )
                        ],
                        width=400,
                        position="bottom",
                        withArrow=True,
                        shadow="md",
                        zIndex=2000
                    ),
                    style={'position': 'absolute', 'top': 5, 'left': 258, 'zIndex': 1}
                ),
                dcc.Dropdown(
                    id='violence-variable',
                    options=[{'label':v,'value':v} for v in sorted(df['type_of_violence'].unique())],
                    value=None,
                    multi=True,
                    searchable=True,
                    placeholder="Select a type of violence",
                    style={'color': 'black', 'width': 276, 'height': 40}
                )
            ], style={'position': 'relative', 'display': 'inline-block', 'marginRight': 10, 'marginBottom': 10, 'verticalAlign': 'top'}),
            html.Div([
                dmc.Button(
                    id="submit-btn-wcf",
                    children="Submit",
                    size="md",
                    color="black",
                    style={'font-weight': 'bold', 'font-size': 15, 'width': 276, 'height': 40}
                )
            ], style={'display': 'inline-block', 'marginRight': 10, 'marginBottom': 10, 'verticalAlign': 'bottom'})
        ]), 
        #cards
        html.Div([
            html.Div([
                dmc.Card(
                    id='selected-year-card',
                    shadow="sm",
                    withBorder=True,
                    style={'backgroundColor': '#bebebe', 'color': '#b7091d', 'fontWeight': 'bold'}
                )
            ], style={'display': 'inline-block', 'marginLeft': 10, 'marginRight': 10, 'marginBottom': 10, 'width': 276, 'textAlign': 'center', 'fontSize': 20}),
            html.Div([
                dmc.Card(
                    id='selected-region-card',
                    shadow="sm",
                    withBorder=True,
                    style={'backgroundColor': '#bebebe', 'color': '#b7091d', 'fontWeight': 'bold'}
                )
            ], style={'display': 'inline-block', 'marginRight': 10, 'marginBottom': 10, 'width': 276, 'textAlign': 'center', 'fontSize': 20}),
            html.Div([
                dmc.Card(
                    id='selected-country-card',
                    shadow="sm",
                    withBorder=True,
                    style={'backgroundColor': '#bebebe', 'color': '#b7091d', 'fontWeight': 'bold'}
                )
            ], style={'display': 'inline-block', 'marginRight': 10, 'marginBottom': 10, 'width': 276, 'textAlign': 'center', 'fontSize': 20}),
            html.Div([
                dmc.Card(
                    id='conflict-count-card',
                    shadow="sm",
                    withBorder=True,
                    style={'backgroundColor': '#bebebe', 'color': '#b7091d', 'fontWeight': 'bold'}
                )
            ], style={'display': 'inline-block', 'marginRight': 10, 'marginBottom': 10, 'width': 276, 'textAlign': 'center', 'fontSize': 20}),
            html.Div([
                dmc.Card(
                    id='fatality-sum-card',
                    shadow="sm",
                    withBorder=True,
                    style={'backgroundColor': '#bebebe', 'color': '#b7091d', 'fontWeight': 'bold'}
                )
            ], style={'display': 'inline-block', 'marginRight': 10, 'marginBottom': 10, 'width': 276, 'textAlign': 'center', 'fontSize': 20})
        ]),
        #treemap graph
        html.Div([
            dcc.Graph(id='wcf-chart')
        ], style={'marginLeft': 10, 'marginRight': 10, 'width': 1420})
    ]
)

# FATALITIES CAUSATION PAGE
fo_layout = dmc.MantineProvider(
    children=[
        dmc.Title("Shattered Lives", order=1, style={'textAlign': 'center', 'color': 'red'}),
        #menu and page title
        html.Div([
            html.Div([
                dmc.Menu([
                    dmc.MenuTarget(dmc.Burger()),
                    dmc.MenuDropdown([
                        dmc.MenuItem(dcc.Link("Worldwide Conflicts and Fatalities", href="/worldwide-conflicts-and-fatalities")),
                        dmc.MenuItem(dcc.Link("Fatalities Causation", href="/fatalities-causation")),
                        dmc.MenuItem(dcc.Link("Fatalities Distribution", href="/fatalities-distribution")),
                        dmc.MenuItem(dcc.Link("Conflicts Details", href="/conflicts-details"))
                    ])
                ])
            ], style={'display': 'inline-block', 'marginLeft': 10}),
            html.Div([
                dmc.Text("Fatalities Causation", size="xl", fw=700)
            ], style={'display': 'inline-block', 'marginLeft': 5})
        ], style={'display': 'flex', 'alignItems': 'center'}),
        #dropdowns
        html.Div([
            html.Div([
                html.Label(children=['Year:'], style={'color': 'black', 'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='year-variable',
                    options=[{'label':y,'value':y} for y in sorted(df['year'].unique())],
                    value=None,
                    multi=True,
                    searchable=True,
                    placeholder="Select a year",
                    style={'color': 'black', 'width': 276, 'height': 40}
                )
            ], style={'display': 'inline-block', 'marginLeft': 10, 'marginRight': 10, 'marginBottom': 10, 'verticalAlign': 'top'}),
            html.Div([
                html.Label(children=['Region:'], style={'color': 'black', 'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='region-variable',
                    options=[{'label':r,'value':r} for r in sorted(df['region'].unique())],
                    value=None,
                    multi=True,
                    searchable=True,
                    placeholder="Select a region",
                    style={'color': 'black', 'width': 276, 'height': 40}
                )
            ], style={'display': 'inline-block', 'marginRight': 10, 'marginBottom': 10, 'verticalAlign': 'top'}),
            html.Div([
                html.Label(children=['Country:'], style={'color': 'black', 'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='country-variable',
                    options=[{'label':c,'value':c} for c in sorted(df['country'].unique())],
                    value=None,
                    multi=True,
                    searchable=True,
                    placeholder="Select a country",
                    style={'color': 'black', 'width': 276, 'height': 40}
                )
            ], style={'display': 'inline-block', 'marginRight': 10, 'marginBottom': 10, 'verticalAlign': 'top'}),
            html.Div([
                html.Label(children=['Type of violence:'], style={'color': 'black', 'fontWeight': 'bold'}),
                html.Div(
                    children=dmc.Popover(
                        [
                            dmc.PopoverTarget(
                                dmc.ActionIcon(
                                    DashIconify(icon="dashicons:info"),
                                    size="xs"
                                )
                            ),
                            dmc.PopoverDropdown(
                                children=[
                                    dmc.Text(
                                        children=[
                                            html.B("Non-state conflict"), " is armed force between two organized groups, neither of "
                                            "which is a state government, resulting in at least 25 battle-related deaths in a year."
                                        ],
                                    size="sm"
                                    ),
                                    dmc.Text(
                                        children=[
                                            html.B("One-sided violence"), " is the use of armed force by a government or organized group "
                                            "against civilians, resulting in at least 25 deaths, excluding extrajudicial killings in custody."
                                        ],
                                        size="sm"
                                    ),
                                    dmc.Text(
                                        children=[
                                            html.B("State-based armed conflict"), " involves a dispute over government or territory, "
                                            "where armed force between at least one government and another party results in "
                                            "at least 25 battle-related deaths in a year."
                                        ],
                                        size="sm"
                                    ),
                                    dmc.Text(
                                        "source: Uppsala Conflict Data Program (UCDP)",
                                        size="sm",
                                        c="gray"
                                    )
                                ] 
                            )
                        ],
                        width=400,
                        position="bottom",
                        withArrow=True,
                        shadow="md",
                        zIndex=2000
                    ),
                    style={'position': 'absolute', 'top': 5, 'left': 258, 'zIndex': 1}
                ),
                dcc.Dropdown(
                    id='violence-variable',
                    options=[{'label':v,'value':v} for v in sorted(df['type_of_violence'].unique())],
                    value=None,
                    multi=True,
                    searchable=True,
                    placeholder="Select a type of violence",
                    style={'color': 'black', 'width': 276, 'height': 40}
                )
            ], style={'position': 'relative', 'display': 'inline-block', 'marginRight': 10, 'marginBottom': 10, 'verticalAlign': 'top'}),
            html.Div([
                dmc.Button(
                    id="submit-btn-fo",
                    children="Submit",
                    size="md",
                    color="black",
                    style={'font-weight': 'bold', 'font-size': 15, 'width': 276, 'height': 40}
                )
            ], style={'display': 'inline-block', 'marginRight': 10, 'marginBottom': 10, 'verticalAlign': 'bottom'})
        ]),
        #pie and bar graphs
        html.Div([
            html.Div([
                dcc.Graph(id='tov-chart')
            ], style={'display': 'inline-block', 'marginLeft': 10, 'marginRight': 20, 'width': 700, 'height': 450}),
            html.Div([
                dcc.Graph(id='fc-chart')
            ], style={'display': 'inline-block', 'marginRight': 10, 'width': 700, 'height': 450})
        ]),
        #donut graphs
        html.Div([
            dcc.Graph(id='ft-chart'),
            html.Div(
                children=dmc.Popover(
                    [
                        dmc.PopoverTarget(
                            dmc.ActionIcon(
                                DashIconify(icon="streamline:information-desk-solid", width=30),
                                size="lg"
                            )
                        ),
                        dmc.PopoverDropdown(
                            children=[
                                dmc.Text(
                                    "If a party killing unarmed civilians crosses the 25-death threshold in a year, all its events, "
                                    "even those in years below the threshold, are included."
                                ),
                                dmc.Text(
                                    "source: Uppsala Conflict Data Program (UCDP)",
                                    c="gray"
                                )
                            ] 
                        )
                    ],
                    width=200,
                    position="bottom",
                    withArrow=True,
                    shadow="md",
                    zIndex=2000
                ),
                style={'position': 'absolute', 'top': 25, 'left': 1380, 'zIndex': 1}
            )
        ], style={'position': 'relative', 'marginLeft': 10, 'marginRight': 10, 'width': 1420, 'height': 450}) 
    ]
)

# FATALITIES DISTRIBUTION PAGE
fd_layout = dmc.MantineProvider(
    children=[
        dmc.Title("Shattered Lives", order=1, style={'textAlign': 'center', 'color': 'red'}),
        #menu and page title
        html.Div([
            html.Div([
                dmc.Menu([
                    dmc.MenuTarget(dmc.Burger()),
                    dmc.MenuDropdown([
                        dmc.MenuItem(dcc.Link("Worldwide Conflicts and Fatalities", href="/worldwide-conflicts-and-fatalities")),
                        dmc.MenuItem(dcc.Link("Fatalities Causation", href="/fatalities-causation")),
                        dmc.MenuItem(dcc.Link("Fatalities Distribution", href="/fatalities-distribution")),
                        dmc.MenuItem(dcc.Link("Conflicts Details", href="/conflicts-details"))
                    ])
                ])
            ], style={'display': 'inline-block', 'marginLeft': 10}),
            html.Div([
                dmc.Text("Fatalities Distribution", size="xl", fw=700)
            ], style={'display': 'inline-block', 'marginLeft': 5})
        ], style={'display': 'flex', 'alignItems': 'center'}),
        #dropdowns
        html.Div([
            html.Div([
                html.Label(children=['Year:'], style={'color': 'black', 'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='year-variable',
                    options=[{'label':y,'value':y} for y in sorted(df['year'].unique())],
                    value=None,
                    multi=True,
                    searchable=True,
                    placeholder="Select a year",
                    style={'color': 'black', 'width': 276, 'height': 40}
                )
            ], style={'display': 'inline-block', 'marginLeft': 10, 'marginRight': 10, 'marginBottom': 10, 'verticalAlign': 'top'}),
            html.Div([
                html.Label(children=['Region:'], style={'color': 'black', 'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='region-variable',
                    options=[{'label':r,'value':r} for r in sorted(df['region'].unique())],
                    value=None,
                    multi=True,
                    searchable=True,
                    placeholder="Select a region",
                    style={'color': 'black', 'width': 276, 'height': 40}
                )
            ], style={'display': 'inline-block', 'marginRight': 10, 'marginBottom': 10, 'verticalAlign': 'top'}),
            html.Div([
                html.Label(children=['Country:'], style={'color': 'black', 'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='country-variable',
                    options=[{'label':c,'value':c} for c in sorted(df['country'].unique())],
                    value=None,
                    multi=True,
                    searchable=True,
                    placeholder="Select a country",
                    style={'color': 'black', 'width': 276, 'height': 40}
                )
            ], style={'display': 'inline-block', 'marginRight': 10, 'marginBottom': 10, 'verticalAlign': 'top'}),
            html.Div([
                html.Label(children=['Type of violence:'], style={'color': 'black', 'fontWeight': 'bold'}),
                html.Div(
                    children=dmc.Popover(
                        [
                            dmc.PopoverTarget(
                                dmc.ActionIcon(
                                    DashIconify(icon="dashicons:info"),
                                    size="xs"
                                )
                            ),
                            dmc.PopoverDropdown(
                                children=[
                                    dmc.Text(
                                        children=[
                                            html.B("Non-state conflict"), " is armed force between two organized groups, neither of "
                                            "which is a state government, resulting in at least 25 battle-related deaths in a year."
                                        ],
                                    size="sm"
                                    ),
                                    dmc.Text(
                                        children=[
                                            html.B("One-sided violence"), " is the use of armed force by a government or organized group "
                                            "against civilians, resulting in at least 25 deaths, excluding extrajudicial killings in custody."
                                        ],
                                        size="sm"
                                    ),
                                    dmc.Text(
                                        children=[
                                            html.B("State-based armed conflict"), " involves a dispute over government or territory, "
                                            "where armed force between at least one government and another party results in "
                                            "at least 25 battle-related deaths in a year."
                                        ],
                                        size="sm"
                                    ),
                                    dmc.Text(
                                        "source: Uppsala Conflict Data Program (UCDP)",
                                        size="sm",
                                        c="gray"
                                    )
                                ] 
                            )
                        ],
                        width=400,
                        position="bottom",
                        withArrow=True,
                        shadow="md",
                        zIndex=2000
                    ),
                    style={'position': 'absolute', 'top': 5, 'left': 258, 'zIndex': 1}
                ),
                dcc.Dropdown(
                    id='violence-variable',
                    options=[{'label':v,'value':v} for v in sorted(df['type_of_violence'].unique())],
                    value=None,
                    multi=True,
                    searchable=True,
                    placeholder="Select a type of violence",
                    style={'color': 'black', 'width': 276, 'height': 40}
                )
            ], style={'position': 'relative', 'display': 'inline-block', 'marginRight': 10, 'marginBottom': 10, 'verticalAlign': 'top'}),
            html.Div([
                dmc.Button(
                    id="submit-btn-fd",
                    children="Submit",
                    size="md",
                    color="black",
                    style={'font-weight': 'bold', 'font-size': 15, 'width': 276, 'height': 40}
                )
            ], style={'display': 'inline-block', 'marginRight': 10, 'marginBottom': 10, 'verticalAlign': 'bottom'})
        ]),
        #pie and bar graphs
        html.Div([
            dcc.Graph(id='tof-chart'),
            html.Div(
                children=dmc.Popover(
                    [
                        dmc.PopoverTarget(
                            dmc.ActionIcon(
                                DashIconify(icon="streamline:information-desk-solid", width=30),
                                size="lg"
                            )
                        ),
                        dmc.PopoverDropdown(
                            children=[
                                dmc.Text(
                                    "In conflicts, typically two parties are involved."
                                ),
                                dmc.Text(
                                    children=[
                                            html.B("First-party fatalities"), ": Deaths sustained by one side. In state-based conflicts, this is usually " 
                                            "the government. In one-sided violence, it is the perpetrating party. Always 0 for one-sided violence events."
                                        ],
                                    size="sm"
                                ),
                                dmc.Text(
                                    children=[
                                            html.B("Second-party fatalities"), ": Deaths sustained by the other side. In state-based conflicts, this is "
                                            "typically the rebel movement or a rival government. In one-sided violence, it refers to civilians. Always 0 for "
                                            "one-sided violence events."
                                        ],
                                    size="sm"
                                ),
                                dmc.Text(
                                    children=[
                                            html.B("Civilian fatalities"), ": Collateral damage during fighting between the two parties in state-based or "
                                            "non-state conflicts. In one-sided violence, it is the number of civilians killed by the first party."
                                        ],
                                    size="sm"
                                ),
                                dmc.Text(
                                    children=[
                                            html.B("Unknown fatalities"), ": Deaths of individuals whose status is unknown."
                                        ],
                                    size="sm"
                                ),
                                dmc.Text(
                                    children=[
                                        html.I("Note: These numbers represent the best estimates of fatalities.")
                                    ],
                                    size="sm",
                                    c="gray"
                                ),
                                dmc.Text(
                                    "source: Uppsala Conflict Data Program (UCDP)",
                                    size="sm",
                                    c="gray"
                                )
                            ] 
                        )
                    ],
                    width=500,
                    position="bottom",
                    withArrow=True,
                    shadow="md",
                    zIndex=2000
                ),
                style={'position': 'absolute', 'top': 25, 'left': 1380, 'zIndex': 1}
            )
        ], style={'position': 'relative', 'marginLeft': 10, 'marginRight': 10, 'width': 1420})
    ]
)

# CONFLICTS DETAILS PAGE
cd_layout = dmc.MantineProvider(
    children=[
        dmc.Title("Shattered Lives", order=1, style={'textAlign': 'center', 'color': 'red'}),
        #menu and page title
        html.Div([
            html.Div([
                dmc.Menu([
                    dmc.MenuTarget(dmc.Burger()),
                    dmc.MenuDropdown([
                        dmc.MenuItem(dcc.Link("Worldwide Conflicts and Fatalities", href="/worldwide-conflicts-and-fatalities")),
                        dmc.MenuItem(dcc.Link("Fatalities Causation", href="/fatalities-causation")),
                        dmc.MenuItem(dcc.Link("Fatalities Distribution", href="/fatalities-distribution")),
                        dmc.MenuItem(dcc.Link("Conflicts Details", href="/conflicts-details"))
                    ])
                ])
            ], style={'display': 'inline-block', 'marginLeft': 10}),
            html.Div([
                dmc.Text("Conflicts Details", size="xl", fw=700)
            ], style={'display': 'inline-block', 'marginLeft': 5})
        ], style={'display': 'flex', 'alignItems': 'center'}),
        #table grid
        html.Div([
            dag.AgGrid(
                id="conflicts-details",
                className="ag-theme-material",
                rowData=dff_cd.to_dict("records"),
                columnDefs=[
                    {'field': 'year', 'headerName': 'Year'},
                    {'field': 'region', 'headerName': 'Region'},
                    {'field': 'country', 'headerName': 'Country'},
                    {'field': 'conflict_name', 'headerName': 'Conflict'},
                    {'field': 'conflict_period', 'headerName': 'Duration (days)'},
                    {'field': 'best', 'headerName': 'Total fatalities'},
                    {'field': 'where_prec', 'headerName': 'Location precision'},
                    {'field': 'date_prec', 'headerName': 'Date precision'}
                ],
                columnSize = "autoSize",
                defaultColDef = {"filter": True, "wrapHeaderText": True},
                dashGridOptions = {"animateRows": True, "pagination": True, "paginationPageSize":12},
                style = {"height": 700}
            )
        ], style={'marginLeft': 10, 'marginRight': 10, 'width': 1420})
    ]
)

# WELCOME PAGE 
wlc_page_layout = html.Div(
    style={
        "width": "1440px",
        "height": "780px",
        "background-image": "url('https://i.postimg.cc/gJ73Mfcw/Stop-war.png')",
        "background-size": "contain",
        "background-repeat": "no-repeat",
        "background-position": "center",
        "background-color": "black",
        "position": "relative"
    },
    children=html.Div(
        style={
            "position": "absolute",
            "bottom": "20px",
            "left": "50%",
            "transform": "translateX(-50%)"
        },
        children=html.A(
            dmc.Button(
                children="Know more!",
                size="xl",
                color="black"
            ),
            href="/worldwide-conflicts-and-fatalities"
        )
    )
)

# APP LAYOUT
app.layout = dmc.MantineProvider(
    children=[
        dcc.Location(id='url', refresh=False),  
        html.Div(id='page-content')
    ]
)

# PAGES LINK
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/worldwide-conflicts-and-fatalities':
        return wcf_layout
    elif pathname == '/fatalities-causation':
        return fo_layout
    elif pathname == '/fatalities-distribution':
        return fd_layout
    elif pathname == '/conflicts-details':
        return cd_layout
    else:
        return wlc_page_layout

# REGION OPTIONS BASED ON YEAR
@app.callback(
    Output('region-variable', 'options'),
    Input('year-variable', 'value')
)
def set_region_options_on_year(selected_year):
    if selected_year:
        fyr = df[df['year'].isin(selected_year)]['region'].unique()
        return [{'label': region, 'value': region} for region in fyr]
    else:
        return [{'label': region, 'value': region} for region in sorted(df['region'].unique())]

# COUNTRIES OPTIONS BASED ON YEAR AND REGION
@app.callback(
    Output('country-variable', 'options'),
    [Input('year-variable', 'value'),
     Input('region-variable', 'value')]
)
def set_country_options(selected_year, selected_region):
    fyrc = df.copy()
    if selected_year:
        fyrc = df[df['year'].isin(selected_year)]
    if selected_region:
        fyrc = df[df['region'].isin(selected_region)]
    cf = sorted(fyrc['country'].unique())
    return [{'label': country, 'value': country} for country in cf]
    
# YEARS CARD
@app.callback(
    Output('selected-year-card', 'children'),
    Input('submit-btn-wcf', 'n_clicks'),
    State('year-variable', 'value'),
    State('region-variable', 'value'),
    State('country-variable', 'value'),
    State('violence-variable', 'value')
)
def update_selected_year_count(_, selected_year, selected_region, selected_country, selected_violence):
    if selected_year and selected_region and selected_country and selected_violence:
        dff_y = df[(df['year'].isin(selected_year)) & (df['region'].isin(selected_region)) & (df['country'].isin(selected_country)) & (df['type_of_violence'].isin(selected_violence))]
        year_count = dff_y['year'].nunique()
    elif selected_year and selected_region and selected_country:
        dff_y = df[(df['year'].isin(selected_year)) & (df['region'].isin(selected_region)) & (df['country'].isin(selected_country))]
        year_count = dff_y['year'].nunique()
    elif selected_year and selected_region and selected_violence:
        dff_y = df[(df['year'].isin(selected_year)) & (df['region'].isin(selected_region)) & (df['type_of_violence'].isin(selected_violence))]
        year_count = dff_y['year'].nunique()
    elif selected_year and selected_region:
        dff_y = df[(df['year'].isin(selected_year)) & (df['region'].isin(selected_region))]
        year_count = dff_y['year'].nunique()
    elif selected_year and selected_violence:
        dff_y = df[(df['year'].isin(selected_year)) & (df['type_of_violence'].isin(selected_violence))]
        year_count = dff_y['year'].nunique()
    elif selected_region and selected_country:
        dff_y = df[(df['region'].isin(selected_region)) & (df['country'].isin(selected_country))]
        year_count = dff_y['year'].nunique()
    elif selected_region and selected_violence:
        dff_y = df[(df['region'].isin(selected_region)) & (df['type_of_violence'].isin(selected_violence))]
        year_count = dff_y['year'].nunique()
    elif selected_year:
        dff_y = df[(df['year'].isin(selected_year))]
        year_count = dff_y['year'].nunique()
    elif selected_region:
        dff_y = df[(df['region'].isin(selected_region))]
        year_count = dff_y['year'].nunique()
    elif selected_country:
        dff_y = df[(df['country'].isin(selected_country))]
        year_count = dff_y['year'].nunique()
    elif selected_violence:
        dff_y = df[(df['type_of_violence'].isin(selected_violence))]
        year_count = dff_y['year'].nunique()
    else:
        year_count = df['year'].nunique()
    return [html.Span("Total years"), html.Span(year_count)]

# REGIONS CARD
@app.callback(
    Output('selected-region-card', 'children'),
    Input('submit-btn-wcf', 'n_clicks'),
    State('year-variable', 'value'),
    State('region-variable', 'value'),
    State('country-variable', 'value'),
    State('violence-variable', 'value')
)
def update_selected_region_count(_, selected_year, selected_region, selected_country, selected_violence):
    if selected_year and selected_region and selected_country and selected_violence:
        dff_r = df[(df['year'].isin(selected_year)) & (df['region'].isin(selected_region)) & (df['country'].isin(selected_country)) & (df['type_of_violence'].isin(selected_violence))]
        region_count = dff_r['region'].nunique()
    elif selected_year and selected_region and selected_country:
        dff_r = df[(df['year'].isin(selected_year)) & (df['region'].isin(selected_region)) & (df['country'].isin(selected_country))]
        region_count = dff_r['region'].nunique()
    elif selected_year and selected_region and selected_violence:
        dff_r = df[(df['year'].isin(selected_year)) & (df['region'].isin(selected_region)) & (df['type_of_violence'].isin(selected_violence))]
        region_count = dff_r['region'].nunique()
    elif selected_year and selected_region:
        dff_r = df[(df['year'].isin(selected_year)) & (df['region'].isin(selected_region))]
        region_count = dff_r['region'].nunique()
    elif selected_year and selected_violence:
        dff_r = df[(df['year'].isin(selected_year)) & (df['type_of_violence'].isin(selected_violence))]
        region_count = dff_r['region'].nunique()
    elif selected_region and selected_country:
        dff_r = df[(df['region'].isin(selected_region)) & (df['country'].isin(selected_country))]
        region_count = dff_r['region'].nunique()
    elif selected_region and selected_violence:
        dff_r = df[(df['region'].isin(selected_region)) & (df['type_of_violence'].isin(selected_violence))]
        region_count = dff_r['region'].nunique()
    elif selected_year:
        dff_r = df[(df['year'].isin(selected_year))]
        region_count = dff_r['region'].nunique()
    elif selected_region:
        dff_r = df[(df['region'].isin(selected_region))]
        region_count = dff_r['region'].nunique()
    elif selected_country:
        dff_r = df[(df['country'].isin(selected_country))]
        region_count = dff_r['region'].nunique()
    elif selected_violence:
        dff_r = df[(df['type_of_violence'].isin(selected_violence))]
        region_count = dff_r['region'].nunique()
    else:
        region_count = df['region'].nunique()
    return [html.Span("Total regions"), html.Span(region_count)]

# COUNTRIES CARD
@app.callback(
    Output('selected-country-card', 'children'),
    Input('submit-btn-wcf', 'n_clicks'),
    State('year-variable', 'value'),
    State('region-variable', 'value'),
    State('country-variable', 'value'),
    State('violence-variable', 'value')
)
def update_selected_country_count(_, selected_year, selected_region, selected_country, selected_violence):
    if selected_year and selected_region and selected_country and selected_violence:
        dff_c = df[(df['year'].isin(selected_year)) & (df['region'].isin(selected_region)) & (df['country'].isin(selected_country)) & (df['type_of_violence'].isin(selected_violence))]
        country_count = dff_c['country'].nunique()
    elif selected_year and selected_region and selected_country:
        dff_c = df[(df['year'].isin(selected_year)) & (df['region'].isin(selected_region)) & (df['country'].isin(selected_country))]
        country_count = dff_c['country'].nunique()
    elif selected_year and selected_region and selected_violence:
        dff_c = df[(df['year'].isin(selected_year)) & (df['region'].isin(selected_region)) & (df['type_of_violence'].isin(selected_violence))]
        country_count = dff_c['country'].nunique()
    elif selected_year and selected_region:
        dff_c = df[(df['year'].isin(selected_year)) & (df['region'].isin(selected_region))]
        country_count = dff_c['country'].nunique()
    elif selected_year and selected_violence:
        dff_c = df[(df['year'].isin(selected_year)) & (df['type_of_violence'].isin(selected_violence))]
        country_count = dff_c['country'].nunique()
    elif selected_region and selected_country:
        dff_c = df[(df['region'].isin(selected_region)) & (df['country'].isin(selected_country))]
        country_count = dff_c['country'].nunique()
    elif selected_region and selected_violence:
        dff_c = df[(df['region'].isin(selected_region)) & (df['type_of_violence'].isin(selected_violence))]
        country_count = dff_c['country'].nunique()
    elif selected_year:
        dff_c = df[(df['year'].isin(selected_year))]
        country_count = dff_c['country'].nunique()
    elif selected_region:
        dff_c = df[(df['region'].isin(selected_region))]
        country_count = dff_c['country'].nunique()
    elif selected_country:
        dff_c = df[(df['country'].isin(selected_country))]
        country_count = dff_c['country'].nunique()
    elif selected_violence:
        dff_c = df[(df['type_of_violence'].isin(selected_violence))]
        country_count = dff_c['country'].nunique()
    else:
        country_count = df['country'].nunique()
    return [html.Span("Total countries"), html.Span(country_count)]

# CONFLICTS CARD
@app.callback(
    Output('conflict-count-card', 'children'),
    Input('submit-btn-wcf', 'n_clicks'),
    State('year-variable', 'value'),
    State('region-variable', 'value'),
    State('country-variable', 'value'),
    State('violence-variable', 'value')
)
def update_conflict_count_count(_, selected_year, selected_region, selected_country, selected_violence):
    if selected_year and selected_region and selected_country and selected_violence:
        dff_cc = df[(df['year'].isin(selected_year)) & (df['region'].isin(selected_region)) & (df['country'].isin(selected_country)) & (df['type_of_violence'].isin(selected_violence))]
        conflict_count = dff_cc['id'].count()
    elif selected_year and selected_region and selected_country:
        dff_cc = df[(df['year'].isin(selected_year)) & (df['region'].isin(selected_region)) & (df['country'].isin(selected_country))]
        conflict_count = dff_cc['id'].count()
    elif selected_year and selected_region and selected_violence:
        dff_cc = df[(df['year'].isin(selected_year)) & (df['region'].isin(selected_region)) & (df['type_of_violence'].isin(selected_violence))]
        conflict_count = dff_cc['id'].count()
    elif selected_year and selected_region:
        dff_cc = df[(df['year'].isin(selected_year)) & (df['region'].isin(selected_region))]
        conflict_count = dff_cc['id'].count()
    elif selected_year and selected_violence:
        dff_cc = df[(df['year'].isin(selected_year)) & (df['type_of_violence'].isin(selected_violence))]
        conflict_count = dff_cc['id'].count()
    elif selected_region and selected_country:
        dff_cc = df[(df['region'].isin(selected_region)) & (df['country'].isin(selected_country))]
        conflict_count = dff_cc['id'].count()
    elif selected_region and selected_violence:
        dff_cc = df[(df['region'].isin(selected_region)) & (df['type_of_violence'].isin(selected_violence))]
        conflict_count = dff_cc['id'].count()
    elif selected_year:
        dff_cc = df[df['year'].isin(selected_year)]
        conflict_count = dff_cc['id'].count()
    elif selected_region:
        dff_cc = df[df['region'].isin(selected_region)]
        conflict_count = dff_cc['id'].count()
    elif selected_country:
        dff_cc = df[df['country'].isin(selected_country)]
        conflict_count = dff_cc['id'].count()
    elif selected_violence:
        dff_cc = df[df['type_of_violence'].isin(selected_violence)]
        conflict_count = dff_cc['id'].count()
    else:
        conflict_count = df['id'].count()
    return [html.Span("Total conflicts"), html.Span(conflict_count)]

# FATALITIES CARD
@app.callback(
    Output('fatality-sum-card', 'children'),
    Input('submit-btn-wcf', 'n_clicks'),
    State('year-variable', 'value'),
    State('region-variable', 'value'),
    State('country-variable', 'value'),
    State('violence-variable', 'value')
)
def update_fatality_sum_count(_, selected_year, selected_region, selected_country, selected_violence):
    if selected_year and selected_region and selected_country and selected_violence:
        dff_f = df[(df['year'].isin(selected_year)) & (df['region'].isin(selected_region)) & (df['country'].isin(selected_country)) & (df['type_of_violence'].isin(selected_violence))]
        fatality_count = dff_f['best'].sum()
    elif selected_year and selected_region and selected_country:
        dff_f = df[(df['year'].isin(selected_year)) & (df['region'].isin(selected_region)) & (df['country'].isin(selected_country))]
        fatality_count = dff_f['best'].sum()
    elif selected_year and selected_region and selected_violence:
        dff_f = df[(df['year'].isin(selected_year)) & (df['region'].isin(selected_region)) & (df['type_of_violence'].isin(selected_violence))]
        fatality_count = dff_f['best'].sum()
    elif selected_year and selected_region:
        dff_f = df[(df['year'].isin(selected_year)) & (df['region'].isin(selected_region))]
        fatality_count = dff_f['best'].sum()
    elif selected_year and selected_violence:
        dff_f = df[(df['year'].isin(selected_year)) & (df['type_of_violence'].isin(selected_violence))]
        fatality_count = dff_f['best'].sum()
    elif selected_region and selected_country:
        dff_f = df[(df['region'].isin(selected_region)) & (df['country'].isin(selected_country))]
        fatality_count = dff_f['best'].sum()
    elif selected_region and selected_violence:
        dff_f = df[(df['region'].isin(selected_region)) & (df['type_of_violence'].isin(selected_violence))]
        fatality_count = dff_f['best'].sum()
    elif selected_year:
        dff_f = df[df['year'].isin(selected_year)]
        fatality_count = dff_f['best'].sum()
    elif selected_region:
        dff_f = df[df['region'].isin(selected_region)]
        fatality_count = dff_f['best'].sum()
    elif selected_country:
        dff_f = df[df['country'].isin(selected_country)]
        fatality_count = dff_f['best'].sum()
    elif selected_violence:
        dff_f = df[df['type_of_violence'].isin(selected_violence)]
        fatality_count = dff_f['best'].sum()
    else:
        fatality_count = df['best'].sum()
    return [html.Span("Total fatalities"), html.Span(fatality_count)]

# WORLDWIDE CONFLICTS AND FATALITIES TREEMAP CHART
@app.callback(
    Output('wcf-chart', 'figure'),
    Input('submit-btn-wcf', 'n_clicks'),
    State('year-variable', 'value'),
    State('region-variable', 'value'),
    State('country-variable', 'value'),
    State('violence-variable', 'value')
)
def update_wcf_chart(_, selected_year, selected_region, selected_country, selected_violence):
    if selected_year and selected_region and selected_country and selected_violence:
        dff_wcf = df[(df['year'].isin(selected_year)) & (df['region'].isin(selected_region)) & (df['country'].isin(selected_country)) & (df['type_of_violence'].isin(selected_violence))]
    elif selected_year and selected_region and selected_country:
        dff_wcf = df[(df['year'].isin(selected_year)) & (df['region'].isin(selected_region)) & (df['country'].isin(selected_country))]
    elif selected_year and selected_region and selected_violence:
        dff_wcf = df[(df['year'].isin(selected_year)) & (df['region'].isin(selected_region)) & (df['type_of_violence'].isin(selected_violence))]
    elif selected_year and selected_region:
        dff_wcf = df[(df['year'].isin(selected_year)) & (df['region'].isin(selected_region))]
    elif selected_year and selected_violence:
        dff_wcf = df[(df['year'].isin(selected_year)) & (df['type_of_violence'].isin(selected_violence))]
    elif selected_region and selected_country:
        dff_wcf = df[(df['region'].isin(selected_region)) & (df['country'].isin(selected_country))]
    elif selected_region and selected_violence:
        dff_wcf = df[(df['region'].isin(selected_region)) & (df['type_of_violence'].isin(selected_violence))]
    elif selected_year:
        dff_wcf = df[(df['year'].isin(selected_year))]
    elif selected_region:
        dff_wcf = df[(df['region'].isin(selected_region))]
    elif selected_country:
        dff_wcf = df[(df['country'].isin(selected_country))]
    elif selected_violence:
        dff_wcf = df[(df['type_of_violence'].isin(selected_violence))]
    else:
        dff_wcf = df
    wcf = dff_wcf.groupby(['region', 'country']).agg(
        conflicts=pd.NamedAgg(column='id', aggfunc='count'),
        total_fatalities=pd.NamedAgg(column='best', aggfunc='sum')
        ).reset_index()
    if wcf['conflicts'].sum() == 0:
        fig_wcf = go.Figure()
        fig_wcf.add_annotation(
            text="No data to display that's why the cards aren't updated",
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=20)
        )
    else:
        fig_wcf = px.treemap(
            wcf,
            path=[px.Constant("world"), 'region', 'country'],
            values='conflicts',
            color='total_fatalities',
            color_continuous_scale='balance',
            color_continuous_midpoint=np.average(wcf['total_fatalities'], weights=wcf['conflicts']),
            labels={'region': 'Region', 'country': 'Country', 'conflicts': 'No. of conflicts', 'total_fatalities': 'Total fatalities'}
        )
        fig_wcf.update_traces(marker=dict(cornerradius=5))
    return fig_wcf

# TYPE OF VIOLENCE DISTRIBUTION PIE CHART
@app.callback(
    Output('tov-chart', 'figure'),
    Input('submit-btn-fo', 'n_clicks'),
    State('year-variable', 'value'),
    State('region-variable', 'value'),
    State('country-variable', 'value'),
    State('violence-variable', 'value')
)
def update_tov_chart(_, selected_year, selected_region, selected_country, selected_violence):
    if selected_year and selected_region and selected_country and selected_violence:
        dff_tov = df[(df['year'].isin(selected_year)) & (df['region'].isin(selected_region)) & (df['country'].isin(selected_country)) & (df['type_of_violence'].isin(selected_violence))]
    elif selected_year and selected_region and selected_country:
        dff_tov = df[(df['year'].isin(selected_year)) & (df['region'].isin(selected_region)) & (df['country'].isin(selected_country))]
    elif selected_year and selected_region and selected_violence:
        dff_tov = df[(df['year'].isin(selected_year)) & (df['region'].isin(selected_region)) & (df['type_of_violence'].isin(selected_violence))]
    elif selected_year and selected_region:
        dff_tov = df[(df['year'].isin(selected_year)) & (df['region'].isin(selected_region))]
    elif selected_year and selected_violence:
        dff_tov = df[(df['year'].isin(selected_year)) & (df['type_of_violence'].isin(selected_violence))]
    elif selected_region and selected_country:
        dff_tov = df[(df['region'].isin(selected_region)) & (df['country'].isin(selected_country))]
    elif selected_region and selected_violence:
        dff_tov = df[(df['region'].isin(selected_region)) & (df['type_of_violence'].isin(selected_violence))]
    elif selected_year:
        dff_tov = df[(df['year'].isin(selected_year))]
    elif selected_region:
        dff_tov = df[(df['region'].isin(selected_region))]
    elif selected_country:
        dff_tov = df[(df['country'].isin(selected_country))]
    elif selected_violence:
        dff_tov = df[(df['type_of_violence'].isin(selected_violence))]
    else:
        dff_tov = df
    if dff_tov.empty:
        fig_tov = go.Figure()
        fig_tov.add_annotation(
            text="No data to display",
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=20)
        )
    else:
        fig_tov = px.pie(
            dff_tov,
            names='type_of_violence',
            values='best',
            color='type_of_violence',
            color_discrete_map={
                'State-based conflict': px.colors.qualitative.Dark2[6],
                'Non-state conflict': px.colors.qualitative.Dark2[1],
                'One-sided violence': px.colors.qualitative.Dark2[2]
            },
            labels={'type_of_violence': 'Type of violence', 'best': 'Total fatalities'},
            title="Total fatalities by violence"
        )
        fig_tov.update_layout(
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=-0.05
            )
        )
    return fig_tov

# TOP 10 COUNTRIES BASED ON FATALITIES COUNT BAR CHART
@app.callback(
    Output('fc-chart', 'figure'),
    Input('submit-btn-fo', 'n_clicks'),
    State('year-variable', 'value'),
    State('region-variable', 'value'),
    State('country-variable', 'value'),
    State('violence-variable', 'value')
)
def update_fc_chart(_, selected_year, selected_region, selected_country, selected_violence):
    if selected_year and selected_region and selected_country and selected_violence:
        dff_fc = df[(df['year'].isin(selected_year)) & (df['region'].isin(selected_region)) & (df['country'].isin(selected_country)) & (df['type_of_violence'].isin(selected_violence))]
    elif selected_year and selected_region and selected_country:
        dff_fc = df[(df['year'].isin(selected_year)) & (df['region'].isin(selected_region)) & (df['country'].isin(selected_country))]
    elif selected_year and selected_region and selected_violence:
        dff_fc = df[(df['year'].isin(selected_year)) & (df['region'].isin(selected_region)) & (df['type_of_violence'].isin(selected_violence))]
    elif selected_year and selected_region:
        dff_fc = df[(df['year'].isin(selected_year)) & (df['region'].isin(selected_region))]
    elif selected_year and selected_violence:
        dff_fc = df[(df['year'].isin(selected_year)) & (df['type_of_violence'].isin(selected_violence))]
    elif selected_region and selected_country:
        dff_fc = df[(df['region'].isin(selected_region)) & (df['country'].isin(selected_country))]
    elif selected_region and selected_violence:
        dff_fc = df[(df['region'].isin(selected_region)) & (df['type_of_violence'].isin(selected_violence))]
    elif selected_year:
        dff_fc = df[(df['year'].isin(selected_year))]
    elif selected_region:
        dff_fc = df[(df['region'].isin(selected_region))]
    elif selected_country:
        dff_fc = df[(df['country'].isin(selected_country))]
    elif selected_violence:
        dff_fc = df[(df['type_of_violence'].isin(selected_violence))]
    else:
        dff_fc = df
    if dff_fc.empty:
        fig_fc = go.Figure()
        fig_fc.add_annotation(
            text="No data to display",
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=20)
        )
    else:
        bar_data = dff_fc.groupby(['type_of_violence', 'region', 'country'])['best'].sum().reset_index()
        top_10_countries = bar_data.sort_values(by='best', ascending=False).head(10)
        fig_fc = px.bar(
            top_10_countries,
            x='country',
            y='best',
            color='type_of_violence',
            color_discrete_map={
                'State-based conflict': px.colors.qualitative.Dark2[6],
                'Non-state conflict': px.colors.qualitative.Dark2[1],
                'One-sided violence': px.colors.qualitative.Dark2[2]
            },
            category_orders={'country': top_10_countries['country'].tolist()},
            text_auto='.2s',
            hover_data=['type_of_violence','region', 'country', 'best'],
            labels={'best': 'Total fatalities', 'country': 'Country', 'type_of_violence': 'Type of violence', 'region': 'Region'},
            title="Top 10 countries by total fatalities"
        )
        fig_fc.update_xaxes(title_text="")
        fig_fc.update_yaxes(title_text="")
        fig_fc.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
        fig_fc.update_layout(showlegend=False)
    return fig_fc

# FATALITIES THRESHOLD DONUT CHARTS
@app.callback(
    Output('ft-chart', 'figure'),
    Input('submit-btn-fo', 'n_clicks'),
    State('year-variable', 'value'),
    State('region-variable', 'value'),
    State('country-variable', 'value'),
    State('violence-variable', 'value')
)
def update_ft_chart(_, selected_year, selected_region, selected_country, selected_violence):
    if selected_year and selected_region and selected_country and selected_violence:
        dff_ft = df[(df['year'].isin(selected_year)) & (df['region'].isin(selected_region)) & (df['country'].isin(selected_country)) & (df['type_of_violence'].isin(selected_violence))]
    elif selected_year and selected_region and selected_country:
        dff_ft = df[(df['year'].isin(selected_year)) & (df['region'].isin(selected_region)) & (df['country'].isin(selected_country))]
    elif selected_year and selected_region and selected_violence:
        dff_ft = df[(df['year'].isin(selected_year)) & (df['region'].isin(selected_region)) & (df['type_of_violence'].isin(selected_violence))]
    elif selected_year and selected_region:
        dff_ft = df[(df['year'].isin(selected_year)) & (df['region'].isin(selected_region))]
    elif selected_year and selected_violence:
        dff_ft = df[(df['year'].isin(selected_year)) & (df['type_of_violence'].isin(selected_violence))]
    elif selected_region and selected_country:
        dff_ft = df[(df['region'].isin(selected_region)) & (df['country'].isin(selected_country))]
    elif selected_region and selected_violence:
        dff_ft = df[(df['region'].isin(selected_region)) & (df['type_of_violence'].isin(selected_violence))]
    elif selected_year:
        dff_ft = df[(df['year'].isin(selected_year))]
    elif selected_region:
        dff_ft = df[(df['region'].isin(selected_region))]
    elif selected_country:
        dff_ft = df[(df['country'].isin(selected_country))]
    elif selected_violence:
        dff_ft = df[(df['type_of_violence'].isin(selected_violence))]
    else:
        dff_ft = df 
    if dff_ft.empty:
        fig_ft = go.Figure()
        fig_ft.add_annotation(
            text="No data to display",
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=20)
        )
    else:
        fig_ft = make_subplots(
            rows=1, 
            cols=2, 
            specs=[[{'type':'domain'}, {'type':'domain'}]], 
            subplot_titles=['Over 25 fatalities', 'Under 25 fatalities']
        )
        fig_ft.add_trace(
            go.Pie(
                labels=dff_ft['region'][dff_ft['active_year'] == "Over 25 fatalities"], 
                values=dff_ft['best'][dff_ft['active_year'] == "Over 25 fatalities"], 
                name=">25"
            ), row=1, col=1
        )
        fig_ft.add_trace(
            go.Pie(
                labels=dff_ft['region'][dff_ft['active_year'] == "Under 25 fatalities"], 
                values=dff_ft['best'][dff_ft['active_year'] == "Under 25 fatalities"], 
                name="<25"
            ), row=1, col=2
        )
        fig_ft.update_traces(
            hole=0.4,
            hoverinfo="label+percent+name",
            textinfo="value"
        )
        fig_ft.update_layout(
            title_text="Fatalities threshold ", 
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5)
        )
    return fig_ft

# TYPE OF FATALITIES DISTRIBUTION PIE AND BAR CHARTS
@app.callback(
    Output('tof-chart', 'figure'),
    Input('submit-btn-fd', 'n_clicks'),
    State('year-variable', 'value'),
    State('region-variable', 'value'),
    State('country-variable', 'value'),
    State('violence-variable', 'value')
)
def update_tof_chart(_, selected_year, selected_region, selected_country, selected_violence):
    if selected_year and selected_region and selected_country and selected_violence:
        dff_tof = df[(df['year'].isin(selected_year)) & (df['region'].isin(selected_region)) & (df['country'].isin(selected_country)) & (df['type_of_violence'].isin(selected_violence))]
    elif selected_year and selected_region and selected_country:
        dff_tof = df[(df['year'].isin(selected_year)) & (df['region'].isin(selected_region)) & (df['country'].isin(selected_country))]
    elif selected_year and selected_region and selected_violence:
        dff_tof = df[(df['year'].isin(selected_year)) & (df['region'].isin(selected_region)) & (df['type_of_violence'].isin(selected_violence))]
    elif selected_year and selected_region:
        dff_tof = df[(df['year'].isin(selected_year)) & (df['region'].isin(selected_region))]
    elif selected_year and selected_violence:
        dff_tof = df[(df['year'].isin(selected_year)) & (df['type_of_violence'].isin(selected_violence))]
    elif selected_region and selected_country:
        dff_tof = df[(df['region'].isin(selected_region)) & (df['country'].isin(selected_country))]
    elif selected_region and selected_violence:
        dff_tof = df[(df['region'].isin(selected_region)) & (df['type_of_violence'].isin(selected_violence))]
    elif selected_year:
        dff_tof = df[(df['year'].isin(selected_year))]
    elif selected_region:
        dff_tof = df[(df['region'].isin(selected_region))]
    elif selected_country:
        dff_tof = df[(df['country'].isin(selected_country))]
    elif selected_violence:
        dff_tof = df[(df['type_of_violence'].isin(selected_violence))]
    else:
        dff_tof = df
    tof = dff_tof.groupby(['region', 'country']).agg(
        conflicts=pd.NamedAgg(column='id', aggfunc='count'),
        side_a_fatalities=pd.NamedAgg(column='deaths_a', aggfunc='sum'),
        side_b_fatalities=pd.NamedAgg(column='deaths_b', aggfunc='sum'),
        civilians_fatalities=pd.NamedAgg(column='deaths_civilians', aggfunc='sum'),
        unknown_fatalities=pd.NamedAgg(column='deaths_unknown', aggfunc='sum'),
        total_fatalities=pd.NamedAgg(column='best', aggfunc='sum')
        ).reset_index()
    if dff_tof.empty:
        fig_tof = go.Figure()
        fig_tof.add_annotation(
            text="No data to display",
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=20)
        )
    else:
        fig_tof = make_subplots(
            rows=4, 
            cols=2, 
            column_widths=[0.3, 0.7], 
            subplot_titles=['Conflicts by region', 'First-party fatalities', 'Second-party fatalities', 'Civilian fatalities', 'Unknown fatalities'],
            specs=[
                [{"type": "domain", "rowspan": 4}, {"type": "xy"}],
                [None, {"type": "xy"}],
                [None, {"type": "xy"}],
                [None, {"type": "xy"}]
                ]
        )
        fig_tof.add_trace(
            go.Pie(
                labels=tof['region'], 
                values=tof['conflicts'], 
                name="Conflicts", 
                textinfo='label+percent', 
                insidetextorientation='radial', 
                showlegend=False
            ), row=1, col=1
        )
        top_10_side_a = tof.nlargest(10, 'side_a_fatalities')
        fig_tof.add_bar(
            x=top_10_side_a['country'], 
            y=top_10_side_a['side_a_fatalities'], 
            marker=dict(color="rgb(102,17,0)"), 
            name="First party fatalities", 
            showlegend=False, 
            text=top_10_side_a['side_a_fatalities'], 
            textposition='auto', 
            texttemplate='%{text:.2s}',
            hovertemplate='Region: %{customdata[0]}<br>Conflicts: %{customdata[1]}<br>First-party fatalities: %{y}',
            customdata=top_10_side_a[['region', 'conflicts']].values,
            row=1, 
            col=2
        )
        top_10_side_b = tof.nlargest(10, 'side_b_fatalities')
        fig_tof.add_bar(
            x=top_10_side_b['country'], 
            y=top_10_side_b['side_b_fatalities'], 
            marker=dict(color="rgb(136,34,85)"), 
            name="Second party fatalities", 
            showlegend=False, 
            text=top_10_side_b['side_b_fatalities'], 
            textposition='auto', 
            texttemplate='%{text:.2s}',
            hovertemplate='Region: %{customdata[0]}<br>Conflicts: %{customdata[1]}<br>Second-party fatalities: %{y}',
            customdata=top_10_side_b[['region', 'conflicts']].values,
            row=2, 
            col=2
        )
        top_10_civilians = tof.nlargest(10, 'civilians_fatalities')
        fig_tof.add_bar(
            x=top_10_civilians['country'], 
            y=top_10_civilians['civilians_fatalities'], 
            marker=dict(color="rgb(231,63,116)"), 
            name="Civilians fatalities", 
            showlegend=False, 
            text=top_10_civilians['civilians_fatalities'], 
            textposition='auto', 
            texttemplate='%{text:.2s}',
            hovertemplate='Region: %{customdata[0]}<br>Conflicts: %{customdata[1]}<br>Civilian fatalities: %{y}',
            customdata=top_10_civilians[['region', 'conflicts']].values,
            row=3, 
            col=2
        )
        top_10_unknown = tof.nlargest(10, 'unknown_fatalities')
        fig_tof.add_bar(
            x=top_10_unknown['country'], 
            y=top_10_unknown['unknown_fatalities'], 
            marker=dict(color="rgb(0,134,149)"), 
            name="Unknown fatalities", 
            showlegend=False, 
            text=top_10_unknown['unknown_fatalities'], 
            textposition='auto', 
            texttemplate='%{text:.2s}',
            hovertemplate='Region: %{customdata[0]}<br>Conflicts: %{customdata[1]}<br>Unknown fatalities: %{y}',
            customdata=top_10_unknown[['region', 'conflicts']].values,
            row=4, 
            col=2
        )
        fig_tof.update_layout(height=1000)
    return fig_tof

if __name__ == '__main__':
    app.run_server(debug=True)
