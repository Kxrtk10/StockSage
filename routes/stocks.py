import os
import httpx
from fastapi import APIRouter
from dotenv import load_dotenv

load_dotenv()
router = APIRouter(tags=["stocks"])
AV_KEY = os.getenv("ALPHA_VANTAGE_KEY")

SYMBOL_MAP = {
    "reliance": "RELIANCE.BSE",
    "reliance industries": "RELIANCE.BSE",
    "infosys": "INFY.BSE",
    "hdfc bank": "HDFCBANK.BSE",
    "tata motors": "TATAMOTORS.BSE",
    "tcs": "TCS.BSE",
    "tata consultancy": "TCS.BSE",
    "wipro": "WIPRO.BSE",
    "apple": "AAPL",
    "aapl": "AAPL",
    "tesla": "TSLA",
    "tsla": "TSLA",
    "nvidia": "NVDA",
    "nvda": "NVDA",
    "microsoft": "MSFT",
    "msft": "MSFT",
    "google": "GOOGL",
    "googl": "GOOGL",
    "amazon": "AMZN",
    "amzn": "AMZN",
    "meta": "META",
    "netflix": "NFLX",
    "nflx": "NFLX",
}

@router.get("/api/stock-price/{symbol}")
async def get_stock_price(symbol: str):
    try:
        key = symbol.lower().strip()
        ticker = SYMBOL_MAP.get(key, symbol.upper())
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={AV_KEY}"
        async with httpx.AsyncClient() as client:
            res = await client.get(url, timeout=10)
            data = res.json()
        quote = data.get("Global Quote", {})
        if not quote or not quote.get("05. price"):
            return {"success": False, "error": "Price not found"}
        price = float(quote.get("05. price", 0))
        change = float(quote.get("09. change", 0))
        change_pct = quote.get("10. change percent", "0%").replace("%", "")
        prev_close = float(quote.get("08. previous close", 0))
        high = float(quote.get("03. high", 0))
        low = float(quote.get("04. low", 0))
        volume = quote.get("06. volume", "N/A")
        is_indian = ".BSE" in ticker or ".NSE" in ticker
        currency = "₹" if is_indian else "$"
        return {
            "success": True,
            "symbol": ticker,
            "price": f"{currency}{price:,.2f}",
            "change": f"{change:+.2f}",
            "change_pct": f"{float(change_pct):+.2f}%",
            "is_positive": change >= 0,
            "high": f"{currency}{high:,.2f}",
            "low": f"{currency}{low:,.2f}",
            "prev_close": f"{currency}{prev_close:,.2f}",
            "volume": volume,
            "currency": currency
        }
    except Exception as e:
        print(f"Stock price error: {e}")
        return {"success": False, "error": str(e)}

@router.get("/api/market-indices")
async def get_market_indices():
    try:
        symbols = {
            "NIFTY 50": "NIFTY50.NSE",
            "SENSEX": "SENSEX.BSE",
            "S&P 500": "SPX",
            "NASDAQ": "IXIC"
        }
        results = {}
        async with httpx.AsyncClient() as client:
            for name, symbol in symbols.items():
                url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={AV_KEY}"
                res = await client.get(url, timeout=10)
                data = res.json()
                quote = data.get("Global Quote", {})
                if quote and quote.get("05. price"):
                    price = float(quote.get("05. price", 0))
                    change = float(quote.get("09. change", 0))
                    change_pct = quote.get("10. change percent", "0%").replace("%", "")
                    results[name] = {
                        "price": f"{price:,.2f}",
                        "change": f"{change:+.2f}",
                        "change_pct": f"{float(change_pct):+.2f}%",
                        "is_positive": change >= 0
                    }
        return {"success": True, "indices": results}
    except Exception as e:
        print(f"Indices error: {e}")
        return {"success": False, "indices": {}}
