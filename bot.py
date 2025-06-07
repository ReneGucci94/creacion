import asyncio
import aiohttp
import os
import pandas as pd
import numpy as np
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

# === CONFIGURACIÓN INICIAL ===
TOKEN = os.getenv("TOKEN")
user_id_telegram = None
modo_sniper_activo = False
activo_actual = None
modo_actual = ""
contador_senales = 0
mensaje_editable_id = None
ultimo_mensaje_fxpro = ""
ultimo_mensaje_signalpro = ""

activos_validos = [
    "EUR/USD", "USD/JPY", "GBP/USD", "BTC/USD",
    "ETH/USD", "USD/CAD", "USD/CHF", "AUD/USD"
]

# Normaliza el formato del activo antes de enviarlo a la API
def normalizar_activo(activo: str) -> str:
    activo = activo.upper().strip()
    mapping = {
        "EURUSD": "EUR/USD",
        "USDJPY": "USD/JPY",
        "GBPUSD": "GBP/USD",
        "AUDUSD": "AUD/USD",
        "BTCUSDT": "BTC/USD",
        "ETHUSDT": "ETH/USD",
        "USDCAD": "USD/CAD",
        "USDCHF": "USD/CHF",
    }
    # Si ya está en formato correcto, se devuelve sin cambios
    return mapping.get(activo, activo)

async def consultar_api_ia(activo, intervalo, mensaje):
    url = "https://web-production-70f1.up.railway.app/analizar"
    payload = {"activo": activo, "intervalo": intervalo, "estrategia": mensaje}
    payload["activo"] = normalizar_activo(payload["activo"])
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                data = await resp.json()
                print(f"📥 RESPUESTA DE API:\n{data}")  # Solo si quieres ver la respuesta
                return data.get("analisis", "❌ No se recibió un análisis válido desde la IA.")
    except Exception as e:
        print(f"❌ Error en consultar_api_ia: {e}")
        return "❌ Error al conectar con la API de análisis."

async def enviar_senal(activo, intervalo, estrategia):
    url = "https://web-production-70f1.up.railway.app/analizar"
    payload = {
        "activo": activo,
        "intervalo": intervalo,
        "estrategia": estrategia
    }
    payload["activo"] = normalizar_activo(payload["activo"])

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                print("✅ Señal recibida:", data)
            else:
                print("❌ Error en la petición:", resp.status)
      
def obtener_intervalo_por_modo():
    if modo_actual == "Scalping":
        return "1m"
    elif modo_actual == "DayTrader":
        return "15m"
    elif modo_actual == "SwingTrader":
        return "1h"
    return "1m"

