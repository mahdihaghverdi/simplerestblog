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


def test_add_reply(client, mahdi_auth_headers, post_id, comment_id):
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


def test_get_comments(client, mahdi_auth_headers, post_id):
    c1_id = client.post(
        f"{settings.PREFIX}/{APIPrefixesEnum.COMMENTS.value}/{post_id}",
        json={"comment": "comment1"},
        headers=mahdi_auth_headers,
    ).json()["id"]

    c2_id = client.post(
        f"{settings.PREFIX}/{APIPrefixesEnum.COMMENTS.value}/{post_id}",
        json={"comment": "comment2"},
        headers=mahdi_auth_headers,
    ).json()["id"]

    _ = client.post(
        f"{settings.PREFIX}/{APIPrefixesEnum.COMMENTS.value}/{post_id}",
        json={"comment": "comment3"},
        headers=mahdi_auth_headers,
    ).json()["id"]

    response = client.get(
        f"{settings.PREFIX}/{APIPrefixesEnum.COMMENTS.value}/{post_id}",
        params={"order": "first"},
    )
    assert response.status_code == 200, response.text

    data = response.json()
    assert len(data) == 3

    for idx, cmt in enumerate(data, 1):
        assert cmt["comment"] == f"comment{idx}"

    response = client.get(
        f"{settings.PREFIX}/{APIPrefixesEnum.COMMENTS.value}/{post_id}",
        params={"order": "last"},
    )
    assert response.status_code == 200, response.text

    data = response.json()
    assert len(data) == 3

    for idx, cmt in enumerate(reversed(data), 1):
        assert cmt["comment"] == f"comment{idx}"

    # add 2 rep to 1st
    client.post(
        f"{settings.PREFIX}/{APIPrefixesEnum.COMMENTS.value}/{post_id}/{c1_id}",
        json={"comment": "rep1"},
        headers=mahdi_auth_headers,
    )
    client.post(
        f"{settings.PREFIX}/{APIPrefixesEnum.COMMENTS.value}/{post_id}/{c1_id}",
        json={"comment": "rep2"},
        headers=mahdi_auth_headers,
    )

    # add 1 rep to 2nd
    client.post(
        f"{settings.PREFIX}/{APIPrefixesEnum.COMMENTS.value}/{post_id}/{c2_id}",
        json={"comment": "rep1"},
        headers=mahdi_auth_headers,
    )

    response = client.get(
        f"{settings.PREFIX}/{APIPrefixesEnum.COMMENTS.value}/{post_id}",
        params={"order": "most_replied"},
    )
    assert response.status_code == 200, response.text

    data = response.json()
    assert len(data) == 3

    for idx, cmt in enumerate(data, 1):
        assert cmt["comment"] == f"comment{idx}"


def test_get_replies(client, mahdi_auth_headers, post_id, comment_id):
    client.post(
        f"{settings.PREFIX}/{APIPrefixesEnum.COMMENTS.value}/{post_id}/{comment_id}",
        json={"comment": "reply1"},
        headers=mahdi_auth_headers,
    )
    client.post(
        f"{settings.PREFIX}/{APIPrefixesEnum.COMMENTS.value}/{post_id}/{comment_id}",
        json={"comment": "reply2"},
        headers=mahdi_auth_headers,
    )
    client.post(
        f"{settings.PREFIX}/{APIPrefixesEnum.COMMENTS.value}/{post_id}/{comment_id}",
        json={"comment": "reply3"},
        headers=mahdi_auth_headers,
    )

    response = client.get(
        f"{settings.PREFIX}/{APIPrefixesEnum.COMMENTS.value}/{post_id}/{comment_id}",
        params={"order": "first"},
    )
    assert response.status_code == 200, response.text

    data = response.json()
    assert len(data) == 3

    for idx, cmt in enumerate(data, 1):
        assert cmt["comment"] == f"reply{idx}"

    response = client.get(
        f"{settings.PREFIX}/{APIPrefixesEnum.COMMENTS.value}/{post_id}/{comment_id}",
        params={"order": "last"},
    )
    assert response.status_code == 200, response.text

    data = response.json()
    assert len(data) == 3

    for idx, cmt in enumerate(reversed(data), 1):
        assert cmt["comment"] == f"reply{idx}"


def test_update_comment(client, mahdi_auth_headers, post_id, comment_id):
    response = client.put(
        f"{settings.PREFIX}/{APIPrefixesEnum.COMMENTS.value}/{post_id}/{comment_id}",
        json={"comment": "updated comment"},
        headers=mahdi_auth_headers,
    )
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["commented"]
    assert data["comment"] == "updated comment"
    assert data["path"] == str(data["id"])
    assert data["updated"] is not None
    assert data["parent_id"] is None
    assert data["username"] == "mahdi"
    assert data["reply_count"] == 0
