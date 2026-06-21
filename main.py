import sys
import os
import math

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from config.settings import TELEGRAM_TOKEN, APP_NAME, VERSION
from services.finnhub_api import get_quote


# =========================
# SAFE ACCESS
# =========================
def safe(data, key, default=0):
    try:
        return data.get(key, default)
    except:
        return default


# =========================
# INDICATORS (SIMPLIFIÉS MAIS PRO)
# =========================

def ema(values, period=10):
    if not values:
        return 0
    k = 2 / (period + 1)
    e = values[0]
    for v in values:
        e = v * k + e * (1 - k)
    return e


def rsi(values, period=14):
    if len(values) < 2:
        return 50

    gains = 0
    losses = 0

    for i in range(1, len(values)):
        diff = values[i] - values[i - 1]
        if diff >= 0:
            gains += diff
        else:
            losses += abs(diff)

    if losses == 0:
        return 100

    rs = gains / losses
    return 100 - (100 / (1 + rs))


def atr(high, low):
    if not high or not low:
        return 0
    return sum([h - l for h, l in zip(high, low)]) / len(high)


# =========================
# ACTIFS
# =========================
BINARY_ASSETS = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD"]
CLASSIC_ASSETS = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "NAS100"]


# =========================
# MENU
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

PREDICTHOOD V4 ENGINE

Statut : ONLINE

Choisis un module :
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
# ENGINE CORE
# =========================
def confluence_score(price, ema_val, rsi_val):

    score = 50

    # Trend EMA
    if price > ema_val:
        score += 20
    else:
        score -= 20

    # RSI logic
    if rsi_val < 30:
        score += 20
    elif rsi_val > 70:
        score -= 20

    return max(0, min(100, score))


# =========================
# ANALYSE MARKET
# =========================
async def analyse(update: Update, context: ContextTypes.DEFAULT_TYPE):

    symbol = "AAPL"
    data = get_quote(symbol)

    if not data:
        await update.message.reply_text("Erreur données.")
        return

    price = safe(data, "current", 100)

    # simulation historique (plan gratuit fallback)
    history = [price * (1 + i * 0.001) for i in range(-10, 10)]

    ema_val = ema(history)
    rsi_val = rsi(history)

    score = confluence_score(price, ema_val, rsi_val)

    trend = "HAUSSIER" if price > ema_val else "BAISSIER"

    signal = "ATTENTE"
    if score >= 70:
        signal = "CALL"
    elif score <= 30:
        signal = "PUT"

    await update.message.reply_text(f"""
PREDICTHOOD V4 ANALYSE

Actif : {symbol}

Prix : {price}
EMA : {round(ema_val,2)}
RSI : {round(rsi_val,2)}

Trend : {trend}
Confluence Score : {score}/100

SIGNAL : {signal}
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

    ema_val = ema(history)
    rsi_val = rsi(history)
    score = confluence_score(price, ema_val, rsi_val)

    signal = "ATTENTE"
    if score >= 75:
        signal = "CALL (1-3 MIN)"
    elif score <= 25:
        signal = "PUT (1-3 MIN)"

    await update.message.reply_text(f"""
OPTION BINAIRE V4

Actif : {symbol}
RSI : {round(rsi_val,2)}
EMA : {round(ema_val,2)}
Score : {score}

SIGNAL : {signal}
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

    ema_val = ema(history)
    rsi_val = rsi(history)
    score = confluence_score(price, ema_val, rsi_val)

    signal = "ATTENTE"
    if score >= 65:
        signal = "BUY"
    elif score <= 35:
        signal = "SELL"

    await update.message.reply_text(f"""
TRADING CLASSIQUE V4

Actif : {symbol}
RSI : {round(rsi_val,2)}
EMA : {round(ema_val,2)}
Score : {score}

SIGNAL : {signal}
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
        await update.message.reply_text(
            "BINARY:\n" + "\n".join(BINARY_ASSETS) +
            "\n\nCLASSIC:\n" + "\n".join(CLASSIC_ASSETS)
        )


# =========================
# MAIN STABLE
# =========================
def main():

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu))

    print("PredictHood V4 RUNNING...")

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
