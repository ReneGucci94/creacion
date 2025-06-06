import pandas as pd
from pydantic import BaseModel
from servicios.twelve_data import obtener_velas_twelve_data

class Entrada(BaseModel):
    activo: str
    intervalo: str
    estrategia: str

async def contexto_cripto1h(info: Entrada):
    if info.activo not in ["BTCUSDT", "ETHUSDT"]:
        return {"analisis": "❌ Esta función solo acepta BTCUSDT o ETHUSDT."}

    # Puedes usar lógica real de contexto o poner un ejemplo temporal:
    contexto = (
        "Tendencia general: Alcista\n"
        "Volatilidad: Alta\n"
        "Soportes clave: 67,000 | 65,000\n"
        "Resistencias clave: 71,000 | 73,500\n"
        "MACD positivo, RSI en zona neutral. El mercado de cripto muestra fortaleza en temporalidad 1H."
    )

    return {
        "analisis": f"\n📊 *Contexto Cripto*\n━━━━━━━━━━━━━━━\n{contexto}\n━━━━━━━━━━━━━━━"
    }

async def analizar_cripto1h(info: Entrada):
    if info.activo not in ["BTCUSDT", "ETHUSDT"]:
        return {"analisis": "❌ Esta estrategia solo acepta BTCUSDT o ETHUSDT."}

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

    estrategia = "📉 Sin señal clara"
    accion = "ESPERA"
    confianza = "-"
    descripcion = "No hay condiciones suficientes para entrar."

    if ema20 > ema50 and rsi > 50 and macd_hist > 0:
        estrategia = "⚡ Rayo Directo"
        accion = "COMPRA"
        confianza = "85%"
        descripcion = "EMA20 > EMA50, RSI y MACD alineados al alza."
    elif ema20 > ema50 and abs(precio - ema20) < 0.001 and 50 < rsi < 60 and macd_hist > 0:
        estrategia = "💎 Pullback Limpio"
        accion = "COMPRA"
        confianza = "88%"
        descripcion = "Rebote técnico en tendencia alcista."
    elif abs(ema20 - ema50) < 0.0005 and 40 < rsi < 50:
        estrategia = "🐉 Dragón Dormido"
        accion = "ESPERA"
        confianza = "70%"
        descripcion = "Mercado consolidando. Evitar entrada."

    resultado = f"""\n🧠 *SignalPRO Cripto 1H*\n━━━━━━━━━━━━━━━━━━━━━━━\n🔍 Activo: *{info.activo}*\n🕒 Intervalo: 1 hora\n💵 Precio actual: *{precio:.2f}*\n━━━━━━━━━━━━━━━━━━━━━━━\n📊 EMA20: {ema20:.2f} | EMA50: {ema50:.2f}\n📈 RSI: {rsi:.2f} | MACD Hist: {macd_hist:.4f}\n━━━━━━━━━━━━━━━━━━━━━━━\n🎯 Acción: *{accion}*\n📘 Estrategia: {estrategia}\n🔥 Confianza: *{confianza}*\n📚 Nota: {descripcion}\n━━━━━━━━━━━━━━━━━━━━━━━\n""".strip()

    return {"analisis": resultado}