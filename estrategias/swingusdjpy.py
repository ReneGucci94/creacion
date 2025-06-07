import os
import pandas as pd
import requests

def obtener_ultimas_velas(activo, intervalo="1h", limite=100):
    apikey = os.getenv("API_KEY")
    if activo.endswith("USDT") and "/" not in activo:
        activo = activo[:-4] + "/USD"
    url = (
        f"https://api.twelvedata.com/time_series?symbol={activo}&interval={intervalo}&outputsize={limite}&apikey={apikey}"
    )
    try:
        r = requests.get(url)
        data = r.json()
        if "values" not in data:
            return pd.DataFrame()
        df = pd.DataFrame(data["values"])
        df = df.rename(columns={
            "datetime": "timestamp",
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
        })
        df = df.astype({"open": float, "high": float, "low": float, "close": float})
        df = df[::-1]
        return df
    except Exception:
        return pd.DataFrame()


def calcular_ema(df, period):
    return df['close'].ewm(span=period, adjust=False).mean()

def calcular_rsi(df, period=7):
    delta = df['close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def analizar_usdjpy_swing():
    df_1h = obtener_ultimas_velas("USDJPY", "1h")
    df_4h = obtener_ultimas_velas("USDJPY", "4h")
    if df_1h.empty or df_4h.empty:
        return {"analisis": "❌ No se pudieron obtener velas."}

    df_1h['ema20'] = calcular_ema(df_1h, 20)
    df_1h['ema100'] = calcular_ema(df_1h, 100)
    df_1h['rsi'] = calcular_rsi(df_1h, 7)
    df_1h['atr'] = (df_1h['high'] - df_1h['low']).rolling(window=14).mean()
    
    precio = df_1h['close'].iloc[-1]
    ema20 = df_1h['ema20'].iloc[-1]
    ema100 = df_1h['ema100'].iloc[-1]
    rsi = df_1h['rsi'].iloc[-1]
    atr = df_1h['atr'].iloc[-1]
    hora = pd.to_datetime(df_1h['timestamp'].iloc[-1], unit='ms').hour

    df_4h['ema20_4h'] = calcular_ema(df_4h, 20)
    df_4h['ema100_4h'] = calcular_ema(df_4h, 100)
    ema20_4h = df_4h['ema20_4h'].iloc[-1]
    ema100_4h = df_4h['ema100_4h'].iloc[-1]
    tendencia_4h = "ALCISTA" if ema20_4h > ema100_4h else "BAJISTA"

    if atr < 0.05:
        return {"analisis": "⏳ Volatilidad muy baja. No operar por ahora."}
    
    if hora > 15:
        return {"analisis": "⏳ Fuera del horario óptimo (00:00 a 15:00 UTC)."}

    if ema20 > ema100 and rsi > 60 and tendencia_4h == "ALCISTA":
        resultado = f"""
📊 *SignalPRO USDJPY Swing V1.0*
━━━━━━━━━━━━━━━━━━━━━━━
✅ Condición: *LONG Confirmado*
💰 Precio actual: {precio:.3f}
📈 EMA20: {ema20:.3f} | EMA100: {ema100:.3f}
📊 RSI(7): {rsi:.2f} | ATR: {atr:.4f}
🕒 Hora: {hora}:00 UTC
━━━━━━━━━━━━━━━━━━━━━━━
🎯 Acción recomendada: *COMPRA*
✅ Confianza: 85%+
━━━━━━━━━━━━━━━━━━━━━━━
"""
        return {"analisis": resultado.strip()}

    return {"analisis": "❌ No hay condiciones de compra claras ahora mismo."}
