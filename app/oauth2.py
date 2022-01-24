from http.client import HTTPException
from wsgiref.util import setup_testing_defaults
from jose import JWTError, jwt
from datetime import datetime, timedelta 
from app import schemas, database, models
from app.config import settings
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data: dict):
    
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def verify_access_token(token: str, credentials_exeptinon):

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        id = payload.get("user_id")
        if not id:
            raise credentials_exeptinon
        token_data = schemas.TokenData(id=id)
    except JWTError:
        raise credentials_exeptinon
    return token_data

def get_current_user(token: str = Depends(oauth2_scheme),
                     db: Session = Depends(database.get_db)):

    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"})
    token = verify_access_token(token, credentials_exception)
    user = db.query(models.User).filter(models.User.id == token.id).first()
    return user