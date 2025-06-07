import os
import asyncio
from datetime import datetime, timedelta

import pandas as pd
import httpx

from servicios.twelve_data import obtener_velas_twelve_data

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")

# Ensure the legacy variable used in twelve_data.py is populated
if TWELVE_DATA_API_KEY and not os.getenv("API_KEY"):
    os.environ["API_KEY"] = TWELVE_DATA_API_KEY


def _formatear_ticker_polygon(activo: str) -> str:
    """Convierte EUR/USD -> C:EURUSD y BTC/USD -> X:BTCUSD"""
    activo = activo.upper().strip()
    if "/" in activo:
        base, quote = activo.split("/")
    else:
        base, quote = activo[:3], activo[3:]
    if len(base) == 3 and len(quote) == 3:
        return f"C:{base}{quote}"
    return f"X:{base}{quote}"


def _intervalo_polygon(intervalo: str) -> tuple[int, str]:
    """Devuelve el multiplier y unidad para Polygon."""
    i = intervalo.lower().strip()
    if i.endswith("m"):
        return int(i[:-1]), "minute"
    if i.endswith("h"):
        return int(i[:-1]) * 60, "minute"
    return int(i), "minute"


async def _obtener_desde_polygon(activo: str, intervalo: str) -> pd.DataFrame | None:
    if not POLYGON_API_KEY:
        return None
    ticker = _formatear_ticker_polygon(activo)
    mult, unidad = _intervalo_polygon(intervalo)
    fin = datetime.utcnow()
    inicio = fin - timedelta(minutes=mult * 50)
    url = (
        f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/{mult}/{unidad}/"
        f"{inicio.isoformat()}/{fin.isoformat()}?apiKey={POLYGON_API_KEY}"
    )
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url)
            if resp.status_code != 200:
                print(f"❌ Error Polygon: {resp.status_code} - {resp.text}")
                return None
            data = resp.json()
            if "results" not in data:
                print("❌ Respuesta inesperada de Polygon:", data)
                return None
            df = pd.DataFrame(data["results"])
            if df.empty:
                return None
            df = df.rename(columns={
                "o": "open",
                "h": "high",
                "l": "low",
                "c": "close",
                "v": "volume",
                "t": "timestamp",
            })
            df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms")
            return df[["open", "high", "low", "close", "volume", "datetime"]]
    except Exception as e:
        print("❌ Excepción al obtener de Polygon:", e)
        return None


async def obtener_datos_unificados(activo: str, intervalo: str):
    """Intenta obtener datos de Polygon.io y, si falla, de Twelve Data."""
    df = await _obtener_desde_polygon(activo, intervalo)
    if df is not None:
        return df
    try:
        df_td = await asyncio.to_thread(obtener_velas_twelve_data, activo, intervalo)
        if df_td is None or df_td.empty:
            return None
        df_td["datetime"] = pd.to_datetime(df_td["timestamp"])
        columnas = ["open", "high", "low", "close", "volume", "datetime"]
        return df_td[columnas]
    except Exception as e:
        print("❌ Error en fuente alternativa Twelve Data:", e)
        return None
