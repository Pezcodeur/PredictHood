def detect_trend(price_data):
    """
    Détection simple de tendance basée sur open / current / previous close
    """

    if not price_data:
        return "NEUTRE"

    try:
        current = price_data.get("current", 0)
        open_price = price_data.get("open", 0)
        prev_close = price_data.get("previous_close", 0)

        if current == 0 or open_price == 0:
            return "NEUTRE"

        # comparaison simple
        if current > open_price and current > prev_close:
            return "HAUSSIER"

        if current < open_price and current < prev_close:
            return "BAISSIER"

        return "NEUTRE"

    except:
        return "NEUTRE"