async def mensaje_inicio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global user_id_telegram, mensaje_editable_id
    user_id_telegram = update.effective_user.id
    keyboard = [[InlineKeyboardButton("🚀 Iniciar bot", callback_data="menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = await update.message.reply_text("Bienvenido. Presiona el botón para comenzar.", reply_markup=reply_markup)
    mensaje_editable_id = msg.message_id

async def mostrar_fxpro(query):
    global ultimo_mensaje_fxpro
    try:
        intervalo = obtener_intervalo_por_modo()

        # 1. Mostrar mensaje de "Analizando..."
        buttons_loading = [
            [InlineKeyboardButton("🕒 Esperando análisis...", callback_data="fxpro")]
        ]
        await query.edit_message_text(
            text=f"⏳ Analizando *{activo_actual}*...\nPor favor espera unos segundos.",
            reply_markup=InlineKeyboardMarkup(buttons_loading),
            parse_mode="Markdown"
        )

        # 2. Llamar al análisis
        respuesta = await consultar_api_ia(activo_actual, intervalo, "fxpro")

        # 3. No actualices si es igual al anterior
        if respuesta == ultimo_mensaje_fxpro:
            return
        ultimo_mensaje_fxpro = respuesta

        # 4. Mostrar resultado final
        buttons = [
            [InlineKeyboardButton("🔄 Actualizar análisis", callback_data="fxpro")],
            [InlineKeyboardButton("💪 SignalPRO", callback_data="signalpro")],
            [InlineKeyboardButton("🏠 Menú principal", callback_data="menu")]
        ]
        await query.edit_message_text(text=respuesta, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")

    except Exception as e:
        print(f"❌ Error en mostrar_fxpro: {e}")



async def mostrar_signalpro(query):
    global ultimo_mensaje_signalpro
    try:
        intervalo = obtener_intervalo_por_modo()

        # 1. Mostrar mensaje de carga
        buttons_loading = [
            [InlineKeyboardButton("🕒 Esperando análisis...", callback_data="signalpro")]
        ]
        await query.edit_message_text(
            text=f"⏳ Analizando *{activo_actual}*...\nPor favor espera unos segundos.",
            reply_markup=InlineKeyboardMarkup(buttons_loading),
            parse_mode="Markdown"
        )

        # 2. Llamar análisis
        respuesta = await consultar_api_ia(activo_actual, intervalo, "signalpro")

        # 3. Evitar mensaje duplicado
        if respuesta == ultimo_mensaje_signalpro:
            return
        ultimo_mensaje_signalpro = respuesta

        # 4. Mostrar resultado final
        buttons = [
            [InlineKeyboardButton("🔄 Actualizar análisis", callback_data="signalpro")],
            [InlineKeyboardButton("🧠 FxPRO", callback_data="fxpro")],
            [InlineKeyboardButton("🏠 Menú principal", callback_data="menu")]
        ]
        await query.edit_message_text(text=respuesta, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")

    except Exception as e:
        print(f"❌ Error en mostrar_signalpro: {e}")


async def texto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        mensaje_usuario = update.message.text
        intervalo = obtener_intervalo_por_modo()
        respuesta = await consultar_api_ia(activo_actual, intervalo, mensaje_usuario)
        await update.message.reply_text(respuesta)
    except Exception as e:
        await update.message.reply_text("❌ Error al analizar con IA.")
        print(f"Error IA: {e}")

async def boton_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    global activo_actual, modo_actual, modo_sniper_activo, contador_senales
    if data == "menu":
        keyboard = [[InlineKeyboardButton(par, callback_data=par)] for par in activos_validos]
        await query.edit_message_text("Selecciona el par que quieres analizar:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data in activos_validos:
        activo_actual = data
        keyboard = [[
            InlineKeyboardButton("DayTrader", callback_data="modo_day"),
            InlineKeyboardButton("SwingTrader", callback_data="modo_swing")
        ], [InlineKeyboardButton("⚡ Scalping", callback_data="scalp_on")]]
        await query.edit_message_text(f"Par seleccionado: {activo_actual}\nSelecciona tu modo:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data in ["modo_day", "modo_swing"]:
        modo_actual = "DayTrader" if data == "modo_day" else "SwingTrader"
        buttons = [
            [InlineKeyboardButton("🧠 FxPRO", callback_data="fxpro")],
            [InlineKeyboardButton("💪 SignalPRO", callback_data="signalpro")],
            [InlineKeyboardButton("🏠 Menú principal", callback_data="menu")]
        ]
        await query.edit_message_text(f"✅ Modo: {modo_actual}\nSelecciona una acción:", reply_markup=InlineKeyboardMarkup(buttons))
    elif data == "fxpro":
        await mostrar_fxpro(query)
    elif data == "signalpro":
        await mostrar_signalpro(query)
    elif data == "scalp_on":
        modo_actual = "Scalping"
        modo_sniper_activo = True
        contador_senales = 0
        buttons = [
            [InlineKeyboardButton("🚩 Detener scalping", callback_data="scalp_off")],
            [InlineKeyboardButton("🏠 Menú principal", callback_data="menu")]
        ]
        await query.edit_message_text(
            f"""⚡ *Scalping activado* para *{activo_actual}*.
El bot te notificará automáticamente cuando detecte una señal.""",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode="Markdown"
        )
    elif data == "scalp_off":
        modo_sniper_activo = False
        texto = f"""
🚩 *Scalping detenido* para *{activo_actual}*.
📊 Señales enviadas en esta sesión: *{contador_senales}*
Ya no se enviarán más señales en tiempo real.
"""
        await query.edit_message_text(
            texto,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Menú principal", callback_data="menu")]]),
            parse_mode="Markdown"
        )

async def loop_senal_automatica():
    while True:
        if activo_actual:
            await enviar_senal(activo_actual, "15m", "senal_automatica")
        await asyncio.sleep(60)

# Indicadores para sniper

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

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", mensaje_inicio))
    app.add_handler(CallbackQueryHandler(boton_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, texto))
    asyncio.create_task(loop_senal_automatica())
    print("🧠 BOT SNIPER ACTIVO")
    await app.run_polling()

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())













