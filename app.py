#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import os
import io

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table as dt
import dash_bootstrap_components as dbc
from dash_extensions import Download
from dash_extensions.snippets import send_data_frame
import pybso.core as core
import pybso.charts as charts
#from plotly.offline import plot
import pandas as pd

FA = "https://use.fontawesome.com/releases/v5.12.1/css/all.css"
external_stylesheets = [dbc.themes.FLATLY,FA]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions'] = True

# STYLES
## the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 80,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}
## the styles for the main content position in data tab
CONTENT_STYLE_WITH_SIDEBAR = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}
## the styles for the main content without sidebar
CONTENT_STYLE = {
    "margin-left": "2rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}
FOOTER_STYLE = {
     "background-color": "grey",

}
# COMPONENTS VARIABLES
## Nav item links
nav_items = dbc.Nav(
    [
        dbc.NavLink("Données", href="/data", active="exact"),
        dbc.NavLink("Visualisations", href="/viz", active="exact"),
        dbc.NavLink("A propos", href="/", active="exact"),
    ]
)

## [Unused] sidebar
sidebar = html.Div(
    [
        html.H2("Menu", className="display-4"),
        html.Hr(),
        html.P(
            "A simple sidebar layout with navigation links", className="lead"
        ),
       dbc.Nav(
        [
          dbc.NavLink("Data", href="/data", active="exact"),
          dbc.NavLink("Viz", href="/viz", active="exact"),
          dbc.NavLink("About", href="/", active="exact"),
        ],
        vertical=True,
        pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

## navbar
navbar = dbc.Navbar(children=[dbc.NavbarBrand("Self OA Baromètre"),nav_items], sticky="top",color="primary",dark=True,)
## footer
footer = dbc.Row(
          [
            html.P(
                [
                    html.Span('Géraldine Geoffroy', className='mr-4'), 
                    html.A(html.I(className='fas fa-envelope-square mr-1'), href='mailto:geraldine.geoffroy@univ-cotedazur.fr'), 
                    html.A(html.I(className='fab fa-github-square mr-1'), href='https://github.com/gegedenice'),  
                ], 
                className='lead',
            )
        ],justify="center",align="center",style=FOOTER_STYLE,)

# COMPONENTS FUNCTIONS
## drag&drop upload div
def render_upload(id):
    return dcc.Upload(
            id=id,
            children=html.Div(
                ["Glisser-déposer ou cliquer pour importer un fichier au format csv (séparateur indifférent), json ou Excel"]
                    ),
            style={
            "width": "100%",
            "height": "60px",
            "lineHeight": "60px",
            "borderWidth": "1px",
            "borderStyle": "dashed",
            "borderRadius": "5px",
            "textAlign": "center",
            "margin": "10px",
                   },
            multiple=True,
     )
## datatable
def render_datatable(id):
    return html.Div(dt.DataTable(
            id=id,
            sort_action="native",
            sort_mode="multi",
            page_action="native",
            page_current=0,
            page_size=10,
            style_table={'overflowX': 'auto'},
            style_header={'backgroundColor': 'rgb(30, 30, 30)'},
            style_cell={
                'backgroundColor': 'rgb(50, 50, 50)',
                'color': 'white',
                'textAlign': 'left',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
                'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',},
            #export_format="csv",
            )
            )
## card for chart
def render_graph_card(id,title):
    return dbc.Card(
    [
        dbc.CardHeader(title),
        dbc.CardBody(
            [
                dcc.Graph(id=id),
            ]
        ),
        dbc.CardFooter(

        ),
    ],
    color="primary", inverse=True
)

# PAGES CONTENT
## about page     
about_content = html.Div([html.H3("A propos de cette application"),
                   html.Hr(),
                   dcc.Markdown('''

Cette application est un exemple d'implémentation du package Python [pybso](https://pypi.org/project/pybso/) dans une application web.
Elle permet de construire un baromètre de Science ouverte local avec son propre corpus de DOI, sur le modèle du baromètre national. 

La page [Données](/data) propose d'importer votre fichier source de DOI et de 
- moissonner les caractéristiques OA de chaque DOI via l'API d'Unpaywall. Le résultat renvoie votre fichier en entrée augmenté des données suivantes :
  - données Unpaywall brutes : "title", "genre" (type de publication), "published_date", "year", "journal_name", "journal_issn_l" ,"journal_is_oa" , "journal_is_in_doaj" ,"publisher" ;
  - données reconstruites (voir la [documentation du package]()): 
    - "is_oa_normalized" : Accès ouvert / Accès fermé
    - "oa_status_normalized" : Green, Gold, Bronze, Hybrid
    - "oa_host_type_normalized" : Archive ouverte, Editeur, Editeur et archive ouverte
    - "oa_host_domain" : les noms de domaines concaténés de tous les plateformes d'hébergement du document
- récupérer si vous le souhaitez les noms des éditeurs plus homogénéisés en interrogeant [l'API Crossref prefixes]. Le résultat renvoie votre fichier en entrée augmenté des données suivantes :
  - "doi_prefix"
  - "publisher_by_doiprefix" : le libellé éditeur obtenu à partir des préfixes de DOI
- télécharger vos résultats en format csv, Json ou Excel.

Une fois les données OA récupérées, la page [Visualisations](/viz) permet d'importer à son tour votre fichier résultat et affiche les graphiques du baromètre.

Cette application est réalisée avec le framework Python d'application web Dash, qui est lui-même construit sur Flask, Plotly et React.

Pour une installation en local, le code source est accessible ici : [https://github.com/gegedenice/self-oa-barometre](https://github.com/gegedenice/self-oa-barometre)
'''),])
## data harvest page
data_content = html.Div([html.H3("Obtenir les données OA"),
                   html.Hr(),
                   dbc.Row(
              [
                dbc.Col(
                    html.H4("1. Importer un fichier de DOI"),
                    width={"size": 9},
                ),
                dbc.Col(
                    dbc.Col(dbc.Button("Effacer",color="danger",block=True,id="reset",className="mb-3",href="/data")),
                    width={"size": 3},
                ),
              ]),
                   dbc.FormGroup(
                    [#dbc.Label("Upload source file", html_for="upload-data"),
                     render_upload("upload-data"),
                     dbc.FormText(
                       "Le fichier peut contenir plusieurs colonnes/entrées mais doit avoir au minimum une colonne/entrée de DOI avec l'en-tête 'doi'",
                       color="secondary",
                        )
                        ]),
                    html.Div(id="import-error"),
                    render_datatable("table-data"),
                    html.Hr(),
                    html.H4("2. Enrichir les données"),
                    dbc.Row([
                      dbc.Button("Avec les données OA d'Unpaywall",color="primary",block=True,id="unpaywall_button",className="mb-3",n_clicks=0),
                     ]),
                    dbc.Row([html.P("OU")], align="center", justify="center",className="h-50"),
                    dbc.Row([
                      dbc.Col(dbc.Input(id="email", placeholder="Entrer une adresse mail valide...", type="email"),width=6),
                      dbc.Col(dbc.Button("Avec les libellés éditeurs de Crossref",color="primary",block=True,id="crossref_button",className="mb-3"),width=6),
                     ]),
                    #html.Div(id='intermediate-source-value', style={'display': 'none'}),
                    dcc.Store(id="intermediate-source-value"),
                    html.Hr(),
                    html.H4("3. Sauvegarder les résultats"),
                    dbc.Spinner(html.Div(id="loading",
                                          children=[render_datatable("table-result"),
                                                    #html.Div(id='intermediate-result-value', style={'display': 'none'}),
                                                    dcc.Store(id="intermediate-result-value"),
                                                    dbc.Button("Download CSV", id="csvdownload", color="success", className="mr-1",n_clicks_timestamp='0'),
                                                    dbc.Button("Download Excel", id="xlsdownload", color="success", className="mr-1",n_clicks_timestamp='0'),
                                                    dbc.Button("Download Json", id="jsondownload", color="success", className="mr-1",n_clicks_timestamp='0'),
                                                    Download(id="download")]),
                                color="primary",
                     )
                  ])
## charts page
viz_content = html.Div([html.H3("Visualisations du baromètre"),
                   html.Hr(),
             dbc.Row(
              [
                dbc.Col(
                      dbc.FormGroup(
                    [#dbc.Label("Upload source file", html_for="upload-data"),
                     render_upload("data-all-charts"),
                     dbc.FormText(
                       "Importer un fichier avec les données issues d'Unpaywall. La mention éditeur de Crossref est facultative.",
                       color="secondary",
                        )]
                    ),
                    width={"size": 9},
                ),
                dbc.Col(
                    dbc.Col(dbc.Button("Effacer",color="danger",block=True,id="reset",className="mb-3",href="/viz")),
                    width={"size": 3},
                ),
              ]),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(children=[render_graph_card("oa_rate","Proportion des publications en accès ouvert")],width=12),
                ]
            ),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(children=[render_graph_card("oa_rate_by_year","Evolution du taux d'accès ouvert aux publications")],width=12),
                ]
            ),
             html.Hr(),
             dbc.Row(
                [
                    dbc.Col(children=[render_graph_card("oa_by_status","Part Open Access : Evolution du type d'accès ouvert")],width=6),
                    dbc.Col(children=[render_graph_card("oa_rate_by_type","Répartition des publications par type de publications et par accès")],width=6),
                ]
            ),
             html.Hr(),
            dbc.Row(
                [   dbc.Col(
                      dbc.FormGroup([
                       dbc.Label("Source du libellé éditeur", html_for="pub_source"),
                       dbc.RadioItems(options=[
                                       {"label": "Unpaywall", "value": "publisher"},
                                       {"label": "Crossref (valeurs normalisées)", "value": "publisher_by_doiprefix"}],
                                      value="publisher",
                                      id="pub_source",
                                      inline=True)]), width=4),
                    dbc.Col(
                      dbc.FormGroup([
                      dbc.Label("Nombre d'éditeurs à afficher : ", html_for="n_select"),
                      html.Span(id='slider-output'),
                      dcc.Slider(id="n_select", min=1, max=20, step=1, marks={
                        1: '1',
                        5: '5',
                        10: '10',
                        15: '15',
                        20: '20'
                           },value=10),
                      ]), width=6)
                ]
            ),
            dbc.Row(dbc.Col(children=[render_graph_card("oa_rate_by_publisher","Taux d'accès ouvert aux publications par éditeur")],width=12))
        ])

