from fastapi import FastAPI, status, HTTPException, Response
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import time


app = FastAPI()
CONNECTION_ATTEMPTS = 10


def db_connector(**kwargs):
    db_conn, cursor = None, None
    for i in range(kwargs["attempts"]):
        try:
            db_conn = psycopg2.connect(host=kwargs["host"],
                                       database=kwargs["database"],
                                       user=kwargs["user"],
                                       password=kwargs["password"],
                                       cursor_factory=RealDictCursor)
            cursor = db_conn.cursor()
            print("Connected to DB")
            break
        except (psycopg2.Error, psycopg2.OperationalError) as e:
            if i == kwargs["attempts"] - 1:
                raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    detail=f"Failed connecting to DB after {kwargs['attempts']} tries")
            print(f"Got failure: {e}. Connecting to DB...")
            time.sleep(3)
    return db_conn, cursor


CONNECTION, CURSOR = db_connector(host="localhost",
                                  database="fastapi",
                                  user="postgres",
                                  password="database",
                                  attempts=CONNECTION_ATTEMPTS)


class Post(BaseModel):
    title: str
    content: str
    published: bool = True


@app.get("/")
def root():
    return {"data": "Welcome to API example"}


@app.get("/posts")
def get_posts():
    CURSOR.execute("""SELECT * from posts""")
    return {"data": CURSOR.fetchall()}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    CURSOR.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, (post.title, post.content, post.published))
    CONNECTION.commit()
    return {"data": CURSOR.fetchall()}


@app.get("/posts/{post_id}")
def get_post(post_id: int):
    CURSOR.execute("""SELECT * from posts WHERE id = %s """, (str(post_id),))
    post = CURSOR.fetchone()
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail=f"Post {post_id} does not exist")
    return {"data": post}


@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int):
    CURSOR.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(post_id),))
    CURSOR.fetchone()
    CONNECTION.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{post_id}")
def update_post(post_id: int, post: Post):
    CURSOR.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""", (post.title, post.content, post.published, str(post_id)))
    updated_post = CURSOR.fetchone()
    if not updated_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with {post_id} does not exist")
    CONNECTION.commit()
    return {"data": updated_post}
