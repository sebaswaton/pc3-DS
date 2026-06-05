from abc import ABC, abstractmethod
import hashlib
import uuid
from datetime import datetime, timezone


class SignatureService(ABC):
    @abstractmethod
    def sign(self, user_id: str, initiative_id: str, db: dict) -> dict:
        pass


class BaseSignatureService(SignatureService):
    def sign(self, user_id: str, initiative_id: str, db: dict) -> dict:
        sig = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "initiative_id": initiative_id,
            "status": "VALIDA",
        }
        db["signatures"][sig["id"]] = sig
        return sig


class SignatureDecorator(SignatureService):
    def __init__(self, wrapped: SignatureService):
        self._wrapped = wrapped

    def sign(self, user_id: str, initiative_id: str, db: dict) -> dict:
        return self._wrapped.sign(user_id, initiative_id, db)


class DuplicateCheckDecorator(SignatureDecorator):
    def sign(self, user_id: str, initiative_id: str, db: dict) -> dict:
        already_signed = any(
            s["user_id"] == user_id and s["initiative_id"] == initiative_id
            for s in db.get("signatures", {}).values()
        )
        if already_signed:
            raise ValueError("El ciudadano ya firmo esta iniciativa")
        return super().sign(user_id, initiative_id, db)


class MetadataEnrichmentDecorator(SignatureDecorator):
    def sign(self, user_id: str, initiative_id: str, db: dict) -> dict:
        sig = super().sign(user_id, initiative_id, db)
        content = db.get("initiatives", {}).get(initiative_id, {}).get("content", "")
        sig["doc_hash"] = hashlib.sha256(content.encode()).hexdigest()
        sig["timestamp"] = datetime.now(timezone.utc).isoformat()
        db["signatures"][sig["id"]] = sig
        return sig
