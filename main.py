import requests
from datetime import datetime, timedelta

# === Configuration ===
TELEGRAM_CHAT_ID = "insert_id"
TELEGRAM_TOKEN = "insert_token"
ALPHAVANTAGE_API = "insert_api_key"
NEWS_API = "insert_api_key"

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

ALPHAVANTAGE_URL = "https://www.alphavantage.co/query"
NEWS_URL = "https://newsapi.org/v2/everything"

# === STEP 1: Get Stock Data ===
def get_stocks(symbol):
    params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": symbol,
        "apikey": ALPHAVANTAGE_API,
    }
    response = requests.get(ALPHAVANTAGE_URL, params=params)
    response.raise_for_status()
    return response.json().get("Time Series (Daily)", {})

# === STEP 2: Get News ===
def get_news(company_name, from_date, to_date):
    params = {
        "q": company_name,
        "from": from_date,
        "to": to_date,
        "language": "en",
        "sortBy": "relevancy",
        "pageSize": 3,
        "apiKey": NEWS_API,
    }
    response = requests.get(NEWS_URL, params=params)
    response.raise_for_status()
    return response.json().get("articles", [])

# === STEP 3: Send Telegram Message ===
def send_telegram_message(message):
    params = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
    }
    response = requests.post(
        url=f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        params=params
    )
    response.raise_for_status()
    return response.json()

# === Main Logic ===
def main():
    today = datetime.now()
    yesterday = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    day_before_yesterday = (today - timedelta(days=2)).strftime("%Y-%m-%d")

    stocks = get_stocks(STOCK)

    try:
        stock_yesterday = float(stocks[yesterday]["4. close"])
        stock_day_before = float(stocks[day_before_yesterday]["4. close"])
    except KeyError:
        send_telegram_message("Error: Could not fetch stock data for given dates.")
        return

    percent_diff = abs((stock_yesterday - stock_day_before) / stock_day_before * 100)

    if percent_diff >= 5:
        articles = get_news(COMPANY_NAME, day_before_yesterday, yesterday)
        if articles:
            for article in articles[:3]:
                title = article.get("title", "No title")
                brief = article.get("description", "No description")
                message = f"{STOCK}: 🔺{percent_diff:.2f}%\nHeadline: {title}\nBrief: {brief}"
                send_telegram_message(message)
        else:
            send_telegram_message(f"{STOCK}: Significant movement detected but no news found.")
    else:
        send_telegram_message(f"{STOCK}: No significant change ({percent_diff:.2f}%).")

if __name__ == "__main__":
    main()
