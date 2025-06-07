import os
import pandas as pd
import requests

API_KEY = os.getenv("API_KEY")

_INTERVAL_MAP = {
    "1m": "1min",
    "5m": "5min",
    "15m": "15min",
    "30m": "30min",
    "45m": "45min",
    "1h": "1h",
    "2h": "2h",
    "4h": "4h",
    "8h": "8h",
    "1d": "1day",
    "1day": "1day",
    "1w": "1week",
    "1week": "1week",
    "1M": "1month",
    "1month": "1month",
}

def _normalizar_intervalo(intervalo: str) -> str:
    """Devuelve el intervalo en el formato que espera Twelve Data."""
    i = intervalo.strip()
    if i.endswith("m") and not i.endswith("min"):
        i = f"{i[:-1]}min"
    return _INTERVAL_MAP.get(i, i)


def obtener_velas_twelve_data(activo: str, intervalo: str = "15min", limite: int = 100) -> pd.DataFrame:
    """Obtiene velas desde Twelve Data normalizando símbolo e intervalo."""
    symbol = activo.upper().strip()
    interval = _normalizar_intervalo(intervalo)
    url = (
        f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}"
        f"&apikey={API_KEY}&outputsize={limite}"
    )
    try:
        r = requests.get(url)
        data = r.json()
        if "values" not in data:
            print("❌ Twelve Data respondió algo inesperado:", data)
            return pd.DataFrame()
        df = pd.DataFrame(data["values"])
        df = df.rename(
            columns={
                "datetime": "timestamp",
                "open": "open",
                "high": "high",
                "low": "low",
                "close": "close",
            }
        )
        df = df.astype({"open": float, "high": float, "low": float, "close": float})
        df = df[::-1]
        return df
    except Exception as e:
        print("❌ Error al procesar velas:", e)
        return pd.DataFrame()