# LAYOUT
content = html.Div(id="page-content", style=CONTENT_STYLE)
app.layout = dbc.Container([navbar,dcc.Location(id="url"), content,footer],fluid=True)     

# CALLBACKS
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return about_content
    elif pathname == "/data":
        return data_content
    elif pathname == "/viz":
        return viz_content
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Non trouvée", className="text-danger"),
            html.Hr(),
            html.P(f"L'url {pathname} n'est pas reconnue..."),
        ]
    )

@app.callback(Output('table-data', 'columns'),
              Output('table-data', 'data'),
              Output('intermediate-source-value', 'data'),
              Output('import-error','children'),
              [Input('upload-data', 'contents'),
              Input('upload-data', 'filename')],
              prevent_initial_call=True)
def update_table(contents, filename):
    if contents is not None:
        content_type, content_string = contents[0].split(',')
        decoded = base64.b64decode(content_string)
        try:
            if 'csv' in filename[0]:
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            elif (('xlsx' in filename[0]) | ('xls' in filename[0])):
                df = pd.read_excel(io.BytesIO(decoded))
            elif 'json' in filename[0]:
                df = pd.read_json(io.StringIO(decoded.decode('utf-8')))
            try:
                if df['doi'].isnull().sum() != 0:
                    return None,None,None,dbc.Alert("Votre fichier contient des DOI vides !", color="danger")
            except:
                pass
            columns = [{"name": i, "id": i} for i in df.columns]
            data = df.to_dict('records')
            return columns, data, df.to_json(),None
        except Exception as e:
            print(e)
            return None,None,None,dbc.Alert("Le format de fichier n'est pas valide !", color="danger")

