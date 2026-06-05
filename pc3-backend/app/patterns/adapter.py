# Pattern: Adapter
# Convierte la interfaz de servicios externos (RENIEC, API del Congreso)
# a la interfaz interna que espera el dominio de la aplicacion.
# Los stubs simulan lo que devolverian los servicios reales.

from abc import ABC, abstractmethod


# --- Interfaces objetivo (dominio interno) ---

class IdentityVerifier(ABC):
    @abstractmethod
    def verify(self, user_id: str) -> bool:
        pass


class ExpedientDispatcher(ABC):
    @abstractmethod
    def send(self, initiative_id: str, content: dict) -> dict:
        pass


# --- Adaptados (servicios externos con su propia interfaz incompatible) ---

class ReniecServiceStub:
    """Simula el servicio externo RENIEC con su propio formato."""

    def consultar_identidad(self, numero_documento: str) -> dict:
        return {
            "valido": True,
            "estado": "activo",
            "num_doc": numero_documento,
        }


class CongressApiStub:
    """Simula la API externa del Congreso con su propio formato."""

    def recibir_expediente(self, payload: dict) -> dict:
        radicacion = f"RAD-{payload['id'][:8].upper()}"
        return {"numero_radicacion": radicacion, "estado": "recibido"}


# --- Adaptadores ---

class ReniecAdapter(IdentityVerifier):
    """Adapta ReniecServiceStub a la interfaz IdentityVerifier."""

    def __init__(self):
        self._reniec = ReniecServiceStub()

    def verify(self, user_id: str) -> bool:
        result = self._reniec.consultar_identidad(user_id)
        return result.get("valido", False) and result.get("estado") == "activo"


class CongressApiAdapter(ExpedientDispatcher):
    """Adapta CongressApiStub a la interfaz ExpedientDispatcher."""

    def __init__(self):
        self._api = CongressApiStub()

    def send(self, initiative_id: str, content: dict) -> dict:
        payload = {"id": initiative_id, "contenido": content, "formato": "JSON-LD"}
        return self._api.recibir_expediente(payload)
