from fastapi import FastAPI
from app.routes import post, user, auth, vote
from app import models, database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)


@app.get("/healthcheck/")
def healthcheck():
    return {"status": "OK"}
