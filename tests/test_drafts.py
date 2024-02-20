from src.core.config import settings
from src.core.enums import APIPrefixesEnum

drafts_url = f"{settings.PREFIX}/{APIPrefixesEnum.DRAFTS.value}"


def test_create_draft(client, admin_auth_headers):
    response = client.post(
        f"{drafts_url}/create",
        json={"title": "title", "body": "body"},
        headers=admin_auth_headers,
    )
    assert response.status_code == 201, response.text

    data = response.json()
    assert data["title"] == "title"
    assert data["body"] == "body"
    assert data["username"] == "admin"


def test_get_all_drafts(client, mahdi_auth_headers):
    def _():
        return client.post(
            f"{drafts_url}/create",
            json={"title": "title", "body": "body"},
            headers=mahdi_auth_headers,
        ).json()["id"]

    ids = [_(), _()]
    response = client.get(
        f"{drafts_url}/all",
        headers=mahdi_auth_headers,
    )
    assert response.status_code == 200, response.text

    data = response.json()
    for draft, id_ in zip(data, reversed(ids)):
        assert draft["title"] == "title"
        assert draft["updated"] is None
        assert draft["link"] == [
            "GET",
            f"{drafts_url}/{id_}",
        ]


def test_get_one_draft(client, mahdi_auth_headers):
    draft_id = client.post(
        f"{drafts_url}/create",
        json={"title": "title", "body": "body"},
        headers=mahdi_auth_headers,
    ).json()["id"]

    response = client.get(
        f"{drafts_url}/{draft_id}",
        headers=mahdi_auth_headers,
    )
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["title"] == "title"
    assert data["body"] == "body"
    assert data["username"] == "mahdi"


def test_update_draft(client, mahdi_auth_headers):
    draft_id = client.post(
        f"{drafts_url}/create",
        json={"title": "title", "body": "body"},
        headers=mahdi_auth_headers,
    ).json()["id"]

    response = client.put(
        f"{drafts_url}/{draft_id}",
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
        f"{drafts_url}/1",
        json={"title": "updated title", "body": "updated body"},
        headers=mahdi_auth_headers,
    )
    assert response.status_code == 404, response.text


def test_delete_draft(client, mahdi_auth_headers):
    draft_id = client.post(
        f"{drafts_url}/create",
        json={"title": "title", "body": "body"},
        headers=mahdi_auth_headers,
    ).json()["id"]

    response = client.delete(
        f"{drafts_url}/{draft_id}",
        headers=mahdi_auth_headers,
    )
    assert response.status_code == 204, response.text


def test_delete_draft_not_found(client, mahdi_auth_headers):
    response = client.delete(
        f"{drafts_url}/1",
        headers=mahdi_auth_headers,
    )
    assert response.status_code == 404, response.text


def test_open_read(client, mahdi_auth_headers):
    draft_hash = client.post(
        f"{drafts_url}/create",
        json={"title": "title", "body": "body"},
        headers=mahdi_auth_headers,
    ).json()["draft_hash"]

    response = client.get(draft_hash)
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["title"] == "title"
    assert data["body"] == "body"
    assert data["username"] == "mahdi"


def test_publish_post(client, mahdi_auth_headers):
    draft_id = client.post(
        f"{drafts_url}/create",
        json={"title": "title", "body": "body"},
        headers=mahdi_auth_headers,
    ).json()["id"]

    response = client.post(
        f"{drafts_url}/publish/{draft_id}",
        json={"tags": ["tag1", "tag2"], "slug": "my slug"},
        headers=mahdi_auth_headers,
    )
    assert response.status_code == 200, response.text

    data = response.json()
    title, body, tags, published, updated = (
        data["title"],
        data["body"],
        data["tags"],
        data["published"],
        data["updated"],
    )
    assert title == "title"
    assert body == "body"
    assert set(tags) == {"tag1", "tag2"}
    assert published
    assert not updated


def test_draft_published_before(client, mahdi_auth_headers):
    draft_id = client.post(
        f"{drafts_url}/create",
        json={"title": "title", "body": "body"},
        headers=mahdi_auth_headers,
    ).json()["id"]
    client.post(
        f"{drafts_url}/publish/{draft_id}",
        json={"tags": ["tag1", "tag2"], "slug": "my slug"},
        headers=mahdi_auth_headers,
    )
    response = client.post(
        f"{drafts_url}/publish/{draft_id}",
        json={"tags": ["tag1", "tag2"], "slug": "my slug"},
        headers=mahdi_auth_headers,
    )
    assert response.status_code == 400, response.text


def test_publish_but_draft_not_found(client, mahdi_auth_headers):
    response = client.post(
        f"{drafts_url}/publish/1",
        json={"tags": ["tag1", "tag2"], "slug": "my slug"},
        headers=mahdi_auth_headers,
    )
    assert response.status_code == 404, response.text
