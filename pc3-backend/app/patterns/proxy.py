# Pattern: Proxy
# CryptographicSealProxy controla el acceso al expediente de una iniciativa.
# Antes del sellado: delega lecturas y escrituras al sujeto real.
# Despues del sellado: deniega toda operacion de escritura (expediente de solo lectura).
# Al sellar: genera hash SHA-512 y registra el timestamp del sello.

import hashlib
import json
from datetime import datetime, timezone


# --- Sujeto real ---

class InitiativeExpedient:
    def __init__(self, initiative_id: str, db: dict):
        self._id = initiative_id
        self._db = db

    def get(self) -> dict:
        return self._db["initiatives"].get(self._id, {})

    def update(self, data: dict):
        self._db["initiatives"][self._id].update(data)


# --- Proxy ---

class CryptographicSealProxy:
    def __init__(self, expedient: InitiativeExpedient):
        self._expedient = expedient

    def _is_sealed(self) -> bool:
        return self._expedient.get().get("sealed", False)

    def get(self) -> dict:
        return self._expedient.get()

    def update(self, data: dict):
        if self._is_sealed():
            raise PermissionError("El expediente esta sellado. No se permiten modificaciones.")
        self._expedient.update(data)

    def seal(self) -> str:
        if self._is_sealed():
            raise PermissionError("El expediente ya fue sellado anteriormente")

        content = self._expedient.get()
        content_str = json.dumps(content, sort_keys=True, default=str)
        seal_hash = hashlib.sha512(content_str.encode()).hexdigest()

        self._expedient.update({
            "sealed": True,
            "seal_hash": seal_hash,
            "sealed_at": datetime.now(timezone.utc).isoformat(),
            "status": "LISTA_PARA_ENVIO",
        })
        return seal_hash
