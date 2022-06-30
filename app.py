from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc
from datetime import timedelta

# Haritalar için GeoJson bilgilerini almak için gerekli kütüphaneler
from urllib.request import urlopen
import json

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# dataFramelerin düzenlenmesi
df = pd.read_csv("ilceler.csv")
df_tum_il = df.groupby("il").sum().reset_index()


app.layout = dbc.Container(html.Div(children=[
    html.H1(children='Türkiye Konut Satış Verileri - İnteraktif', className="mt-5"),
    html.Hr(),

    html.Div([
        html.H3(children="Yıllara Göre Konut Satışları Haritası"),

        dbc.Spinner(dcc.Graph(id='harita-yillik'), size="lg", color="rgb(227, 96, 11)"),
        dcc.Slider(
            df['yil'].min(),
            df['yil'].max(),
            step=None,
            value=2015,
            marks={str(yil): str(yil) for yil in df['yil'].unique()},
            id='yil-slider',
            className="mt-3"
        )
    ]),

    html.Hr(),

    html.Div([
        html.H3(children="İlçelere Göre Konut Satış Sayıları", className="mb-3"),
        dbc.Row([
            dbc.Col(
                [dbc.Label("İl Seçiniz"),
                 dcc.Dropdown(
                    df['il'].unique(),
                    value="Ankara",
                    id='il-secim'
                )]),
            dbc.Col(
                [dbc.Label("Yıl Seçiniz"),
                 dcc.Dropdown(
                    df['yil'].unique(),
                    value=2015,
                    id='yil-secim'
                )]),
        ])
    ]),

    dbc.Spinner(dcc.Graph(id='ilceler'), size="lg", color="rgb(227, 96, 11)"),

    html.Hr(),

   
]))


# Yıllara Göre Konut Satışları Haritası
@app.callback(
    Output('harita-yillik', 'figure'),
    Input('yil-slider', 'value'))
def update_figure(selected_yil):
    filtered_df = df[df.yil == selected_yil]

    with urlopen('https://raw.githubusercontent.com/cihadturhan/tr-geojson/master/geo/tr-cities-utf8.json') as response:
        geojson = json.load(response)
    geojson["features"][2]["properties"] = {'name': 'Afyonkarahisar'}

    fig = px.choropleth_mapbox(filtered_df.groupby(["yil", "il"]).sum().reset_index(), geojson=geojson, color="satis",
                               locations="il", featureidkey="properties.name",
                               center={"lat": 39, "lon": 35.5},
                               opacity=.6,
                               mapbox_style="carto-positron", zoom=4.7,
                               color_continuous_scale=["White", "Green", "Red"])
    fig.update_layout(margin={"t": 0, "b": 0, "l": 0}, transition_duration=500)
    return fig


# İlçelere Göre Konut Satış Sayıları
@app.callback(
    Output('ilceler', 'figure'),
    Input('il-secim', 'value'),
    Input('yil-secim', 'value'))
def update_figure(selected_il, selected_yil):
    filtered_df = df[df.il == selected_il]
    filtered_df = filtered_df[filtered_df.yil == selected_yil]

    fig = px.bar(filtered_df.groupby(["ilce"]).sum().reset_index().sort_values(by="satis"),
                 x="satis", y='ilce', orientation='h', labels={'satis': 'Satış Sayıları', 'ilce': 'İlçeler'})
    fig.update_traces(marker_color="rgba(227, 96, 11, 0.93)",
                      hoverlabel_bgcolor="rgba(49, 100, 150, 0.8)")
    fig.update_layout(plot_bgcolor="white")
    fig.update_xaxes(gridcolor="rgb(230,230,230)")
    fig.update_yaxes(gridcolor="rgb(230,230,230)")

    return fig




if __name__ == '__main__':
    app.run_server(debug=True)
