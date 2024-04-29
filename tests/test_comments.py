from src.core.config import settings
from src.core.enums import APIPrefixesEnum
from tests.conftest import (
    create_post,
    create_draft,
    comments_basic_url,
    BaseTest,
    create_comment,
)

bt = BaseTest()


def test_add_comment(client, refreshed_mahdi):
    headers, cookies = bt.headers_cookies_tuple(refreshed_mahdi)
    post_id = create_post(
        client, headers, cookies, create_draft(client, headers, cookies)
    )

    response = client.post(
        f"{comments_basic_url}/{post_id}",
        headers=headers,
        cookies=cookies,
        json={"comment": "comment"},
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


def test_add_comment_post_not_found(client, refreshed_mahdi):
    h, c = bt.headers_cookies_tuple(refreshed_mahdi)

    response = client.post(
        f"{settings.PREFIX}/{APIPrefixesEnum.COMMENTS.value}/100",
        json={"comment": "comment"},
        headers=h,
        cookies=c,
    )

    assert response.status_code == 404, response.text


def test_add_reply(client, refreshed_mahdi):
    h, c = bt.headers_cookies_tuple(refreshed_mahdi)
    post_id = create_post(client, h, c, create_draft(client, h, c))
    comment_id = create_comment(client, h, c, post_id)

    response = client.post(
        f"{settings.PREFIX}/{APIPrefixesEnum.COMMENTS.value}/{post_id}/{comment_id}",
        json={"comment": "reply"},
        headers=h,
        cookies=c,
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


def test_add_reply_comment_not_found(client, refreshed_mahdi):
    h, c = bt.headers_cookies_tuple(refreshed_mahdi)
    post_id = create_post(client, h, c, create_draft(client, h, c))

    response = client.post(
        f"{settings.PREFIX}/{APIPrefixesEnum.COMMENTS.value}/{post_id}/100",
        json={"comment": "reply"},
        headers=h,
        cookies=c,
    )

    assert response.status_code == 404, response.text


def test_get_comments(client, refreshed_mahdi):
    h, c = bt.headers_cookies_tuple(refreshed_mahdi)
    post_id = create_post(client, h, c, create_draft(client, h, c))
    c1_id = create_comment(client, h, c, post_id, "comment1")
    c2_id = create_comment(client, h, c, post_id, "comment2")
    _ = create_comment(client, h, c, post_id, "comment3")

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
        headers=h,
        cookies=c,
    )
    client.post(
        f"{settings.PREFIX}/{APIPrefixesEnum.COMMENTS.value}/{post_id}/{c1_id}",
        json={"comment": "rep2"},
        headers=h,
        cookies=c,
    )

    # add 1 rep to 2nd
    client.post(
        f"{settings.PREFIX}/{APIPrefixesEnum.COMMENTS.value}/{post_id}/{c2_id}",
        json={"comment": "rep1"},
        headers=h,
        cookies=c,
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


def test_get_replies(client, refreshed_mahdi):
    h, c = bt.headers_cookies_tuple(refreshed_mahdi)
    post_id = create_post(client, h, c, create_draft(client, h, c))
    comment_id = create_comment(client, h, c, post_id)

    client.post(
        f"{settings.PREFIX}/{APIPrefixesEnum.COMMENTS.value}/{post_id}/{comment_id}",
        json={"comment": "reply1"},
        headers=h,
        cookies=c,
    )
    client.post(
        f"{settings.PREFIX}/{APIPrefixesEnum.COMMENTS.value}/{post_id}/{comment_id}",
        json={"comment": "reply2"},
        headers=h,
        cookies=c,
    )
    client.post(
        f"{settings.PREFIX}/{APIPrefixesEnum.COMMENTS.value}/{post_id}/{comment_id}",
        json={"comment": "reply3"},
        headers=h,
        cookies=c,
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


def test_update_comment(client, refreshed_mahdi):
    h, c = bt.headers_cookies_tuple(refreshed_mahdi)
    post_id = create_post(client, h, c, create_draft(client, h, c))
    comment_id = create_comment(client, h, c, post_id)

    response = client.put(
        f"{settings.PREFIX}/{APIPrefixesEnum.COMMENTS.value}/{post_id}/{comment_id}",
        json={"comment": "updated comment"},
        headers=h,
        cookies=c,
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