@app.callback(
    Output('table-result', 'columns'),
    Output('table-result', 'data'),
    Output('intermediate-result-value', 'data'),
    [Input('unpaywall_button', 'n_clicks'),Input('crossref_button', 'n_clicks'),Input('email', 'value')],
    [State("intermediate-source-value", "data")],
    prevent_initial_call=True)
def get_result(n_upw_clicks,n_crf_clicks,email,data):
    if n_upw_clicks != 0:
        dff = pd.read_json(data)
        df_result = core.unpaywall_data(dataframe=dff)
        columns = [{"name": i, "id": i} for i in df_result.columns]
        data = df_result.to_dict('records')
        return columns, data, df_result.to_json()
    if n_crf_clicks != None:
        dff = pd.read_json(data)
        df_result = core.crossref_publisher_data(dataframe=dff,email=email)
        columns = [{"name": i, "id": i} for i in df_result.columns]
        data = df_result.to_dict('records')
        return columns, data, df_result.to_json()

@app.callback(Output('oa_rate', 'figure'),
              Output('oa_rate_by_year', 'figure'),
              Output('oa_by_status', 'figure'),
              Output('oa_rate_by_type', 'figure'),
              Output('oa_rate_by_publisher', 'figure'),
              Output('slider-output', 'children'),
              [Input('data-all-charts', 'contents'),
              Input('data-all-charts', 'filename'),
              Input('pub_source', 'value'),
              Input('n_select', 'value'),],
              prevent_initial_call=True)
