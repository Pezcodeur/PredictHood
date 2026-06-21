def confluence_score(trend, rsi, ema_trend):
    score = 50

    # trend global
    if trend == "HAUSSIER":
        score += 20
    elif trend == "BAISSIER":
        score -= 20

    # RSI logique
    if rsi > 60:
        score += 10
    elif rsi < 40:
        score -= 10

    # EMA confirmation
    if ema_trend == "HAUSSIER":
        score += 20
    elif ema_trend == "BAISSIER":
        score -= 20

    return max(0, min(100, score))
