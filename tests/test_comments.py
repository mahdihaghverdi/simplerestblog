from src.core.config import settings
from src.core.enums import APIPrefixesEnum


def test_add_comment(client, mahdi_auth_headers, post_id):
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


def test_add_reply(client, mahdi_auth_headers, post_id):
    comment_id = client.post(
        f"{settings.PREFIX}/{APIPrefixesEnum.COMMENTS.value}/{post_id}",
        json={"comment": "comment"},
        headers=mahdi_auth_headers,
    ).json()["id"]

    response = client.post(
        f"{settings.PREFIX}/{APIPrefixesEnum.COMMENTS.value}/{post_id}/{comment_id}",
        json={"comment": "reply"},
        headers=mahdi_auth_headers,
    )

    assert response.status_code == 201, response.text

    data = response.json()
    assert data["commented"]
    assert data["comment"] == "reply"
    assert data["path"] == f'{comment_id}.{data["id"]}'
    assert data["updated"] is None
    assert data["parent_id"] == comment_id
    assert data["username"] == "mahdi"
    assert data["reply_count"] == 0
