import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from config.settings import TELEGRAM_TOKEN, APP_NAME, VERSION
from services.finnhub_api import get_quote

from analysis.scoring import basic_score
from analysis.trend import detect_trend
from analysis.filters import signal_quality


# =========================
# SAFE TOOL
# =========================
def safe(data, key, default=0):
    try:
        return data.get(key, default)
    except:
        return default


# =========================
# ACTIFS STRATÉGIQUES
# =========================
BINARY_ASSETS = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD"]
CLASSIC_ASSETS = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "NAS100"]


# =========================
# MENU PRO
# =========================
MENU = [
    ["📊 Analyse Marché"],
    ["⚡ Option Binaire", "📈 Trading Classique"],
    ["📡 Scanner Actifs"],
    ["ℹ️ Aide"]
]


# =========================
# START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = ReplyKeyboardMarkup(MENU, resize_keyboard=True)

    await update.message.reply_text(
        f"""
{APP_NAME}
Version : {VERSION}

PREDICTHOOD TRADING ENGINE V3

Statut : EN LIGNE

Modules :
- Analyse marché
- Option binaire
- Trading classique
- Scanner intelligent
""",
        reply_markup=keyboard
    )


# =========================
# PRICE TEST
# =========================
async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):

    symbol = "AAPL"
    data = get_quote(symbol)

    if not data:
        await update.message.reply_text("Données indisponibles.")
        return

    await update.message.reply_text(f"""
MARCHÉ LIVE

Actif : {symbol}
Prix : {safe(data,'current')}
Haut : {safe(data,'high')}
Bas : {safe(data,'low')}
""")


# =========================
# SCANNER INTELLIGENT
# =========================
async def scanner(update: Update, context: ContextTypes.DEFAULT_TYPE):

    msg = "OPTION BINAIRE ACTIFS:\n"
    msg += "\n".join(BINARY_ASSETS)

    msg += "\n\nTRADING CLASSIQUE:\n"
    msg += "\n".join(CLASSIC_ASSETS)

    await update.message.reply_text(msg)


# =========================
# ANALYSE PRINCIPALE (CORE ENGINE)
# =========================
async def analyse(update: Update, context: ContextTypes.DEFAULT_TYPE):

    symbol = "AAPL"
    data = get_quote(symbol)

    if not data:
        await update.message.reply_text("Données indisponibles.")
        return

    current = safe(data, "current", 100)
    open_price = safe(data, "open", current)

    score = basic_score(data)
    trend = detect_trend(data)
    quality = signal_quality(score, trend)

    # logique simple mais robuste
    momentum = "BUY_PRESSURE" if current > open_price else "SELL_PRESSURE"

    decision = "ATTENTE"

    if quality == "FORTE" and trend == "HAUSSIER":
        decision = "CALL"
    elif quality == "FORTE" and trend == "BAISSIER":
        decision = "PUT"

    await update.message.reply_text(f"""
PREDICTHOOD ANALYSE V3

Actif : {symbol}

Trend : {trend}
Momentum : {momentum}
Score : {score}
Qualité : {quality}

SIGNAL : {decision}
""")


# =========================
# OPTION BINAIRE ENGINE
# =========================
async def binary_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):

    symbol = "EURUSD"
    data = get_quote(symbol)

    if not data:
        await update.message.reply_text("Données indisponibles.")
        return

    score = basic_score(data)
    trend = detect_trend(data)
    quality = signal_quality(score, trend)

    decision = "ATTENTE"

    if score >= 70 and trend == "HAUSSIER":
        decision = "CALL (EXP 1-3min)"
    elif score <= 30 and trend == "BAISSIER":
        decision = "PUT (EXP 1-3min)"

    await update.message.reply_text(f"""
OPTION BINAIRE V3

Actif : {symbol}
Trend : {trend}
Score : {score}
Qualité : {quality}

SIGNAL : {decision}
""")


# =========================
# TRADING CLASSIQUE ENGINE
# =========================
async def classic_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):

    symbol = "XAUUSD"
    data = get_quote(symbol)

    if not data:
        await update.message.reply_text("Données indisponibles.")
        return

    score = basic_score(data)
    trend = detect_trend(data)

    decision = "ATTENTE"

    if score >= 65 and trend == "HAUSSIER":
        decision = "BUY"
    elif score <= 35 and trend == "BAISSIER":
        decision = "SELL"

    await update.message.reply_text(f"""
TRADING CLASSIQUE V3

Actif : {symbol}
Trend : {trend}
Score : {score}

SIGNAL : {decision}
""")


# =========================
# ROUTEUR MENU
# =========================
async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    if text == "📊 Analyse Marché":
        await analyse(update, context)

    elif text == "⚡ Option Binaire":
        await binary_analysis(update, context)

    elif text == "📈 Trading Classique":
        await classic_analysis(update, context)

    elif text == "📡 Scanner Actifs":
        await scanner(update, context)

    else:
        await update.message.reply_text("Option non reconnue.")


# =========================
# MAIN STABLE RAILWAY
# =========================
def main():

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu))

    print("PredictHood V3 RUNNING...")

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
