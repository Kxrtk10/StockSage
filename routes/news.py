from fastapi import APIRouter


router = APIRouter(prefix="/api/news", tags=["news"])


@router.post("/")
async def news():
    return {"status": "ok", "message": "endpoint working"}
