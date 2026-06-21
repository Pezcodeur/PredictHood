def basic_score(price_data):
    """
    Score simple basé sur volatilité et mouvement
    """

    if not price_data:
        return 0

    try:
        high = price_data.get("high", 0)
        low = price_data.get("low", 0)
        current = price_data.get("current", 0)

        if high == 0 or low == 0:
            return 0

        volatility = abs(high - low)

        if volatility == 0:
            return 30

        position = abs(current - low) / volatility * 100

        score = 50 + (position - 50)

        return round(max(0, min(100, score)))

    except:
        return 0# Calcul du score PredictHood
