from src.core.config import settings
from src.core.enums import APIPrefixesEnum
from tests.conftest import BaseTest, create_draft, create_post, posts_basic_url

bt = BaseTest()


def test_get_self_posts(client, refreshed_mahdi):
    h, c = bt.headers_cookies_tuple(refreshed_mahdi)

    draft_id = create_draft(client, h, c)
    draft_id2 = create_draft(client, h, c, "title2")
    create_post(client, h, c, draft_id)
    create_post(client, h, c, draft_id2)

    response = client.get(
        f"{settings.PREFIX}/{APIPrefixesEnum.POSTS.value}/", headers=h, cookies=c
    )
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


def test_get_posts_with_username(client, refreshed_mahdi):
    h, c = bt.headers_cookies_tuple(refreshed_mahdi)

    draft_id = create_draft(client, h, c)
    draft_id2 = create_draft(client, h, c, "title2")
    create_post(client, h, c, draft_id)
    create_post(client, h, c, draft_id2)

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


def test_unpublish_post(client, refreshed_mahdi):
    h, c = bt.headers_cookies_tuple(refreshed_mahdi)
    draft_id = create_draft(client, h, c)
    post_id = create_post(client, h, c, draft_id)

    response = client.post(f"{posts_basic_url}/unpublish/{post_id}", cookies=c, headers=h)
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["title"] == "title"
    assert data["body"] == "body"
    assert data["username"] == "mahdi"

    response = client.get(f"{posts_basic_url}", headers=h, cookies=c)
    assert not response.json()
