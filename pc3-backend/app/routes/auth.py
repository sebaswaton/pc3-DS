import uuid
from fastapi import APIRouter, HTTPException
from app.database import store, add_audit
from app.models import RegisterRequest
from app.patterns.adapter import ReniecAdapter

router = APIRouter()
_verifier = ReniecAdapter()


@router.post("/register")
def register(req: RegisterRequest):
    user_id = str(uuid.uuid4())
    user = {
        "id": user_id,
        "name": req.name,
        "email": req.email,
        "verified": False,
    }
    store["users"][user_id] = user
    add_audit("REGISTER", user_id, user_id)
    return user


@router.post("/verify/{user_id}")
def verify_identity(user_id: str):
    user = store["users"].get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    verified = _verifier.verify(user_id)
    user["verified"] = verified
    add_audit("VERIFY", user_id, user_id, f"result={verified}")
    return {"user_id": user_id, "verified": verified}


@router.get("/users")
def list_users():
    return list(store["users"].values())
