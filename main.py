import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from config.settings import TELEGRAM_TOKEN, APP_NAME, VERSION
from analysis.engine import analyze_symbol


# =========================
# ACTIFS
# =========================
BINARY = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD"]
CLASSIC = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "NAS100"]


# =========================
# MENU PRO (SANS EMOJI)
# =========================
MENU = [
    ["ANALYSE"],
    ["BINARY", "CLASSIC"],
    ["SCANNER"],
    ["HELP"]
]


# =========================
# FORMAT TERMINAL
# =========================
def box(title: str, content: str):

    line = "─" * 40
    return f"""
{line}
{title}
{line}
{content}
{line}
"""


# =========================
# START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = ReplyKeyboardMarkup(MENU, resize_keyboard=True)

    content = f"""
{APP_NAME}
VERSION: {VERSION}

PREDICTHOOD TRADING ENGINE

STATUS: ONLINE
MODE: MANUAL
"""

    await update.message.reply_text(box("SYSTEM", content), reply_markup=keyboard)


# =========================
# HELP
# =========================
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):

    content = """
ANALYSE   -> Market analysis
BINARY    -> Short term signals
CLASSIC   -> Swing trading signals
SCANNER   -> Best opportunities

NOTE: Manual trading only
"""

    await update.message.reply_text(box("HELP", content))


# =========================
# ANALYSE
# =========================
async def analyse(update: Update, context: ContextTypes.DEFAULT_TYPE):

    symbol = "AAPL"
    r = analyze_symbol(symbol)

    if not r:
        await update.message.reply_text("ERROR: NO DATA")
        return

    content = f"""
SYMBOL: {r['symbol']}
PRICE: {r['price']}

EMA FAST: {r['ema_fast']}
EMA SLOW: {r['ema_slow']}
RSI: {r['rsi']}
VOL: {r['volatility']}

SCORE: {r['score']}/100
SIGNAL: {r['signal']}
"""

    await update.message.reply_text(box("MARKET ANALYSIS", content))


# =========================
# BINARY
# =========================
async def binary(update: Update, context: ContextTypes.DEFAULT_TYPE):

    symbol = "EURUSD"
    r = analyze_symbol(symbol)

    if not r:
        await update.message.reply_text("ERROR: NO DATA")
        return

    signal = "WAIT"

    if r["score"] >= 75:
        signal = "CALL"
    elif r["score"] <= 25:
        signal = "PUT"

    content = f"""
SYMBOL: {symbol}
RSI: {r['rsi']}
SCORE: {r['score']}

SIGNAL: {signal}
"""

    await update.message.reply_text(box("BINARY SIGNAL", content))


# =========================
# CLASSIC
# =========================
async def classic(update: Update, context: ContextTypes.DEFAULT_TYPE):

    symbol = "XAUUSD"
    r = analyze_symbol(symbol)

    if not r:
        await update.message.reply_text("ERROR: NO DATA")
        return

    signal = "WAIT"

    if r["score"] >= 65:
        signal = "BUY"
    elif r["score"] <= 35:
        signal = "SELL"

    content = f"""
SYMBOL: {symbol}
RSI: {r['rsi']}
SCORE: {r['score']}

SIGNAL: {signal}
"""

    await update.message.reply_text(box("CLASSIC SIGNAL", content))


# =========================
# SCANNER
# =========================
async def scanner(update: Update, context: ContextTypes.DEFAULT_TYPE):

    assets = BINARY + CLASSIC
    results = []

    for s in assets:
        r = analyze_symbol(s)
        if not r:
            continue

        if r["score"] < 60:
            continue

        if s == "XAUUSD":
            r["score"] += 5

        results.append(r)

    if not results:
        await update.message.reply_text("NO OPPORTUNITIES")
        return

    results.sort(key=lambda x: x["score"], reverse=True)
    best = results[0]

    content = f"""
BEST SETUP

SYMBOL: {best['symbol']}
PRICE: {best['price']}
SCORE: {best['score']}
SIGNAL: {best['signal']}

TOP 3
"""

    for r in results[:3]:
        content += f"""
{r['symbol']} | {r['score']} | {r['signal']}
"""

    await update.message.reply_text(box("SCANNER PRO", content))


# =========================
# ROUTER
# =========================
async def router(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.upper()

    if text == "ANALYSE":
        await analyse(update, context)

    elif text == "BINARY":
        await binary(update, context)

    elif text == "CLASSIC":
        await classic(update, context)

    elif text == "SCANNER":
        await scanner(update, context)

    elif text == "HELP":
        await help_cmd(update, context)


# =========================
# MAIN
# =========================
def main():

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, router))

    print("PREDICTHOOD TERMINAL MODE RUNNING...")

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
