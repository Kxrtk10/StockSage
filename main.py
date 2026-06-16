from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from database import init_db
from routes import budget, chat, news
from routes.auth import router as auth_router
from routes.news_feed import router as news_feed_router
from routes.stocks import router as stocks_router
from routes.history import router as history_router
load_dotenv()
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
app = FastAPI(title="StockSage AI")
init_db()
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.include_router(chat.router)
app.include_router(budget.router)
app.include_router(news.router)
app.include_router(auth_router)
app.include_router(news_feed_router)
app.include_router(stocks_router)
app.include_router(history_router)
@app.get("/")
async def root():
    return FileResponse(STATIC_DIR / "index.html")
@app.get("/chat")
async def chat_page():
    return FileResponse(STATIC_DIR / "chat.html")
@app.get("/budget")
async def budget_page():
    return FileResponse(STATIC_DIR / "budget.html")
@app.get("/news")
async def news_page():
    return FileResponse(STATIC_DIR / "news.html")
@app.get("/news-detail")
async def news_detail_page():
    return FileResponse(STATIC_DIR / "news-detail.html")
@app.get("/login")
async def login_page():
    return FileResponse(STATIC_DIR / "login.html")
@app.get("/register")
async def register_page():
    return FileResponse(STATIC_DIR / "register.html")
@app.get("/assistant")
async def assistant_page():
    return FileResponse(STATIC_DIR / "assistant.html")
@app.get("/profile")
async def profile_page():
    return FileResponse(STATIC_DIR / "profile.html")
@app.get("/markets")
async def markets_page():
    return FileResponse(STATIC_DIR / "markets.html")
@app.get("/stock-detail")
async def stock_detail_page():
    return FileResponse(STATIC_DIR / "stock-detail.html")
