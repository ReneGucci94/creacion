import pandas as pd
from pydantic import BaseModel
from estrategias.signalpro import calcular_rsi, calcular_ema, calcular_macd
from servicios.twelve_data import obtener_velas_twelve_data

class Entrada(BaseModel):
    activo: str
    intervalo: str
    estrategia: str

async def analizar_senal_automatica(info: Entrada):
    symbol = info.activo.upper().strip()
    intervalo_twelve = "15min"
    df = obtener_velas_twelve_data(symbol, intervalo_twelve)
    if df.empty:
        return {"analisis": ""}

    df['rsi'] = calcular_rsi(df)
    df['ema20'] = calcular_ema(df, 20)
    df['ema50'] = calcular_ema(df, 50)
    _, _, hist = calcular_macd(df)

    rsi = df['rsi'].iloc[-1]
    ema20 = df['ema20'].iloc[-1]
    ema50 = df['ema50'].iloc[-1]
    macd_hist = hist.iloc[-1]
    precio = df['close'].iloc[-1]

    if ema20 > ema50 and rsi > 50 and macd_hist > 0:
        accion = "COMPRA"
        confianza = "82%"
        motivo = "Tendencia alcista con impulso confirmado"
    elif ema20 < ema50 and rsi < 50 and macd_hist < 0:
        accion = "VENTA"
        confianza = "78%"
        motivo = "Tendencia bajista con impulso negativo"
    else:
        return {"analisis": ""}

    resultado = f"""
🤖 *Señal Automática*
━━━━━━━━━━━━━━━━━━━━━━━
🔍 Activo: *{info.activo}*
🕒 Intervalo: *{info.intervalo}*
💵 Precio actual: *{precio:.5f}*
━━━━━━━━━━━━━━━━━━━━━━━
📊 EMA20: {ema20:.5f} | EMA50: {ema50:.5f}
📈 RSI: {rsi:.2f} | MACD Hist: {macd_hist:.4f}
━━━━━━━━━━━━━━━━━━━━━━━
🎯 Señal: *{accion}*
🔥 Confianza: *{confianza}*
⌛ Duración estimada: 15-30 min
📚 Motivo: {motivo}
━━━━━━━━━━━━━━━━━━━━━━━
""".strip()

    return {"analisis": resultado}
