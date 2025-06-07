📊 Bot de Trading en Telegram (Forex y Cripto)
Este bot de Telegram envía señales automáticas y manuales de trading para pares de Forex y criptomonedas, conectándose a la API de Twelve Data para obtener datos en tiempo real. Usa diferentes estrategias como Scalping Sniper, SignalPRO, FxPRO, entre otras.

📁 Estructura del proyecto
```
.
├── bot.py               # Bot principal de Telegram
├── bin.py               # Backend que procesa las señales
├── estrategias/         # Contiene estrategias como scalping, signalpro, fxpro
├── servicios/
│   └── twelve_data.py   # Conexión a la API de Twelve Data
├── .env                 # Variables de entorno (TOKEN y API_KEY)
└── requirements.txt     # Librerías necesarias
```

⚙️ Instalación
Clona este repositorio:

```bash
git clone https://github.com/tuusuario/tu-repo.git
cd tu-repo
```
Instala las dependencias:

```bash
pip install -r requirements.txt
```
Crea un archivo .env con este contenido:

```ini
TELEGRAM_TOKEN=tu_token_de_telegram
TWELVE_DATA_API_KEY=tu_clave_de_twelve_data
```
Corre el bot:

```bash
python bot.py
```

🧪 Uso Básico
1. Inicia una conversación con tu bot de Telegram.
2. Selecciona un par (ej. EUR/USD).
3. Elige una estrategia (DayTrader, Swing o Scalping).
4. Recibe señales en tiempo real.

🔗 Obtener tu API Key de Twelve Data
Crea una cuenta gratis y consigue tu clave aquí:
https://twelvedata.com

✅ Requisitos
- python-telegram-bot
- aiohttp
- nest_asyncio
- pandas
- requests
