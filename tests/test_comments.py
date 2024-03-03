from src.core.config import settings
from src.core.enums import APIPrefixesEnum


def test_add_comment(client, mahdi_auth_headers):
    draft_id = client.post(
        f"{settings.PREFIX}/{APIPrefixesEnum.DRAFTS.value}",
        json={"title": "title", "body": "body"},
        headers=mahdi_auth_headers,
    ).json()["id"]

    post_id = client.post(
        f"{settings.PREFIX}/{APIPrefixesEnum.DRAFTS.value}/publish/{draft_id}",
        json={"tags": ["tag1", "tag2"], "slug": "slug"},
        headers=mahdi_auth_headers,
    ).json()["id"]

    response = client.post(
        f"{settings.PREFIX}/{APIPrefixesEnum.COMMENTS.value}/{post_id}",
        json={"comment": "comment"},
        headers=mahdi_auth_headers,
    )

    assert response.status_code == 201, response.text

    data = response.json()
    assert data["commented"]
    assert data["comment"] == "comment"
    assert data["path"] == str(data["id"])
    assert data["updated"] is None
    assert data["parent_id"] is None
    assert data["username"] == "mahdi"
    assert data["reply_count"] == 0
