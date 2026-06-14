from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from routes import budget, chat, news


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="StockSage AI")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.include_router(chat.router)
app.include_router(budget.router)
app.include_router(news.router)


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
