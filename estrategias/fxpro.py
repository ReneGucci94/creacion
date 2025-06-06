import pandas as pd
from pydantic import BaseModel
from estrategias.cripto1h import contexto_cripto1h
from estrategias.swing.usdjpy import analizar_usdjpy_swing
from servicios.twelve_data import obtener_velas_twelve_data

# Si tienes esta función en otro archivo, importa aquí:
# from estrategias.daytrading.eurusd import fxpro_daytrader_eurusd

class Entrada(BaseModel):
    activo: str
    intervalo: str
    estrategia: str
    modo: str = "daytrader"  # El bot debe enviar este campo

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


# --------- FUNCION PRINCIPAL -----------
async def analizar_fxpro(info: Entrada):
    # --- Swing USDJPY ---
    if info.activo == "USDJPY" and (hasattr(info, "modo") and info.modo.lower() == "swingtrader"):
        return analizar_usdjpy_swing()
    
    # --- Cripto 1H ---
    if info.activo in ["BTCUSDT", "ETHUSDT"]:
        return await contexto_cripto1h(info)
    
    # --- EURUSD Daytrader (Si tienes función especializada, descomenta) ---
    # if info.activo == "EURUSD" and (not hasattr(info, 'modo') or info.modo == "daytrader"):
    #     return await fxpro_daytrader_eurusd(info)
    
    # --- General para cualquier activo ---
    symbol = info.activo.upper().strip()
    intervalos = {
        "1m": "1min", "5m": "5min", "15m": "15min", "30m": "30min",
        "1h": "1h", "4h": "4h", "1d": "1day", "1w": "1week"
    }
    intervalo_twelve = intervalos.get(info.intervalo.lower(), "15min")
    df = obtener_velas_twelve_data(symbol, intervalo_twelve)
    if df.empty:
        return {"analisis": "❌ No se pudieron obtener velas."}
    
    df['ema20'] = calcular_ema(df, 20)
    df['ema100'] = calcular_ema(df, 100)
    df['rsi'] = calcular_rsi(df)
    precio = df['close'].iloc[-1]
    ema20 = df['ema20'].iloc[-1]
    ema100 = df['ema100'].iloc[-1]
    rsi = df['rsi'].iloc[-1]
    
    contexto = "Mercado indeciso"
    accion = "ESPERA"
    confianza = "60%"

    if ema20 > ema100 and rsi > 60:
        accion = "COMPRA"
        contexto = "Tendencia alcista fuerte"
        confianza = "90%"
    elif ema20 < ema100 and rsi < 40:
        accion = "VENTA"
        contexto = "Tendencia bajista con presión vendedora"
        confianza = "85%"

    resultado = f"""
🧠 *FxPRO - Análisis Avanzado*
━━━━━━━━━━━━━━━━━━━━━━━
🔍 Activo: *{info.activo}*
🕒 Intervalo: *{info.intervalo}*
💵 Precio actual: *{precio:.5f}*
━━━━━━━━━━━━━━━━━━━━━━━
📊 EMA20: {ema20:.5f} | EMA100: {ema100:.5f}
📈 RSI: {rsi:.2f}
━━━━━━━━━━━━━━━━━━━━━━━
🎯 Acción: *{accion}*
📘 Contexto: {contexto}
🔥 Confianza: *{confianza}*
━━━━━━━━━━━━━━━━━━━━━━━
""".strip()

    return {"analisis": resultado}

