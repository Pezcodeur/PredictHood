import requests
from config.settings import FINNHUB_API_KEY

BASE_URL = "https://finnhub.io/api/v1"


def get_quote(symbol: str):
    """
    Récupère les informations de marché d'un actif.

    Exemple :
    get_quote("AAPL")
    get_quote("BINANCE:BTCUSDT")
    """

    url = f"{BASE_URL}/quote"

    params = {
        "symbol": symbol,
        "token": FINNHUB_API_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return None

    data = response.json()

    return {
        "current": data.get("c"),
        "high": data.get("h"),
        "low": data.get("l"),
        "open": data.get("o"),
        "previous_close": data.get("pc")
  }# Connexion API Finnhub
