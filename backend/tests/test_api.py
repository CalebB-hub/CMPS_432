"""Tests for auth, files, and tags API endpoints."""
import io
import json


# ── Helpers ──────────────────────────────────────────────────────────────────

def _register(client, username="alice", email="alice@example.com", password="secret123"):
    return client.post(
        "/api/auth/register",
        json={"username": username, "email": email, "password": password},
    )


def _token(client, username="alice", password="secret123"):
    r = client.post(
        "/api/auth/token",
        data={"username": username, "password": password},
    )
    return r.json()["access_token"]


def _auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


# ── Auth tests ────────────────────────────────────────────────────────────────

def test_register(client):
    r = _register(client)
    assert r.status_code == 201
    data = r.json()
    assert data["username"] == "alice"
    assert data["email"] == "alice@example.com"


def test_register_duplicate_username(client):
    r = _register(client, username="alice2", email="alice2@example.com")
    assert r.status_code == 201
    r2 = _register(client, username="alice2", email="other@example.com")
    assert r2.status_code == 400


def test_login(client):
    _register(client, username="bob", email="bob@example.com", password="pass")
    r = client.post("/api/auth/token", data={"username": "bob", "password": "pass"})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_login_bad_password(client):
    _register(client, username="carol", email="carol@example.com", password="correct")
    r = client.post("/api/auth/token", data={"username": "carol", "password": "wrong"})
    assert r.status_code == 401


def test_get_me(client):
    _register(client, username="dave", email="dave@example.com")
    tok = _token(client, username="dave")
    r = client.get("/api/auth/me", headers=_auth_headers(tok))
    assert r.status_code == 200
    assert r.json()["username"] == "dave"


# ── File tests ────────────────────────────────────────────────────────────────

def test_upload_and_list_file(client, tmp_path):
    _register(client, username="erin", email="erin@example.com")
    tok = _token(client, username="erin")
    headers = _auth_headers(tok)

    file_content = b"hello world"
    r = client.post(
        "/api/files/",
        files={"file": ("hello.txt", io.BytesIO(file_content), "text/plain")},
        data={"tags": "docs,work"},
        headers=headers,
    )
    assert r.status_code == 201
    data = r.json()
    assert data["original_filename"] == "hello.txt"
    assert data["size"] == len(file_content)
    tag_names = {t["name"] for t in data["tags"]}
    assert "docs" in tag_names
    assert "work" in tag_names

    r2 = client.get("/api/files/", headers=headers)
    assert r2.status_code == 200
    assert len(r2.json()) >= 1


def test_filter_files_by_tag(client, tmp_path):
    _register(client, username="frank", email="frank@example.com")
    tok = _token(client, username="frank")
    headers = _auth_headers(tok)

    for name, tag in [("a.txt", "alpha"), ("b.txt", "beta")]:
        client.post(
            "/api/files/",
            files={"file": (name, io.BytesIO(b"data"), "text/plain")},
            data={"tags": tag},
            headers=headers,
        )

    r = client.get("/api/files/?tags=alpha", headers=headers)
    assert r.status_code == 200
    names = [f["original_filename"] for f in r.json()]
    assert "a.txt" in names
    assert "b.txt" not in names


def test_delete_file(client):
    _register(client, username="grace", email="grace@example.com")
    tok = _token(client, username="grace")
    headers = _auth_headers(tok)

    r = client.post(
        "/api/files/",
        files={"file": ("del.txt", io.BytesIO(b"bye"), "text/plain")},
        headers=headers,
    )
    file_id = r.json()["id"]

    r2 = client.delete(f"/api/files/{file_id}", headers=headers)
    assert r2.status_code == 204

    r3 = client.get(f"/api/files/{file_id}", headers=headers)
    assert r3.status_code == 404


# ── Tag tests ─────────────────────────────────────────────────────────────────

def test_create_and_list_tags(client):
    _register(client, username="henry", email="henry@example.com")
    tok = _token(client, username="henry")
    headers = _auth_headers(tok)

    r = client.post("/api/tags/", json={"name": "urgent"}, headers=headers)
    assert r.status_code == 201
    assert r.json()["name"] == "urgent"

    r2 = client.get("/api/tags/", headers=headers)
    assert r2.status_code == 200
    tag_names = [t["name"] for t in r2.json()]
    assert "urgent" in tag_names


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_upload_inherits_parent_tags(client):
    _register(client, username="ivy", email="ivy@example.com")
    tok = _token(client, username="ivy")
    headers = _auth_headers(tok)

    r1 = client.post("/api/tags/", json={"name": "technology"}, headers=headers)
    assert r1.status_code == 201
    parent_id = r1.json()["id"]

    r2 = client.post(
        f"/api/tags/{parent_id}/children",
        json={"name": "phone"},
        headers=headers,
    )
    assert r2.status_code == 201

    r = client.post(
        "/api/files/",
        files={"file": ("phone.txt", io.BytesIO(b"data"), "text/plain")},
        data={"tags": "phone"},
        headers=headers,
    )
    assert r.status_code == 201
    tag_names = {t["name"] for t in r.json()["tags"]}
    assert "phone" in tag_names
    assert "technology" in tag_names


def test_upload_unknown_tag_with_parent_hint(client):
    _register(client, username="jack", email="jack@example.com")
    tok = _token(client, username="jack")
    headers = _auth_headers(tok)

    parent_name = "technology_jack"
    r1 = client.post("/api/tags/", json={"name": parent_name}, headers=headers)
    assert r1.status_code == 201

    r = client.post(
        "/api/files/",
        files={"file": ("watch.txt", io.BytesIO(b"data"), "text/plain")},
        data={
            "tags": "smartwatch",
            "tag_parents": json.dumps({"smartwatch": parent_name}),
        },
        headers=headers,
    )
    assert r.status_code == 201

    tag_names = {t["name"] for t in r.json()["tags"]}
    assert "smartwatch" in tag_names
    assert parent_name in tag_names

    tags = client.get("/api/tags/", headers=headers)
    assert tags.status_code == 200
    by_name = {t["name"]: t for t in tags.json()}
    assert by_name["smartwatch"]["parent_id"] == by_name[parent_name]["id"]


def test_patch_unknown_tag_with_parent_hint_inherits_full_ancestor_chain(client):
    _register(client, username="kyle", email="kyle@example.com")
    tok = _token(client, username="kyle")
    headers = _auth_headers(tok)

    root_name = "technology_kyle"
    child_name = "phone_kyle"

    root = client.post("/api/tags/", json={"name": root_name}, headers=headers)
    assert root.status_code == 201
    technology_id = root.json()["id"]

    phone = client.post(
        f"/api/tags/{technology_id}/children",
        json={"name": child_name},
        headers=headers,
    )
    assert phone.status_code == 201

    created_file = client.post(
        "/api/files/",
        files={"file": ("android.txt", io.BytesIO(b"data"), "text/plain")},
        headers=headers,
    )
    assert created_file.status_code == 201
    file_id = created_file.json()["id"]

    updated = client.patch(
        f"/api/files/{file_id}/tags",
        json={"tags": ["android"], "tag_parents": {"android": child_name}},
        headers=headers,
    )
    assert updated.status_code == 200

    tag_names = {t["name"] for t in updated.json()["tags"]}
    assert "android" in tag_names
    assert child_name in tag_names
    assert root_name in tag_names
