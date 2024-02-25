from src.core.config import settings
from src.core.enums import APIPrefixesEnum


def test_get_posts(client, mahdi_auth_headers):
    draft_id = client.post(
        f"{settings.PREFIX}/{APIPrefixesEnum.DRAFTS.value}/",
        json={"title": "title", "body": "body"},
        headers=mahdi_auth_headers,
    ).json()["id"]

    draft_id2 = client.post(
        f"{settings.PREFIX}/{APIPrefixesEnum.DRAFTS.value}/",
        json={"title": "title2", "body": "body"},
        headers=mahdi_auth_headers,
    ).json()["id"]

    client.post(
        f"{settings.PREFIX}/{APIPrefixesEnum.DRAFTS.value}/publish/{draft_id}",
        json={"tags": ["tag1", "tag2"], "slug": "slug"},
        headers=mahdi_auth_headers,
    )

    client.post(
        f"{settings.PREFIX}/{APIPrefixesEnum.DRAFTS.value}/publish/{draft_id2}",
        json={"tags": ["tag1", "tag2"], "slug": "slug"},
        headers=mahdi_auth_headers,
    )

    response = client.get(f"{settings.PREFIX}/{APIPrefixesEnum.POSTS.value}/mahdi")
    assert response.status_code == 200, response.text

    data = response.json()
    assert len(data) == 2

    data1, data2 = data
    assert data1["title"] == "title"
    assert data1["slug"]
    assert data1["published"]
    assert data2["title"] == "title2"
    assert data1["published"] != data2["published"]

    response = client.get(f"/@mahdi/{data1['slug']}")
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["title"] == "title"
    assert data["body"] == "body"
    assert set(data["tags"]) == {"tag1", "tag2"}
    assert not data["comments_count"]
