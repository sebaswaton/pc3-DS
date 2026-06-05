import pytest
from fastapi.testclient import TestClient
from main import app
from app.database import store

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_store():
    """Limpia el store en memoria antes de cada test para garantizar aislamiento."""
    store["users"].clear()
    store["initiatives"].clear()
    store["signatures"].clear()
    store["comments"].clear()
    store["audit_log"].clear()
    yield


# --- Helpers reutilizables ---

def register_user(name="Ana Lopez", email="ana@test.com"):
    res = client.post("/api/auth/register", json={"name": name, "email": email})
    assert res.status_code == 200
    return res.json()


def register_verified_user(name="Ana Lopez", email="ana@test.com"):
    user = register_user(name, email)
    client.post(f"/api/auth/verify/{user['id']}")
    return user


def create_active_initiative(author_id, title="Ley de prueba", content="Art. 1. Se establece."):
    res = client.post("/api/initiatives", json={
        "title": title, "content": content, "author_id": author_id
    })
    assert res.status_code == 200
    initiative = res.json()
    pub = client.post(f"/api/initiatives/{initiative['id']}/publish",
                      json={"author_id": author_id})
    assert pub.status_code == 200
    return pub.json()


# =============================================================================
# CP-01 — Adapter: ReniecAdapter
# =============================================================================

class TestAdapterReniec:

    def test_verificacion_exitosa(self):
        """Usuario registrado puede ser verificado. El Adapter retorna True."""
        user = register_user()
        res = client.post(f"/api/auth/verify/{user['id']}")
        assert res.status_code == 200
        assert res.json()["verified"] is True

    def test_usuario_inexistente_devuelve_404(self):
        """El Adapter no llega al stub si el usuario no existe en el sistema."""
        res = client.post("/api/auth/verify/id-inexistente")
        assert res.status_code == 404

    def test_verificacion_es_idempotente(self):
        """Verificar dos veces al mismo usuario no produce error."""
        user = register_user()
        client.post(f"/api/auth/verify/{user['id']}")
        res = client.post(f"/api/auth/verify/{user['id']}")
        assert res.status_code == 200
        assert res.json()["verified"] is True

    def test_usuario_no_verificado_tiene_verified_false(self):
        """Un usuario recien registrado sin verificar tiene verified=False."""
        user = register_user()
        res = client.get("/api/auth/users")
        found = next(u for u in res.json() if u["id"] == user["id"])
        assert found["verified"] is False


# =============================================================================
# CP-02 — Facade: InitiativeFacade
# =============================================================================

class TestFacadeInitiative:

    def test_publicacion_exitosa(self):
        """La Facade orquesta correctamente: BORRADOR -> ACTIVA con deadline."""
        user = register_verified_user()
        res = client.post("/api/initiatives", json={
            "title": "Ley de agua potable",
            "content": "Art. 1. Acceso universal.",
            "author_id": user["id"]
        })
        initiative = res.json()
        assert initiative["status"] == "BORRADOR"
        assert initiative["published_at"] is None

        pub = client.post(f"/api/initiatives/{initiative['id']}/publish",
                          json={"author_id": user["id"]})
        assert pub.status_code == 200
        data = pub.json()
        assert data["status"] == "ACTIVA"
        assert data["published_at"] is not None
        assert data["deadline"] is not None

    def test_titulo_vacio_rechazado(self):
        """La Facade valida el titulo antes de crear."""
        user = register_verified_user()
        res = client.post("/api/initiatives", json={
            "title": "", "content": "Contenido.", "author_id": user["id"]
        })
        assert res.status_code == 422

    def test_publicacion_doble_rechazada(self):
        """Publicar una iniciativa ya ACTIVA lanza error de negocio."""
        user = register_verified_user()
        initiative = create_active_initiative(user["id"])
        res = client.post(f"/api/initiatives/{initiative['id']}/publish",
                          json={"author_id": user["id"]})
        assert res.status_code == 400
        assert "BORRADOR" in res.json()["detail"]

    def test_autor_incorrecto_no_puede_publicar(self):
        """Solo el autor puede publicar su iniciativa."""
        user = register_verified_user()
        otro = register_verified_user("Carlos", "carlos@test.com")
        res = client.post("/api/initiatives", json={
            "title": "Ley X", "content": "Art. 1.", "author_id": user["id"]
        })
        initiative = res.json()
        pub = client.post(f"/api/initiatives/{initiative['id']}/publish",
                          json={"author_id": otro["id"]})
        assert pub.status_code == 400
        assert "autor" in pub.json()["detail"].lower()


