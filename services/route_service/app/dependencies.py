from fastapi import Request, HTTPException

async def get_current_user(request: Request):
    user_id = request.headers.get("X-User-ID")
    user_role = request.headers.get("X-User-Role")
    if not user_id or not user_role:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"id": int(user_id), "role": user_role}