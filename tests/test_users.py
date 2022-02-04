from fastapi.testclient import TestClient
from fastapi_example.main import app
from fastapi_example import schemas

client = TestClient(app)


def test_root():
    assert client.get("/healthcheck/").status_code == 200


def test_create_user():
    response = client.post("/users/",
                           json={"email": "andreysh@gmail.com",
                                 "password": "my_test_password"})
    new_user = schemas.UserOut(**response.json())
    assert new_user.email == "andreysh@gmail.com"
    assert response.status_code == 201
