from fastapi.testclient import TestClient
from fastapi_example.main import app
from fastapi_example import schemas
from fastapi_example.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
 

client = TestClient(app)
engine = create_engine(f"postgresql://{settings.db_username}:"
                       f"{settings.db_password}@{settings.db_address}:"
                       f"{settings.db_port}/{settings.db_name}")
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_root():
    assert client.get("/healthcheck/").status_code == 200


def test_create_user():
    response = client.post("/users/",
                           json={"email": "andreysh@gmail.com",
                                 "password": "my_test_password"})
    new_user = schemas.UserOut(**response.json())
    assert new_user.email == "andreysh@gmail.com"
    assert response.status_code == 201
