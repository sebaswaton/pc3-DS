from datetime import datetime, timezone

store = {
    "users": {},
    "initiatives": {},
    "signatures": {},
    "comments": {},
    "audit_log": [],
}


def add_audit(action: str, actor: str, entity_id: str, detail: str = ""):
    store["audit_log"].append({
        "action": action,
        "actor": actor,
        "entity_id": entity_id,
        "detail": detail,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