# =============================================================================
# CP-03 — Decorator: DuplicateCheckDecorator + MetadataEnrichmentDecorator
# =============================================================================

class TestDecoratorSignature:

    def test_primera_firma_valida_con_metadata(self):
        """La firma incluye doc_hash y timestamp inyectados por el Decorator."""
        user = register_verified_user()
        initiative = create_active_initiative(user["id"])
        res = client.post(f"/api/initiatives/{initiative['id']}/sign",
                          json={"user_id": user["id"]})
        assert res.status_code == 200
        sig = res.json()["signature"]
        assert sig["status"] == "VALIDA"
        assert "doc_hash" in sig
        assert "timestamp" in sig
        assert len(sig["doc_hash"]) == 64  # SHA-256

    def test_firma_duplicada_rechazada(self):
        """DuplicateCheckDecorator impide que el mismo ciudadano firme dos veces."""
        user = register_verified_user()
        initiative = create_active_initiative(user["id"])
        client.post(f"/api/initiatives/{initiative['id']}/sign",
                    json={"user_id": user["id"]})
        res = client.post(f"/api/initiatives/{initiative['id']}/sign",
                          json={"user_id": user["id"]})
        assert res.status_code == 400
        assert "ya firmo" in res.json()["detail"]

    def test_ciudadano_no_verificado_no_puede_firmar(self):
        """La cadena de decoradores rechaza antes si el ciudadano no esta verificado."""
        author = register_verified_user()
        initiative = create_active_initiative(author["id"])
        no_verificado = register_user("Juan", "juan@test.com")
        res = client.post(f"/api/initiatives/{initiative['id']}/sign",
                          json={"user_id": no_verificado["id"]})
        assert res.status_code == 400
        assert "verificado" in res.json()["detail"]

    def test_firma_sobre_iniciativa_no_activa_rechazada(self):
        """El Decorator no se alcanza si la iniciativa no esta en estado ACTIVA."""
        user = register_verified_user()
        res = client.post("/api/initiatives", json={
            "title": "Ley borrador", "content": "Art. 1.", "author_id": user["id"]
        })
        borrador = res.json()
        sign = client.post(f"/api/initiatives/{borrador['id']}/sign",
                           json={"user_id": user["id"]})
        assert sign.status_code == 400
        assert "activa" in sign.json()["detail"].lower()


# =============================================================================
# CP-04 — Composite: CommentBranch / CommentLeaf
# =============================================================================

