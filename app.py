from flask import Flask, render_template
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlite3
import pandas as pd
import yfinance as yf
from datetime import datetime

# Flask app
server = Flask(__name__)

# Dash app
dash_app = dash.Dash(__name__, server=server, url_base_pathname='/dash/')

def get_data():
    conn = sqlite3.connect('btc_data.db')
    df = pd.read_sql_query("SELECT * FROM bitcoin_data", conn)
    conn.close()
    df['date'] = pd.to_datetime(df['date'])
    return df

# Dash layout - updated with date range slider without marks
dash_app.layout = html.Div([
    dcc.Graph(id='btc-graph', style={'height': '500px'}),
    html.Div([
        dcc.RangeSlider(
            id='date-slider',
            min=0,
            max=1,
            step=1,
            value=[0, 1],
            marks=None,  # Set marks to None to remove labels
            tooltip={"placement": "bottom", "always_visible": False, "format": "%Y-%m-%d"}
        )
    ], style={'margin': '20px 60px 40px 60px'})
])

# Updated callback to include the slider
@dash_app.callback(
    [Output('btc-graph', 'figure'),
     Output('date-slider', 'min'),
     Output('date-slider', 'max'),
     Output('date-slider', 'marks'),
     Output('date-slider', 'value'),
     Output('date-slider', 'tooltip')],
    [Input('date-slider', 'value')]
)
def update_graph(date_range):
    df = get_data()

    if date_range is None or date_range == [0, 1]:
        date_range = [0, len(df) - 1]

    df_filtered = df.iloc[date_range[0]:date_range[1]+1]

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Round portfolio value to 2 decimals when dividing by million
    fig.add_trace(
        go.Scatter(
            x=df_filtered['date'],
            y=(df_filtered['value_usd'] / 1_000_000).round(2),  # Round to 2 decimals
            name="Valor de Cartera (Millones USD)",
            line=dict(color="blue")
        ),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(
            x=df_filtered['date'],
            y=df_filtered['price_usd'].round(2),  # Round to 2 decimals
            name="Precio Bitcoin (USD)",
            line=dict(color="red")
        ),
        secondary_y=True
    )

    fig.update_layout(
        margin=dict(l=50, r=50, t=30, b=30),
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    # Update y-axis formats to show no decimals
    fig.update_yaxes(
        title_text="Valor de Cartera (Millones USD)",
        secondary_y=False,
        tickformat=",.0f",  # Changed to remove decimals
        separatethousands=True,
        gridcolor='lightgray'
    )

    fig.update_yaxes(
        title_text="Precio Bitcoin (USD)",
        secondary_y=True,
        tickformat=",.0f",  # Changed to remove decimals
        separatethousands=True,
        gridcolor='lightgray',
        showgrid=False
    )

    fig.update_xaxes(gridcolor='lightgray')

    # Update hover template to use dots
    fig.update_traces(
        hovertemplate='%{x}<br>' +
                      '$%{y:,.2f}'.replace(',', '.') +
                      '<extra>%{data.name}</extra>'
    )

    # Create marks for the slider
    total_days = len(df)
    step = max(total_days // 8, 1)
    marks = {}
    for i in range(0, total_days, step):
        date_str = df['date'].iloc[i].strftime('%Y-%m')
        marks[i] = {'label': date_str, 'style': {'transform': 'rotate(-45deg)'}}

    if total_days - 1 not in marks:
        date_str = df['date'].iloc[-1].strftime('%Y-%m')
        marks[total_days - 1] = {'label': date_str, 'style': {'transform': 'rotate(-45deg)'}}

    # Format the tooltip to show the selected date range
    tooltip = {
        'value': f"{df['date'].iloc[date_range[0]].strftime('%Y-%m-%d')} - {df['date'].iloc[date_range[1]].strftime('%Y-%m-%d')}"
    }

    return (
        fig,
        0,
        len(df) - 1,
        marks,
        date_range if date_range != [0, 1] else [0, len(df) - 1],
        tooltip  # Return the formatted tooltip
    )

def format_number(value):
    """Format number with dots as thousand separators"""
    return "{:,.0f}".format(value).replace(",", ".")

# Flask routes
@server.route('/')
def index():
    conn = sqlite3.connect('btc_data.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT price_usd, value_usd
        FROM bitcoin_data
        ORDER BY date DESC
        LIMIT 1
    ''')
    latest = cursor.fetchone()
    conn.close()

    if latest:
        current_price = latest[0]
        current_value = latest[1]
        # Update initial investment amount
        initial_investment = 292780000
        percent_increase = ((current_value/initial_investment) - 1) * 100
    else:
        current_price = 0
        current_value = 0
        percent_increase = 0

    return render_template('index.html',
                         current_price=current_price,
                         current_value=current_value,
                         percent_increase=percent_increase)

def update_latest_price():
    """Update only the latest day's price"""
    try:
        btc = yf.download('BTC-USD', period='1d')
        if btc.empty:
            return False

        latest_price = round(float(btc['Close'][-1]), 2)  # Round to 2 decimal places
        date_str = datetime.now().strftime('%Y-%m-%d')
        btc_amount = 472226
        value_usd = round(latest_price * btc_amount, 2)  # Round to 2 decimal places

        conn = sqlite3.connect('btc_data.db')
        cursor = conn.cursor()

        cursor.execute('''
        INSERT OR REPLACE INTO bitcoin_data (date, price_usd, value_usd)
        VALUES (?, ?, ?)
        ''', (date_str, latest_price, value_usd))

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        print(f"Error updating latest price: {e}")
        return False

if __name__ == '__main__':
    # Run the Flask app with Dash
    server.run(debug=True)
