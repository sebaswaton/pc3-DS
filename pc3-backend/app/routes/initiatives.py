from fastapi import APIRouter, HTTPException
from app.database import store
from app.models import CreateInitiativeRequest
from app.patterns.facade import InitiativeFacade

router = APIRouter()
_facade = InitiativeFacade()


@router.get("")
def list_initiatives():
    return list(store["initiatives"].values())


@router.post("")
def create_initiative(req: CreateInitiativeRequest):
    if req.author_id not in store["users"]:
        raise HTTPException(status_code=404, detail="Autor no encontrado")
    return _facade.create_initiative(req.title, req.content, req.author_id)


@router.get("/audit/log")
def get_audit_log():
    return store["audit_log"]


@router.get("/{initiative_id}")
def get_initiative(initiative_id: str):
    initiative = store["initiatives"].get(initiative_id)
    if not initiative:
        raise HTTPException(status_code=404, detail="Iniciativa no encontrada")
    return initiative


@router.post("/{initiative_id}/publish")
def publish_initiative(initiative_id: str, body: dict):
    author_id = body.get("author_id")
    if not author_id:
        raise HTTPException(status_code=400, detail="Se requiere author_id")
    try:
        return _facade.publish_initiative(initiative_id, author_id)
    except (ValueError, PermissionError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{initiative_id}/seal")
def seal_initiative(initiative_id: str):
    try:
        return _facade.manual_seal_and_dispatch(initiative_id)
    except (ValueError, PermissionError) as e:
        raise HTTPException(status_code=400, detail=str(e))
