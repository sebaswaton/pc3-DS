from fastapi import APIRouter, HTTPException
from app.database import store
from app.models import SignRequest
from app.patterns.facade import InitiativeFacade

router = APIRouter()
_facade = InitiativeFacade()


@router.post("/{initiative_id}/sign")
def sign_initiative(initiative_id: str, req: SignRequest):
    try:
        signature = _facade.sign_initiative(initiative_id, req.user_id)
        initiative = store["initiatives"].get(initiative_id, {})
        return {
            "signature": signature,
            "signature_count": initiative.get("signature_count", 0),
            "initiative_status": initiative.get("status"),
        }
    except (ValueError, PermissionError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{initiative_id}/signatures")
def list_signatures(initiative_id: str):
    sigs = [
        s for s in store["signatures"].values()
        if s["initiative_id"] == initiative_id
    ]
    return {"initiative_id": initiative_id, "count": len(sigs), "signatures": sigs}
