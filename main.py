import sys
import os
import math

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from config.settings import TELEGRAM_TOKEN, APP_NAME, VERSION
from services.finnhub_api import get_quote

from analysis.scoring import basic_score
from analysis.trend import detect_trend
from analysis.filters import signal_quality


# =========================
# SAFE
# =========================
def safe(data, key, default=0):
    try:
        return data.get(key, default)
    except:
        return default


# =========================
# ACTIFS
# =========================
BINARY_ASSETS = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD"]
CLASSIC_ASSETS = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "NAS100"]


# =========================
# MENU PRO
# =========================
MENU = [
    ["📊 Analyse Marché"],
    ["⚡ Option Binaire", "📈 Trading Classique"],
    ["📡 Scanner Actifs"]
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

PREDICTHOOD ENGINE V5

Statut : ONLINE

Choisis un mode :
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
        await update.message.reply_text("Erreur données.")
        return

    await update.message.reply_text(f"""
MARCHÉ

Actif : {symbol}
Prix : {safe(data,'current')}
Haut : {safe(data,'high')}
Bas : {safe(data,'low')}
""")


# =========================
# SCANNER
# =========================
async def scanner(update: Update, context: ContextTypes.DEFAULT_TYPE):

    msg = "OPTION BINAIRE:\n" + "\n".join(BINARY_ASSETS)
    msg += "\n\nTRADING CLASSIQUE:\n" + "\n".join(CLASSIC_ASSETS)

    await update.message.reply_text(msg)


# =========================
# ANALYSE CORE (V4 ENGINE)
# =========================
def confluence(price, ema_val, rsi_val):

    score = 50

    if price > ema_val:
        score += 20
    else:
        score -= 20

    if rsi_val < 30:
        score += 20
    elif rsi_val > 70:
        score -= 20

    return max(0, min(100, score))


# =========================
# ANALYSE
# =========================
async def analyse(update: Update, context: ContextTypes.DEFAULT_TYPE):

    symbol = "AAPL"
    data = get_quote(symbol)

    if not data:
        await update.message.reply_text("Erreur données.")
        return

    price = safe(data, "current", 100)

    history = [price * (1 + i * 0.001) for i in range(-10, 10)]

    ema_val = sum(history) / len(history)
    rsi_val = 50

    score = confluence(price, ema_val, rsi_val)

    trend = "HAUSSIER" if price > ema_val else "BAISSIER"

    signal = "ATTENTE"
    if score >= 70:
        signal = "CALL"
    elif score <= 30:
        signal = "PUT"

    await update.message.reply_text(f"""
ANALYSE PREDICTHOOD V5

Actif : {symbol}
Trend : {trend}
Score : {score}

Signal : {signal}
""")


# =========================
# OPTION BINAIRE
# =========================
async def binary_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):

    symbol = "EURUSD"
    data = get_quote(symbol)

    if not data:
        await update.message.reply_text("Erreur données.")
        return

    price = safe(data, "current", 100)
    history = [price * (1 + i * 0.0008) for i in range(-10, 10)]

    ema_val = sum(history) / len(history)
    rsi_val = 50

    score = confluence(price, ema_val, rsi_val)

    signal = "ATTENTE"

    if score >= 75:
        signal = "CALL (EXP 1-3 MIN)"
    elif score <= 25:
        signal = "PUT (EXP 1-3 MIN)"

    await update.message.reply_text(f"""
OPTION BINAIRE V5

Actif : {symbol}
Score : {score}

Signal : {signal}
""")


# =========================
# CLASSIC TRADING
# =========================
async def classic_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):

    symbol = "XAUUSD"
    data = get_quote(symbol)

    if not data:
        await update.message.reply_text("Erreur données.")
        return

    price = safe(data, "current", 100)
    history = [price * (1 + i * 0.0012) for i in range(-10, 10)]

    ema_val = sum(history) / len(history)
    rsi_val = 50

    score = confluence(price, ema_val, rsi_val)

    signal = "ATTENTE"

    if score >= 65:
        signal = "BUY"
    elif score <= 35:
        signal = "SELL"

    await update.message.reply_text(f"""
TRADING CLASSIQUE V5

Actif : {symbol}
Score : {score}

Signal : {signal}
""")


# =========================
# ROUTER MENU
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
# MAIN
# =========================
def main():

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu))

    print("PredictHood V5 RUNNING...")

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
