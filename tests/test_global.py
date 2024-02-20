def test_get_global_post_not_found(client, create_mahdi):
    link = "/@mahdi/123456789"

    response = client.get(link)
    assert response.status_code == 404, response.text