def all_charts(contents, filename,pub_value,n_value):
    if contents is not None:
        content_type, content_string = contents[0].split(',')
        decoded = base64.b64decode(content_string)
        try:
            if 'csv' in filename[0]:
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            if (('xls' in filename[0]) | ("xlsx" in filename[0])):
               df = pd.read_excel(io.BytesIO(decoded))
            if 'json' in filename[0]:
                df = pd.read_json(io.StringIO(decoded.decode('utf-8')))
            return charts.oa_rate(dataframe=df),charts.oa_rate_by_year(dataframe=df),charts.oa_by_status(dataframe=df),charts.oa_rate_by_type(dataframe=df),charts.oa_rate_by_publisher(dataframe=df,publisher_field=pub_value,n=int(n_value)),n_value
        except Exception as e:
            print(e)
            return dbc.Alert("Le format de fichier n'est pas valide !", color="danger"),None,None,None,None,n_value

@app.callback(Output("download", "data"), 
             [Input("csvdownload", "n_clicks_timestamp"),
             Input("xlsdownload", "n_clicks_timestamp"),
             Input("jsondownload", "n_clicks_timestamp")], 
             [State("intermediate-result-value", "data")],
             prevent_initial_call=True)
def download_table(csvdownload, xlsdownload,jsondownload, data):
    df = pd.read_json(data,orient="records")
    if int(csvdownload) > int(xlsdownload) and int(csvdownload) > int(jsondownload):
        return send_data_frame(df.to_csv, "data.csv", index=False)
    elif int(xlsdownload) > int(csvdownload) and int(xlsdownload) > int(jsondownload):
        return send_data_frame(df.to_excel, r"data.xlsx", index=False)
    elif int(jsondownload) > int(csvdownload) and int(jsondownload) > int(xlsdownload):
        return send_data_frame(df.to_json, "data.json", orient="records")

if __name__ == "__main__":
    app.run_server(debug=True)