import os
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from database import get_db
from routes.auth import verify_token

router = APIRouter(tags=["history"])

class MessageSave(BaseModel):
    role: str
    message: str
    page: str = "chat"

def get_user_from_request(request: Request):
    token = request.cookies.get("auth_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not logged in")
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload["user_id"]

@router.post("/api/history/save")
async def save_message(req: MessageSave, request: Request):
    try:
        user_id = get_user_from_request(request)
        conn = get_db()
        conn.execute(
            "INSERT INTO chat_history (user_id, role, message, page) VALUES (?, ?, ?, ?)",
            (user_id, req.role, req.message, req.page)
        )
        conn.commit()
        conn.close()
        return {"success": True}
    except HTTPException:
        return {"success": False, "error": "Not authenticated"}
    except Exception as e:
        print(f"History save error: {e}")
        return {"success": False, "error": str(e)}

@router.get("/api/history/{page}")
async def get_history(page: str, request: Request):
    try:
        user_id = get_user_from_request(request)
        conn = get_db()
        rows = conn.execute(
            "SELECT role, message, created_at FROM chat_history WHERE user_id = ? AND page = ? ORDER BY created_at ASC LIMIT 50",
            (user_id, page)
        ).fetchall()
        conn.close()
        return {"success": True, "messages": [{"role": r["role"], "message": r["message"]} for r in rows]}
    except HTTPException:
        return {"success": True, "messages": []}
    except Exception as e:
        print(f"History fetch error: {e}")
        return {"success": True, "messages": []}

@router.delete("/api/history/{page}")
async def clear_history(page: str, request: Request):
    try:
        user_id = get_user_from_request(request)
        conn = get_db()
        conn.execute("DELETE FROM chat_history WHERE user_id = ? AND page = ?", (user_id, page))
        conn.commit()
        conn.close()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
