import pandas as pd
from estrategias.cripto1h import analizar_cripto1h
#from estrategias.swing.usdjpy import analizar_usdjpy_swing
from pydantic import BaseModel
from servicios.twelve_data import obtener_velas_twelve_data

class Entrada(BaseModel):
    activo: str
    intervalo: str
    estrategia: str
    modo: str = "daytrader"  # El bot debe mandar esto

def calcular_rsi(df, period=14):
    delta = df['close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calcular_ema(df, period):
    return df['close'].ewm(span=period, adjust=False).mean()

def calcular_macd(df):
    ema12 = calcular_ema(df, 12)
    ema26 = calcular_ema(df, 26)
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    hist = macd - signal
    return macd, signal, hist


# --------- EURUSD DayTrader (si la tienes) -----------
async def signalpro_daytrader_eurusd(info: Entrada):
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
    df['ema50'] = calcular_ema(df, 50)
    df['rsi'] = calcular_rsi(df)
    _, _, hist = calcular_macd(df)
    precio = df['close'].iloc[-1]
    ema20 = df['ema20'].iloc[-1]
    ema50 = df['ema50'].iloc[-1]
    rsi = df['rsi'].iloc[-1]
    macd_hist = hist.iloc[-1]

    accion = "ESPERA"
    confianza = "60%"
    motivo = "Condiciones neutras"

    if ema20 > ema50 and rsi > 55 and macd_hist > 0:
        accion = "COMPRA"
        confianza = "84%"
        motivo = "Tendencia alcista clara, impulso confirmado"
    elif ema20 < ema50 and rsi < 45 and macd_hist < 0:
        accion = "VENTA"
        confianza = "80%"
        motivo = "Tendencia bajista con presión vendedora"

    resultado = f"""
📡 *SignalPRO DayTrader EURUSD*
━━━━━━━━━━━━━━━━━━━━━━━
🔍 Activo: *{info.activo}*
🕒 Intervalo: *{info.intervalo}*
💵 Precio actual: *{precio:.5f}*
━━━━━━━━━━━━━━━━━━━━━━━
📊 EMA20: {ema20:.5f} | EMA50: {ema50:.5f}
📈 RSI: {rsi:.2f} | MACD Hist: {macd_hist:.4f}
━━━━━━━━━━━━━━━━━━━━━━━
🎯 Acción sugerida: *{accion}*
🔥 Confianza: *{confianza}*
📚 Motivo: {motivo}
━━━━━━━━━━━━━━━━━━━━━━━
""".strip()
    return {"analisis": resultado}

# --------- ENRUTADOR PRINCIPAL ---------
async def analizar_signalpro(info: Entrada):
    # --- Swing USDJPY ---
    if info.activo == "USDJPY" and (hasattr(info, "modo") and info.modo.lower() == "swingtrader"):
        return analizar_usdjpy_swing()

    # --- Cripto 1H ---
    if info.activo in ["BTCUSDT", "ETHUSDT"]:
        return await analizar_cripto1h(info)

    # --- EURUSD Daytrader (si la tienes) ---
    if info.activo == "EURUSD" and (not hasattr(info, 'modo') or info.modo == "daytrader"):
        return await signalpro_daytrader_eurusd(info)

    # --- Lógica general para otros activos ---
    symbol = info.activo.upper().strip()
    intervalos = {
        "1m": "1min", "5m": "5min", "15m": "15min", "30m": "30min",
        "1h": "1h", "4h": "4h", "1d": "1day", "1w": "1week"
    }
    intervalo_twelve = intervalos.get(info.intervalo.lower(), "15min")
    df = obtener_velas_twelve_data(symbol, intervalo_twelve)
    if df.empty:
        return {"analisis": "❌ No se pudieron obtener velas."}

    df['rsi'] = calcular_rsi(df)
    df['ema20'] = calcular_ema(df, 20)
    df['ema50'] = calcular_ema(df, 50)
    _, _, hist = calcular_macd(df)

    rsi = df['rsi'].iloc[-1]
    ema20 = df['ema20'].iloc[-1]
    ema50 = df['ema50'].iloc[-1]
    macd_hist = hist.iloc[-1]
    precio = df['close'].iloc[-1]

    accion = "ESPERA"
    confianza = "60%"
    motivo = "Condiciones neutras"

    if ema20 > ema50 and rsi > 50 and macd_hist > 0:
        accion = "COMPRA"
        confianza = "82%"
        motivo = "Tendencia alcista con impulso confirmado"
    elif ema20 < ema50 and rsi < 50 and macd_hist < 0:
        accion = "VENTA"
        confianza = "78%"
        motivo = "Tendencia bajista con impulso negativo"

    resultado = f"""
📡 *SignalPRO*
━━━━━━━━━━━━━━━━━━━━━━━
🔍 Activo: *{info.activo}*
🕒 Intervalo: *{info.intervalo}*
💵 Precio actual: *{precio:.5f}*
━━━━━━━━━━━━━━━━━━━━━━━
📊 EMA20: {ema20:.5f} | EMA50: {ema50:.5f}
📈 RSI: {rsi:.2f} | MACD Hist: {macd_hist:.4f}
━━━━━━━━━━━━━━━━━━━━━━━
🎯 Acción sugerida: *{accion}*
🔥 Confianza: *{confianza}*
📚 Motivo: {motivo}
━━━━━━━━━━━━━━━━━━━━━━━
""".strip()

    return {"analisis": resultado}