class TestCompositeComments:

    def test_comentario_raiz_es_branch(self):
        """Un comentario raiz se crea como CommentBranch (can_reply=True)."""
        user = register_verified_user()
        initiative = create_active_initiative(user["id"])
        res = client.post(f"/api/initiatives/{initiative['id']}/comments", json={
            "text": "Apoyo esta iniciativa", "author_id": user["id"]
        })
        assert res.status_code == 200
        data = res.json()
        assert data["level"] == 1
        assert data["can_reply"] is True
        assert data["parent_id"] is None

    def test_respuesta_nivel_2(self):
        """Una respuesta a nivel 1 genera un nodo de nivel 2."""
        user = register_verified_user()
        initiative = create_active_initiative(user["id"])
        l1 = client.post(f"/api/initiatives/{initiative['id']}/comments", json={
            "text": "Comentario raiz", "author_id": user["id"]
        }).json()
        res = client.post(f"/api/initiatives/{initiative['id']}/comments", json={
            "text": "Respuesta nivel 2", "author_id": user["id"], "parent_id": l1["id"]
        })
        assert res.status_code == 200
        assert res.json()["level"] == 2

    def test_nivel_maximo_es_leaf(self):
        """El nodo de nivel 3 se crea como CommentLeaf (can_reply=False)."""
        user = register_verified_user()
        initiative = create_active_initiative(user["id"])
        l1 = client.post(f"/api/initiatives/{initiative['id']}/comments", json={
            "text": "Nivel 1", "author_id": user["id"]
        }).json()
        l2 = client.post(f"/api/initiatives/{initiative['id']}/comments", json={
            "text": "Nivel 2", "author_id": user["id"], "parent_id": l1["id"]
        }).json()
        l3 = client.post(f"/api/initiatives/{initiative['id']}/comments", json={
            "text": "Nivel 3", "author_id": user["id"], "parent_id": l2["id"]
        }).json()
        assert l3["level"] == 3
        assert l3["can_reply"] is False

    def test_nivel_4_bloqueado(self):
        """El Composite rechaza comentarios mas alla de la profundidad maxima (3)."""
        user = register_verified_user()
        initiative = create_active_initiative(user["id"])
        l1 = client.post(f"/api/initiatives/{initiative['id']}/comments", json={
            "text": "N1", "author_id": user["id"]
        }).json()
        l2 = client.post(f"/api/initiatives/{initiative['id']}/comments", json={
            "text": "N2", "author_id": user["id"], "parent_id": l1["id"]
        }).json()
        l3 = client.post(f"/api/initiatives/{initiative['id']}/comments", json={
            "text": "N3", "author_id": user["id"], "parent_id": l2["id"]
        }).json()
        res = client.post(f"/api/initiatives/{initiative['id']}/comments", json={
            "text": "N4 bloqueado", "author_id": user["id"], "parent_id": l3["id"]
        })
        assert res.status_code == 400
        assert "profundidad" in res.json()["detail"].lower()

    def test_arbol_se_construye_correctamente(self):
        """GET /comments devuelve los nodos hijos anidados bajo el padre."""
        user = register_verified_user()
        initiative = create_active_initiative(user["id"])
        l1 = client.post(f"/api/initiatives/{initiative['id']}/comments", json={
            "text": "Raiz", "author_id": user["id"]
        }).json()
        client.post(f"/api/initiatives/{initiative['id']}/comments", json={
            "text": "Hijo", "author_id": user["id"], "parent_id": l1["id"]
        })
        tree = client.get(f"/api/initiatives/{initiative['id']}/comments").json()
        roots = tree["comments"]
        assert len(roots) == 1
        assert len(roots[0]["children"]) == 1


# =============================================================================
# CP-05 — Proxy: CryptographicSealProxy
# =============================================================================

class TestProxyCryptographicSeal:

    def test_sellado_genera_hash_sha512(self):
        """El Proxy genera un hash SHA-512 de 128 caracteres hexadecimales."""
        user = register_verified_user()
        initiative = create_active_initiative(user["id"])
        res = client.post(f"/api/initiatives/{initiative['id']}/seal")
        assert res.status_code == 200
        detail = client.get(f"/api/initiatives/{initiative['id']}").json()
        assert detail["sealed"] is True
        assert detail["seal_hash"] is not None
        assert len(detail["seal_hash"]) == 128  # SHA-512 hex

    def test_expediente_pasa_a_enviada_con_radicacion(self):
        """Tras el sello el CongressApiAdapter asigna numero de radicacion."""
        user = register_verified_user()
        initiative = create_active_initiative(user["id"])
        client.post(f"/api/initiatives/{initiative['id']}/seal")
        detail = client.get(f"/api/initiatives/{initiative['id']}").json()
        assert detail["status"] == "ENVIADA"
        assert detail["radicacion"].startswith("RAD-")

    def test_firma_post_sello_bloqueada(self):
        """El Proxy deniega escrituras sobre un expediente ya sellado."""
        user = register_verified_user()
        initiative = create_active_initiative(user["id"])
        client.post(f"/api/initiatives/{initiative['id']}/seal")
        segundo = register_verified_user("Luis", "luis@test.com")
        res = client.post(f"/api/initiatives/{initiative['id']}/sign",
                          json={"user_id": segundo["id"]})
        assert res.status_code == 400

    def test_doble_sellado_rechazado(self):
        """El Proxy detecta que el expediente ya fue sellado y lo rechaza."""
        user = register_verified_user()
        initiative = create_active_initiative(user["id"])
        client.post(f"/api/initiatives/{initiative['id']}/seal")
        res = client.post(f"/api/initiatives/{initiative['id']}/seal")
        assert res.status_code == 400
        assert "sellado" in res.json()["detail"].lower()

    def test_auditoria_registra_seal_and_send(self):
        """El log de auditoria incluye la accion SEAL_AND_SEND tras el sello."""
        user = register_verified_user()
        initiative = create_active_initiative(user["id"])
        client.post(f"/api/initiatives/{initiative['id']}/seal")
        log = client.get("/api/initiatives/audit/log").json()
        acciones = [e["action"] for e in log]
        assert "SEAL_AND_SEND" in acciones
