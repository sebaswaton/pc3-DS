# Pattern: Facade
# InitiativeFacade provee una interfaz unica y simplificada que orquesta
# los subsistemas: Adapter (RENIEC), Decorator (firmas), Proxy (sellado)
# y Adapter (despacho al Congreso). Los clientes interactuan solo con
# la Facade, nunca con los subsistemas directamente.

from datetime import datetime, timezone, timedelta
import uuid

from app.database import store, add_audit
from app.patterns.adapter import ReniecAdapter, CongressApiAdapter
from app.patterns.decorator import (
    BaseSignatureService,
    DuplicateCheckDecorator,
    MetadataEnrichmentDecorator,
)
from app.patterns.proxy import CryptographicSealProxy, InitiativeExpedient

SIGNATURE_THRESHOLD = 25000
DEADLINE_DAYS = 90


class InitiativeFacade:
    def __init__(self):
        self._identity_verifier = ReniecAdapter()
        base_sig = BaseSignatureService()
        self._signature_service = MetadataEnrichmentDecorator(
            DuplicateCheckDecorator(base_sig)
        )
        self._congress_adapter = CongressApiAdapter()

    # --- Operaciones publicas de la Facade ---

    def create_initiative(self, title: str, content: str, author_id: str) -> dict:
        initiative_id = str(uuid.uuid4())
        initiative = {
            "id": initiative_id,
            "title": title,
            "content": content,
            "author_id": author_id,
            "status": "BORRADOR",
            "signature_count": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "published_at": None,
            "deadline": None,
            "sealed": False,
            "seal_hash": None,
            "sealed_at": None,
            "radicacion": None,
        }
        store["initiatives"][initiative_id] = initiative
        add_audit("CREATE", author_id, initiative_id)
        return initiative

    def publish_initiative(self, initiative_id: str, author_id: str) -> dict:
        initiative = store["initiatives"].get(initiative_id)
        if not initiative:
            raise ValueError("Iniciativa no encontrada")
        if initiative["status"] != "BORRADOR":
            raise ValueError("Solo se puede publicar una iniciativa en estado BORRADOR")
        if initiative["author_id"] != author_id:
            raise PermissionError("Solo el autor puede publicar la iniciativa")

        now = datetime.now(timezone.utc)
        initiative["status"] = "ACTIVA"
        initiative["published_at"] = now.isoformat()
        initiative["deadline"] = (now + timedelta(days=DEADLINE_DAYS)).isoformat()
        add_audit("PUBLISH", author_id, initiative_id)
        return initiative

    def sign_initiative(self, initiative_id: str, user_id: str) -> dict:
        initiative = store["initiatives"].get(initiative_id)
        if not initiative:
            raise ValueError("Iniciativa no encontrada")
        if initiative["status"] != "ACTIVA":
            raise ValueError("La iniciativa no esta activa")

        user = store["users"].get(user_id)
        if not user or not user.get("verified"):
            raise PermissionError("El ciudadano debe estar verificado para firmar")

        # Decorator chain: DuplicateCheck -> MetadataEnrichment -> Base
        signature = self._signature_service.sign(user_id, initiative_id, store)
        initiative["signature_count"] += 1
        add_audit("SIGN", user_id, initiative_id)

        if initiative["signature_count"] >= SIGNATURE_THRESHOLD:
            self._seal_and_dispatch(initiative_id)

        return signature

    def manual_seal_and_dispatch(self, initiative_id: str) -> dict:
        initiative = store["initiatives"].get(initiative_id)
        if not initiative:
            raise ValueError("Iniciativa no encontrada")
        # Delegar al Proxy primero: el detecta si ya fue sellado
        if initiative.get("sealed"):
            expedient = InitiativeExpedient(initiative_id, store)
            CryptographicSealProxy(expedient).seal()  # lanza PermissionError
        if initiative["status"] not in ("ACTIVA", "LISTA_PARA_ENVIO"):
            raise ValueError("La iniciativa no esta en un estado valido para sellar")
        return self._seal_and_dispatch(initiative_id)

    # --- Subsistema interno ---

    def _seal_and_dispatch(self, initiative_id: str) -> dict:
        # Proxy: sella criptograficamente el expediente
        expedient = InitiativeExpedient(initiative_id, store)
        proxy = CryptographicSealProxy(expedient)
        seal_hash = proxy.seal()

        # Adapter: envia a la API del Congreso
        result = self._congress_adapter.send(
            initiative_id, store["initiatives"][initiative_id]
        )
        store["initiatives"][initiative_id]["status"] = "ENVIADA"
        store["initiatives"][initiative_id]["radicacion"] = result["numero_radicacion"]
        add_audit("SEAL_AND_SEND", "system", initiative_id, f"hash={seal_hash[:16]}...")
        return result
