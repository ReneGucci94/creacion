import pandas as pd
from pydantic import BaseModel
from servicios.twelve_data import obtener_velas_twelve_data

class Entrada(BaseModel):
    activo: str
    intervalo: str
    estrategia: str

def calcular_ema(df, period):
    return df['close'].ewm(span=period, adjust=False).mean()

def calcular_rsi(df, period=14):
    delta = df['close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


async def analizar_scalping_sniper(info: Entrada):
    symbol = info.activo.upper().strip()
    intervalos = {
        "1m": "1min", "5m": "5min", "15m": "15min", "30m": "30min",
        "1h": "1h", "4h": "4h", "1d": "1day", "1w": "1week"
    }
    intervalo_twelve = intervalos.get(info.intervalo.lower(), "15min")
    df = obtener_velas_twelve_data(symbol, intervalo_twelve)
    if df.empty:
        return {"analisis": "❌ No se pudieron obtener velas."}

    df['ema9'] = calcular_ema(df, 9)
    df['ema21'] = calcular_ema(df, 21)
    df['rsi'] = calcular_rsi(df)

    precio = df['close'].iloc[-1]
    ema9 = df['ema9'].iloc[-1]
    ema21 = df['ema21'].iloc[-1]
    rsi = df['rsi'].iloc[-1]

    accion = "ESPERA"
    confianza = "60%"
    motivo = "Condiciones neutras."

    if ema9 > ema21 and rsi > 55:
        accion = "COMPRA"
        confianza = "88%"
        motivo = "Cruce EMA + RSI fuerte"
    elif ema9 < ema21 and rsi < 45:
        accion = "VENTA"
        confianza = "85%"
        motivo = "Cruce bajista + debilidad RSI"

    resultado = f"""\n🎯 *Scalping Sniper*\n━━━━━━━━━━━━━━━━━━━━━━━\n🔍 Activo: *{info.activo}*\n🕒 Intervalo: *{info.intervalo}*\n💵 Precio actual: *{precio:.5f}*\n━━━━━━━━━━━━━━━━━━━━━━━\n📊 EMA9: {ema9:.5f} | EMA21: {ema21:.5f}\n📈 RSI: {rsi:.2f}\n━━━━━━━━━━━━━━━━━━━━━━━\n🚀 Acción sugerida: *{accion}*\n🔥 Confianza: *{confianza}*\n📚 Motivo: {motivo}\n━━━━━━━━━━━━━━━━━━━━━━━\n""".strip()

    return {"analisis": resultado}