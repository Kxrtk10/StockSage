import os
import httpx
from fastapi import APIRouter
from dotenv import load_dotenv

load_dotenv()
router = APIRouter(tags=["news_feed"])
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

@router.get("/api/live-news")
async def get_live_news():
    try:
        queries = [
            "Indian stock market NSE BSE Sensex Nifty",
            "US stock market NASDAQ NYSE Wall Street"
        ]
        all_articles = []
        async with httpx.AsyncClient() as client:
            for query in queries:
                url = f"https://newsapi.org/v2/everything?q={query}&language=en&sortBy=publishedAt&pageSize=6&apiKey={NEWS_API_KEY}"
                res = await client.get(url, timeout=10)
                data = res.json()
                if data.get("status") == "ok":
                    all_articles.extend(data.get("articles", []))
        seen = set()
        unique = []
        for a in all_articles:
            if a.get("title") and a["title"] not in seen and a.get("description"):
                seen.add(a["title"])
                unique.append(a)
        formatted = []
        for a in unique[:12]:
            source = a.get("source", {}).get("name", "Unknown")
            title = a.get("title", "")
            description = a.get("description", "")
            url = a.get("url", "")
            published = a.get("publishedAt", "")
            is_india = any(word in title.lower() + description.lower() for word in ["india", "nse", "bse", "sensex", "nifty", "rupee", "rbi", "sebi", "mumbai"])
            market = "INDIA" if is_india else "US"
            sector = "General"
            text = title.lower() + description.lower()
            if any(w in text for w in ["bank", "rbi", "fed", "rate", "loan", "credit"]): sector = "Banking"
            elif any(w in text for w in ["tech", "ai", "software", "apple", "google", "nvidia", "microsoft"]): sector = "Tech"
            elif any(w in text for w in ["oil", "energy", "solar", "power", "gas", "renewable"]): sector = "Energy"
            elif any(w in text for w in ["auto", "car", "ev", "vehicle", "tata motors", "tesla"]): sector = "Auto"
            formatted.append({
                "source": source,
                "title": title,
                "summary": description[:200] + "..." if len(description) > 200 else description,
                "url": url,
                "market": market,
                "sector": sector.lower(),
                "sentiment": "Neutral",
                "time": "Just now"
            })
        return {"success": True, "articles": formatted}
    except Exception as e:
        print(f"News API error: {e}")
        return {"success": False, "articles": []}
