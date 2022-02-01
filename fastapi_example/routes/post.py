from typing import List, Optional
from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from fastapi_example import database, models, schemas, oauth2


router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/", response_model=List[schemas.Post])
def test_post(db: Session = Depends(database.get_db),
              limit: int = 10,
              skip: int = 0,
              search: Optional[str] = ""):
    posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return posts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate,
                db: Session = Depends(database.get_db),
                current_user=Depends(oauth2.get_current_user)):
    new_post = models.Post(owner_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/{post_id}", response_model=schemas.Post)
def get_post(post_id: int,
             db: Session = Depends(database.get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail=f"Post {post_id} does not exist")
    
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int,
                db: Session = Depends(database.get_db),
                current_user=Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == post_id)
    if not post.first():
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail=f"Post {post_id} does not exist")
    if post.first().owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{post_id}", response_model=schemas.Post)
def update_post(post_id: int,
                post: schemas.PostCreate,
                db: Session = Depends(database.get_db),
                current_user=Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == post_id)
    if not post_query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with {post_id} does not exist")
    if post_query.first().owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")
    post_query.update(post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()
