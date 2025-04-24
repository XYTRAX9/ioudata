from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from . import models, schemas
from .database import get_db

# Настройки JWT
SECRET_KEY = "your-secret-key-here"  # В продакшене использовать безопасный ключ
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_employee(db: Session, name: str) -> Optional[models.Employee]:
    return db.query(models.Employee).filter(models.Employee.name == name).first()

def authenticate_employee(db: Session, name: str, password: str) -> Optional[models.Employee]:
    employee = get_employee(db, name)
    if not employee:
        return None
    if not verify_password(password, employee.hashed_password):
        return None
    return employee

async def get_current_employee(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.Employee:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        name: str = payload.get("sub")
        if name is None:
            raise credentials_exception
        token_data = schemas.TokenData(name=name)
    except JWTError:
        raise credentials_exception
    employee = get_employee(db, name=token_data.name)
    if employee is None:
        raise credentials_exception
    return employee

async def get_current_active_employee(
    current_employee: models.Employee = Depends(get_current_employee),
) -> models.Employee:
    if not current_employee.is_active:
        raise HTTPException(status_code=400, detail="Inactive employee")
    return current_employee

async def get_current_superuser(
    current_employee: models.Employee = Depends(get_current_employee),
) -> models.Employee:
    if not current_employee.is_superuser:
        raise HTTPException(
            status_code=403, detail="The employee doesn't have enough privileges"
        )
    return current_employee 