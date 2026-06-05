import uuid
import hashlib
from fastapi import APIRouter, HTTPException
from app.database import store, add_audit
from app.models import RegisterRequest, LoginRequest
from app.patterns.adapter import ReniecAdapter

router = APIRouter()
_verifier = ReniecAdapter()


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _safe(user: dict) -> dict:
    return {k: v for k, v in user.items() if k != "password"}


@router.post("/register")
def register(req: RegisterRequest):
    if any(u["email"] == req.email for u in store["users"].values()):
        raise HTTPException(status_code=400, detail="El email ya esta registrado")

    verified = _verifier.verify(req.dni)
    user_id = str(uuid.uuid4())
    user = {
        "id": user_id,
        "name": req.name,
        "email": req.email,
        "dni": req.dni,
        "password": _hash(req.password),
        "verified": verified,
    }
    store["users"][user_id] = user
    add_audit("REGISTER", user_id, user_id, f"verified={verified}")
    return _safe(user)


@router.post("/login")
def login(req: LoginRequest):
    user = next((u for u in store["users"].values() if u["email"] == req.email), None)
    if not user or user["password"] != _hash(req.password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    return _safe(user)


@router.get("/users")
def list_users():
    return [_safe(u) for u in store["users"].values()]
