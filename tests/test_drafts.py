from src.core.config import settings


def test_create_draft(client, create_admin, admin_auth_headers):
    response = client.post(
        f"{settings.PREFIX}/drafts",
        json={"title": "title", "body": "body"},
        headers=admin_auth_headers,
    )
    assert response.status_code == 201, response.text

    data = response.json()
    assert data["title"] == "title"
    assert data["body"] == "body"
    assert data["username"] == "admin"


def test_get_one_draft(client, create_mahdi, mahdi_auth_headers):
    draft_id = client.post(
        f"{settings.PREFIX}/drafts",
        json={"title": "title", "body": "body"},
        headers=mahdi_auth_headers,
    ).json()["id"]

    response = client.get(
        f"{settings.PREFIX}/drafts/{draft_id}",
        headers=mahdi_auth_headers,
    )
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["title"] == "title"
    assert data["body"] == "body"
    assert data["username"] == "mahdi"
