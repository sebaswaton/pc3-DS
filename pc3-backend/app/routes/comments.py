from fastapi import APIRouter, HTTPException
from app.database import store
from app.models import CommentRequest
from app.patterns.composite import build_comment

router = APIRouter()


@router.post("/{initiative_id}/comments")
def add_comment(initiative_id: str, req: CommentRequest):
    if initiative_id not in store["initiatives"]:
        raise HTTPException(status_code=404, detail="Iniciativa no encontrada")

    parent_depth = 0
    if req.parent_id:
        existing = store["comments"].get(initiative_id, [])
        parent = next((c for c in existing if c["id"] == req.parent_id), None)
        if not parent:
            raise HTTPException(status_code=404, detail="Comentario padre no encontrado")
        parent_depth = parent.get("level", 0)

    try:
        comment = build_comment(req.text, req.author_id, req.parent_id, parent_depth + 1)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    comment_data = comment.get_data()
    store["comments"].setdefault(initiative_id, []).append(comment_data)
    return comment_data


@router.get("/{initiative_id}/comments")
def get_comments(initiative_id: str):
    all_comments = store["comments"].get(initiative_id, [])
    roots = [c for c in all_comments if c["parent_id"] is None]

    def attach_children(node: dict) -> dict:
        node = dict(node)
        node["children"] = [
            attach_children(dict(c))
            for c in all_comments
            if c["parent_id"] == node["id"]
        ]
        return node

    return {"initiative_id": initiative_id, "comments": [attach_children(r) for r in roots]}
