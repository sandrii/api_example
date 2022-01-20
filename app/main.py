from http.client import HTTP_PORT
from statistics import mode
from fastapi import FastAPI, status, HTTPException, Response, Depends
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from typing import List
from sqlalchemy.orm import Session
from . import models, schemas
from .database import get_db, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/healthcheck/")
def healthcheck():
    return {"status": "OK"}


@app.get("/posts", response_model=List[schemas.Post])
def test_post(db: Session = Depends(get_db)):
    return db.query(models.Post).all()


@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@app.get("/posts/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail=f"Post {post_id} does not exist")
    return post


@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id)
    if not post.first():
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail=f"Post {post_id} does not exist")
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{post_id}", response_model=schemas.Post)
def update_post(post_id: int, post: schemas.PostCreate, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == post_id)
    if not post_query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with {post_id} does not exist")
    post_query.update(post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()
