import json
import plotly.graph_objects as go
from app.data_sources.yahoo import get_stock_history


def get_chart(symbol: str):
    history = get_stock_history(symbol)

    fig = go.Figure()

    # Bezpieczne wyciągnięcie osi X (Date/index)
    x_data = history["Date"] if "Date" in history.columns else history.index

    fig.add_trace(
        go.Scatter(
            x=x_data,
            y=history["Close"],
            mode="lines",
            name=symbol.upper()
        )
    )

    fig.update_layout(
        title=f"{symbol.upper()} - ostatni miesiąc",
        xaxis_title="Data",
        yaxis_title="Cena",
        template="plotly_white"
    )

    # 1. Konwertujemy figurę za pomocą wbudowanego, bezpiecznego enkodera Plotly
    chart_json_str = fig.to_json()
    
    # 2. Parsujemy tekst JSON na standardowy słownik Pythona (bez obiektów Numpy/Pandas)
    return json.loads(chart_json_str)