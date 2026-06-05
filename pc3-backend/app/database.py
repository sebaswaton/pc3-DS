from datetime import datetime, timezone

# In-memory store. In production this would be a real database.
store = {
    "users": {},        # user_id -> user dict
    "initiatives": {},  # initiative_id -> initiative dict
    "signatures": {},   # sig_id -> signature dict
    "comments": {},     # initiative_id -> list of comment dicts
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
