import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import pickle
import dash_bootstrap_components as dbc

pickle_in = open('pitcher_classifier_model.pkl', 'rb')
model = pickle.load(pickle_in)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

navbar = dbc.Navbar(
    dbc.Container([
        dbc.NavbarBrand("Pitcher Role Classifier", href="/"),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("Pitcher Classifier", href="/pitcher_classifier", active="exact"),
            ],
            pills=True,
        ),
    ]),
    color="light",
    dark=False,
)

def serve_home_page():
    return html.Div([
        html.H1("Pitcher Cluster Model", style={"text-align": "center"}),
        html.P("This application predicts the pitcher cluster based on various input parameters.",
               style={"text-align": "center"}),
        html.P("The model uses machine learning to categorize pitchers into four clusters: Versatile Pitcher, "
               "Middle Reliever, Starting Pitcher, and Closer.", style={"text-align": "center"}),
    ], style={"padding": "40px"})

def serve_pitcher_classifier_page():
    return html.Div([
        html.H1("Pitcher Classifier", style={"text-align": "center"}),

        # Average Muscle Fatigue Calculator
        html.Div([
            html.H2("Average Muscle Fatigue Calculator"),
            dcc.Input(id='total_pitches', type='number', placeholder='Total Pitches', style={"width": "100%", "margin-bottom": "10px"}),
            dcc.Input(id='pace', type='number', placeholder='Average Pace', style={"width": "100%", "margin-bottom": "10px"}),
            dcc.Input(id='games_played', type='number', placeholder='Games Played', style={"width": "100%", "margin-bottom": "10px"}),
            html.Div(id='muscle_fatigue_output', style={"margin-top": "10px"})
        ], style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'top', 'padding': '10px'}),

        # Fatigue Units Calculator
        html.Div([
            html.H2("Fatigue Units Calculator"),
            dcc.Input(id='whip', type='number', placeholder='WHIP', style={"width": "100%", "margin-bottom": "10px"}),
            dcc.Input(id='bb_ip', type='number', placeholder='Walks per IP', style={"width": "100%", "margin-bottom": "10px"}),
            dcc.Input(id='k_ip', type='number', placeholder='Strikeouts per IP', style={"width": "100%", "margin-bottom": "10px"}),
            dcc.Input(id='batters_ip', type='number', placeholder='Batters Faced per IP', style={"width": "100%", "margin-bottom": "10px"}),
            dcc.Input(id='ip', type='number', placeholder='Innings Pitched', style={"width": "100%", "margin-bottom": "10px"}),
            dcc.Input(id='starting', type='number', placeholder='Games Started', style={"width": "100%", "margin-bottom": "10px"}),
            dcc.Input(id='relieving', type='number', placeholder='Games Relieved', style={"width": "100%", "margin-bottom": "10px"}),
            html.Div(id='fatigue_units_output', style={"margin-top": "10px"})
        ], style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'top', 'padding': '10px'}),

        # Predict Pitcher Cluster
        html.Div([
            html.H2("Predict Pitcher Cluster"),
            dcc.Input(id='average_rest_days', type='number', placeholder='Average Rest Days', style={"width": "100%", "margin-bottom": "10px"}),
            dcc.Input(id='fatigue_units_predict', type='number', placeholder='Fatigue Units', style={"width": "100%", "margin-bottom": "10px"}),
            dcc.Input(id='muscle_fatigue_predict', type='number', placeholder='Muscle Fatigue', style={"width": "100%", "margin-bottom": "10px"}),
            dcc.Input(id='games_played_predict', type='number', placeholder='Games Played', style={"width": "100%", "margin-bottom": "10px"}),
            dcc.Input(id='total_pitches_predict', type='number', placeholder='Total Pitches', style={"width": "100%", "margin-bottom": "10px"}),
            html.Button('Predict Cluster', id='predict_button', style={"width": "100%", "margin-top": "10px"}),
            html.Div(id='cluster_prediction', style={"margin-top": "10px"})
        ], style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'top', 'padding': '10px'})
    ], style={"padding": "20px"})

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content', style={"padding": "20px"})
])

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/':
        return serve_home_page()
    elif pathname == '/pitcher_classifier':
        return serve_pitcher_classifier_page()
    else:
        return serve_home_page()  # Redirect to home page for unknown URLs

@app.callback(
    Output('muscle_fatigue_output', 'children'),
    Input('total_pitches', 'value'),
    Input('pace', 'value'),
    Input('games_played', 'value')
)
def update_muscle_fatigue(total_pitches, pace, games_played):
    if all([total_pitches, pace, games_played]):
        muscle_fatigue = (0.10963 + 0.032 * total_pitches - 0.0023 * pace) / games_played
        return f"Calculated Muscle Fatigue: {muscle_fatigue:.2f}"
    return ""

@app.callback(
    Output('fatigue_units_output', 'children'),
    [
        Input('whip', 'value'),
        Input('bb_ip', 'value'),
        Input('k_ip', 'value'),
        Input('batters_ip', 'value'),
        Input('ip', 'value'),
        Input('starting', 'value'),
        Input('relieving', 'value')
    ]
)
def update_fatigue_units(whip, bb_ip, k_ip, batters_ip, ip, starting, relieving):
    if all([whip, bb_ip, k_ip, batters_ip, ip, starting, relieving]):
        fatigue_units = (
            0.18 * whip +
            0.14 * bb_ip +
            0.34 * k_ip -
            0.16 * batters_ip +
            0.08 * ip +
            0.3 * starting +
            0.14 * relieving
        )
        return f"Calculated Fatigue Units: {fatigue_units:.2f}"
    return ""

@app.callback(
    Output('cluster_prediction', 'children'),
    Input('predict_button', 'n_clicks'),
    Input('average_rest_days', 'value'),
    Input('fatigue_units_predict', 'value'),
    Input('muscle_fatigue_predict', 'value'),
    Input('games_played_predict', 'value'),
    Input('total_pitches_predict', 'value')
)
def predict_pitcher_cluster(n_clicks, average_rest_days, fatigue_units, muscle_fatigue, games_played, total_pitches):
    if n_clicks is not None:
        input_data = pd.DataFrame({
            'average_rest_days': [average_rest_days],
            'fatigue_units': [fatigue_units],
            'average_muscle_fatigue': [muscle_fatigue],
            'games_played': [games_played],
            'total_pitches': [total_pitches]
        })
        cluster_description = {
            0: "Versatile Pitcher",
            1: "Middle Reliever",
            2: "Starting Pitcher",
            3: "Closer"
        }
        cluster = model.predict(input_data)[0]
        predicted_cluster = cluster_description.get(cluster, "Unknown")
        return f"The predicted cluster is: {predicted_cluster}"
    return ""

if __name__ == '__main__':
    app.run_server(debug=True)