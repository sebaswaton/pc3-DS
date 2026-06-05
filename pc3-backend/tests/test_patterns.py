import pytest
from fastapi.testclient import TestClient
from main import app
from app.database import store

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_store():
    store["users"].clear()
    store["initiatives"].clear()
    store["signatures"].clear()
    store["comments"].clear()
    store["audit_log"].clear()
    yield


def register_user(name="Ana Lopez", email="ana@test.com", dni="12345678", password="pass123"):
    res = client.post("/api/auth/register", json={
        "name": name, "email": email, "dni": dni, "password": password
    })
    assert res.status_code == 200
    return res.json()


def register_verified_user(name="Ana Lopez", email="ana@test.com"):
    return register_user(name, email, dni="12345678")


def register_unverified_user(name="Juan", email="juan@test.com"):
    return register_user(name, email, dni="00000000")


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


class TestAdapterReniec:

    def test_registro_con_dni_valido_verifica_usuario(self):
        user = register_user(dni="12345678")
        assert user["verified"] is True

    def test_registro_con_dni_invalido_no_verifica(self):
        user = register_user(dni="00000000")
        assert user["verified"] is False

    def test_dni_con_formato_incorrecto_rechazado(self):
        res = client.post("/api/auth/register", json={
            "name": "X", "email": "x@x.com", "dni": "1234", "password": "pass123"
        })
        assert res.status_code == 422

    def test_email_duplicado_rechazado(self):
        register_user()
        res = client.post("/api/auth/register", json={
            "name": "Otro", "email": "ana@test.com", "dni": "12345678", "password": "pass123"
        })
        assert res.status_code == 400


class TestLogin:

    def test_login_exitoso(self):
        register_user()
        res = client.post("/api/auth/login", json={"email": "ana@test.com", "password": "pass123"})
        assert res.status_code == 200
        data = res.json()
        assert data["email"] == "ana@test.com"
        assert "password" not in data

    def test_password_incorrecto(self):
        register_user()
        res = client.post("/api/auth/login", json={"email": "ana@test.com", "password": "wrongpass"})
        assert res.status_code == 401

    def test_email_inexistente(self):
        res = client.post("/api/auth/login", json={"email": "noexiste@test.com", "password": "pass123"})
        assert res.status_code == 401


class TestFacadeInitiative:

    def test_publicacion_exitosa(self):
        user = register_verified_user()
        res = client.post("/api/initiatives", json={
            "title": "Ley de agua potable",
            "content": "Art. 1. Acceso universal.",
            "author_id": user["id"]
        })
        initiative = res.json()
        assert initiative["status"] == "BORRADOR"

        pub = client.post(f"/api/initiatives/{initiative['id']}/publish",
                          json={"author_id": user["id"]})
        assert pub.status_code == 200
        data = pub.json()
        assert data["status"] == "ACTIVA"
        assert data["published_at"] is not None
        assert data["deadline"] is not None

    def test_titulo_vacio_rechazado(self):
        user = register_verified_user()
        res = client.post("/api/initiatives", json={
            "title": "", "content": "Contenido.", "author_id": user["id"]
        })
        assert res.status_code == 422

    def test_publicacion_doble_rechazada(self):
        user = register_verified_user()
        initiative = create_active_initiative(user["id"])
        res = client.post(f"/api/initiatives/{initiative['id']}/publish",
                          json={"author_id": user["id"]})
        assert res.status_code == 400
        assert "BORRADOR" in res.json()["detail"]

    def test_autor_incorrecto_no_puede_publicar(self):
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


class TestDecoratorSignature:

    def test_primera_firma_valida_con_metadata(self):
        user = register_verified_user()
        initiative = create_active_initiative(user["id"])
        res = client.post(f"/api/initiatives/{initiative['id']}/sign",
                          json={"user_id": user["id"]})
        assert res.status_code == 200
        sig = res.json()["signature"]
        assert sig["status"] == "VALIDA"
        assert "doc_hash" in sig
        assert "timestamp" in sig
        assert len(sig["doc_hash"]) == 64

    def test_firma_duplicada_rechazada(self):
        user = register_verified_user()
        initiative = create_active_initiative(user["id"])
        client.post(f"/api/initiatives/{initiative['id']}/sign",
                    json={"user_id": user["id"]})
        res = client.post(f"/api/initiatives/{initiative['id']}/sign",
                          json={"user_id": user["id"]})
        assert res.status_code == 400
        assert "ya firmo" in res.json()["detail"]

    def test_ciudadano_no_verificado_no_puede_firmar(self):
        author = register_verified_user()
        initiative = create_active_initiative(author["id"])
        no_verificado = register_unverified_user()
        res = client.post(f"/api/initiatives/{initiative['id']}/sign",
                          json={"user_id": no_verificado["id"]})
        assert res.status_code == 400
        assert "verificado" in res.json()["detail"]

    def test_firma_sobre_iniciativa_no_activa_rechazada(self):
        user = register_verified_user()
        res = client.post("/api/initiatives", json={
            "title": "Ley borrador", "content": "Art. 1.", "author_id": user["id"]
        })
        borrador = res.json()
        sign = client.post(f"/api/initiatives/{borrador['id']}/sign",
                           json={"user_id": user["id"]})
        assert sign.status_code == 400
        assert "activa" in sign.json()["detail"].lower()


class TestCompositeComments:

    def test_comentario_raiz_es_branch(self):
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


class TestProxyCryptographicSeal:

    def test_sellado_genera_hash_sha512(self):
        user = register_verified_user()
        initiative = create_active_initiative(user["id"])
        res = client.post(f"/api/initiatives/{initiative['id']}/seal")
        assert res.status_code == 200
        detail = client.get(f"/api/initiatives/{initiative['id']}").json()
        assert detail["sealed"] is True
        assert detail["seal_hash"] is not None
        assert len(detail["seal_hash"]) == 128

    def test_expediente_pasa_a_enviada_con_radicacion(self):
        user = register_verified_user()
        initiative = create_active_initiative(user["id"])
        client.post(f"/api/initiatives/{initiative['id']}/seal")
        detail = client.get(f"/api/initiatives/{initiative['id']}").json()
        assert detail["status"] == "ENVIADA"
        assert detail["radicacion"].startswith("RAD-")

    def test_firma_post_sello_bloqueada(self):
        user = register_verified_user()
        initiative = create_active_initiative(user["id"])
        client.post(f"/api/initiatives/{initiative['id']}/seal")
        segundo = register_verified_user("Luis", "luis@test.com")
        res = client.post(f"/api/initiatives/{initiative['id']}/sign",
                          json={"user_id": segundo["id"]})
        assert res.status_code == 400

    def test_doble_sellado_rechazado(self):
        user = register_verified_user()
        initiative = create_active_initiative(user["id"])
        client.post(f"/api/initiatives/{initiative['id']}/seal")
        res = client.post(f"/api/initiatives/{initiative['id']}/seal")
        assert res.status_code == 400
        assert "sellado" in res.json()["detail"].lower()

    def test_auditoria_registra_seal_and_send(self):
        user = register_verified_user()
        initiative = create_active_initiative(user["id"])
        client.post(f"/api/initiatives/{initiative['id']}/seal")
        log = client.get("/api/initiatives/audit/log").json()
        acciones = [e["action"] for e in log]
        assert "SEAL_AND_SEND" in acciones
