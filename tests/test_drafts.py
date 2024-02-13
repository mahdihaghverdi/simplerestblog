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
