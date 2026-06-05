# Pattern: Decorator
# Agrega responsabilidades a SignatureService de forma dinamica
# sin modificar la clase base.
# DuplicateCheckDecorator: evita que un ciudadano firme dos veces.
# MetadataEnrichmentDecorator: enriquece la firma con hash del documento y timestamp.

from abc import ABC, abstractmethod
import hashlib
import uuid
from datetime import datetime, timezone


# --- Interfaz componente ---

class SignatureService(ABC):
    @abstractmethod
    def sign(self, user_id: str, initiative_id: str, db: dict) -> dict:
        pass


# --- Componente concreto ---

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


# --- Decorador base ---

class SignatureDecorator(SignatureService):
    def __init__(self, wrapped: SignatureService):
        self._wrapped = wrapped

    def sign(self, user_id: str, initiative_id: str, db: dict) -> dict:
        return self._wrapped.sign(user_id, initiative_id, db)


# --- Decoradores concretos ---

class DuplicateCheckDecorator(SignatureDecorator):
    """Rechaza una segunda firma del mismo ciudadano sobre la misma iniciativa."""

    def sign(self, user_id: str, initiative_id: str, db: dict) -> dict:
        already_signed = any(
            s["user_id"] == user_id and s["initiative_id"] == initiative_id
            for s in db.get("signatures", {}).values()
        )
        if already_signed:
            raise ValueError("El ciudadano ya firmo esta iniciativa")
        return super().sign(user_id, initiative_id, db)


class MetadataEnrichmentDecorator(SignatureDecorator):
    """Enriquece la firma con el hash SHA-256 del documento y el timestamp UTC."""

    def sign(self, user_id: str, initiative_id: str, db: dict) -> dict:
        sig = super().sign(user_id, initiative_id, db)
        content = db.get("initiatives", {}).get(initiative_id, {}).get("content", "")
        sig["doc_hash"] = hashlib.sha256(content.encode()).hexdigest()
        sig["timestamp"] = datetime.now(timezone.utc).isoformat()
        db["signatures"][sig["id"]] = sig
        return sig
