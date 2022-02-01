from http.client import HTTPException
from jose import JWTError, jwt
from datetime import datetime, timedelta 
from fastapi_example import schemas, database, models
from fastapi_example.config import settings
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


def verify_access_token(token: str, credentials_exception):

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id = payload.get("user_id")
        if not user_id:
            raise credentials_exception
        token_data = schemas.TokenData(id=user_id)
    except JWTError:
        raise credentials_exception
    return token_data


def get_current_user(token: str = Depends(oauth2_scheme),
                     db: Session = Depends(database.get_db)):

    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"})
    token = verify_access_token(token, credentials_exception)
    return db.query(models.User).filter(models.User.id == token.id).first()
