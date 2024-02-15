from src.core.config import settings
from src.core.enums import APIPrefixesEnum


def test_create_draft(client, admin_auth_headers):
    response = client.post(
        f"{settings.PREFIX}/drafts/create",
        json={"title": "title", "body": "body"},
        headers=admin_auth_headers,
    )
    assert response.status_code == 201, response.text

    data = response.json()
    assert data["title"] == "title"
    assert data["body"] == "body"
    assert data["username"] == "admin"


def test_get_one_draft(client, mahdi_auth_headers):
    draft_id = client.post(
        f"{settings.PREFIX}/drafts/create",
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


def test_get_all_drafts(client, mahdi_auth_headers):
    def _():
        return client.post(
            f"{settings.PREFIX}/drafts/create",
            json={"title": "title", "body": "body"},
            headers=mahdi_auth_headers,
        ).json()["id"]

    ids = [_(), _()]
    response = client.get(
        f"{settings.PREFIX}/drafts/all",
        headers=mahdi_auth_headers,
    )
    assert response.status_code == 200, response.text

    data = response.json()
    for draft, id_ in zip(data, reversed(ids)):
        assert draft["title"] == "title"
        assert draft["updated"] is None
        assert draft["link"] == [
            "GET",
            f"{settings.PREFIX}/{APIPrefixesEnum.DRAFTS.value}/{id_}",
        ]


def test_update_draft(client, mahdi_auth_headers):
    draft_id = client.post(
        f"{settings.PREFIX}/{APIPrefixesEnum.DRAFTS.value}/create",
        json={"title": "title", "body": "body"},
        headers=mahdi_auth_headers,
    ).json()["id"]

    response = client.put(
        f"{settings.PREFIX}/{APIPrefixesEnum.DRAFTS.value}/{draft_id}",
        json={"title": "updated title", "body": "updated body"},
        headers=mahdi_auth_headers,
    )
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["title"] == "updated title"
    assert data["body"] == "updated body"
    assert data["updated"] is not None


def test_update_draft_not_found(client, mahdi_auth_headers):
    response = client.put(
        f"{settings.PREFIX}/{APIPrefixesEnum.DRAFTS.value}/1",
        json={"title": "updated title", "body": "updated body"},
        headers=mahdi_auth_headers,
    )
    assert response.status_code == 404, response.text
