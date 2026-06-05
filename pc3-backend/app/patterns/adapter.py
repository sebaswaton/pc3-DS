from abc import ABC, abstractmethod


class IdentityVerifier(ABC):
    @abstractmethod
    def verify(self, identifier: str) -> bool:
        pass


class ExpedientDispatcher(ABC):
    @abstractmethod
    def send(self, initiative_id: str, content: dict) -> dict:
        pass


class ReniecServiceStub:
    def consultar_identidad(self, numero_documento: str) -> dict:
        es_valido = (
            len(numero_documento) == 8
            and numero_documento.isdigit()
            and numero_documento != "00000000"
        )
        return {
            "valido": es_valido,
            "estado": "activo" if es_valido else "inactivo",
            "num_doc": numero_documento,
        }


class CongressApiStub:
    def recibir_expediente(self, payload: dict) -> dict:
        radicacion = f"RAD-{payload['id'][:8].upper()}"
        return {"numero_radicacion": radicacion, "estado": "recibido"}


class ReniecAdapter(IdentityVerifier):
    def __init__(self):
        self._reniec = ReniecServiceStub()

    def verify(self, identifier: str) -> bool:
        result = self._reniec.consultar_identidad(identifier)
        return result.get("valido", False) and result.get("estado") == "activo"


class CongressApiAdapter(ExpedientDispatcher):
    def __init__(self):
        self._api = CongressApiStub()

    def send(self, initiative_id: str, content: dict) -> dict:
        payload = {"id": initiative_id, "contenido": content, "formato": "JSON-LD"}
        return self._api.recibir_expediente(payload)
