import requests

API_KEY = "67ab0a13aa3948e9b6c5f06198f8452d"  # Clave directa para pruebas

def obtener_indicadores_twelve(symbol, interval="15min"):
    symbol = symbol.upper().strip()

    url_base = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": symbol,
        "interval": interval,
        "outputsize": 5,
        "apikey": API_KEY
    }

    response = requests.get(url_base, params=params)
    data = response.json()

    if "values" not in data:
        return {"error": f"❌ Twelve Data respondió algo inesperado: {data}"}

    precios = [float(entry["close"]) for entry in data["values"]]

    # RSI
    url_rsi = "https://api.twelvedata.com/rsi"
    rsi_params = {
        "symbol": symbol,
        "interval": interval,
        "time_period": 14,
        "apikey": API_KEY
    }
    rsi = requests.get(url_rsi, params=rsi_params).json()
    rsi_valor = rsi.get("values", [{}])[0].get("rsi", "N/A")

    # EMA
    url_ema = "https://api.twelvedata.com/ema"
    ema_params = {
        "symbol": symbol,
        "interval": interval,
        "time_period": 20,
        "apikey": API_KEY
    }
    ema = requests.get(url_ema, params=ema_params).json()
    ema_valor = ema.get("values", [{}])[0].get("ema", "N/A")

    # MACD
    url_macd = "https://api.twelvedata.com/macd"
    macd_params = {
        "symbol": symbol,
        "interval": interval,
        "apikey": API_KEY
    }
    macd = requests.get(url_macd, params=macd_params).json()
    macd_line = macd.get("values", [{}])[0].get("macd", "N/A")
    signal_line = macd.get("values", [{}])[0].get("signal", "N/A")

    return {
        "precio_actual": precios[0],
        "rsi": rsi_valor,
        "ema": ema_valor,
        "macd": macd_line,
        "signal": signal_line
    }
