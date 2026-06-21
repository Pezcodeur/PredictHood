def confluence_score(trend, rsi, ema_bullish):
    """
    Score intelligent basé sur confluence
    """

    score = 50

    # tendance principale
    if trend == "HAUSSIER":
        score += 20
    elif trend == "BAISSIER":
        score -= 20

    # RSI logique (pas signal seul)
    if rsi > 55:
        score += 10
    elif rsi < 45:
        score -= 10

    # EMA confirmation
    if ema_bullish:
        score += 20
    else:
        score -= 20

    return max(0, min(100, score))
