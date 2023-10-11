import json
from util import *


@responses.activate
def test_list_applications(client, dummy_data):
    stub(
        responses.GET,
        "https://api.nexmo.com/v2/applications",
        fixture_path="application/list_applications.json",
    )

    apps = client.application.list_applications()
    assert_basic_auth()
    assert isinstance(apps, dict)
    assert apps["total_items"] == 30
    assert request_user_agent() == dummy_data.user_agent


@responses.activate
def test_get_application(client, dummy_data):
    stub(
        responses.GET,
        "https://api.nexmo.com/v2/applications/xx-xx-xx-xx",
        fixture_path="application/get_application.json",
    )

    app = client.application.get_application("xx-xx-xx-xx")
    assert_basic_auth()
    assert isinstance(app, dict)
    assert app["name"] == "My Test Application"
    assert request_user_agent() == dummy_data.user_agent


@responses.activate
def test_create_application(client, dummy_data):
    stub(
        responses.POST,
        "https://api.nexmo.com/v2/applications",
        fixture_path="application/create_application.json",
    )

    params = {"name": "Example App", "type": "voice"}

    app = client.application.create_application(params)
    assert_basic_auth()
    assert isinstance(app, dict)
    assert app["name"] == "My Test Application"
    assert request_user_agent() == dummy_data.user_agent
    body_data = json.loads(request_body().decode("utf-8"))
    assert body_data["type"] == "voice"


@responses.activate
def test_update_application(client, dummy_data):
    stub(
        responses.PUT,
        "https://api.nexmo.com/v2/applications/xx-xx-xx-xx",
        fixture_path="application/update_application.json",
    )

    params = {"answer_url": "https://example.com/ncco"}

    app = client.application.update_application("xx-xx-xx-xx", params)
    assert_basic_auth()
    assert isinstance(app, dict)
    assert request_user_agent() == dummy_data.user_agent
    assert request_content_type() == "application/json"
    assert b'"answer_url": "https://example.com/ncco"' in request_body()

    assert app["name"] == "A Better Name"


@responses.activate
def test_delete_application(client, dummy_data):
    responses.add(
        responses.DELETE,
        "https://api.nexmo.com/v2/applications/xx-xx-xx-xx",
        status=204,
    )

    assert client.application.delete_application("xx-xx-xx-xx") is None
    assert_basic_auth()
    assert request_user_agent() == dummy_data.user_agent
