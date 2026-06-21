from datetime import datetime, timedelta

from jose import jwt, JWTError

from passlib.context import CryptContext

from fastapi import HTTPException
from fastapi.security import HTTPBearer
from fastapi import Depends

from app.Database import get_connection


SECRET_KEY = "my-secret-key"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

security = HTTPBearer()


ROLE_PERMISSIONS = {
    "manager": {
        "cost.pdf",
        "development.docx",
        "leave.txt"
    },
    "project_lead": {
        "development.docx",
        "leave.txt"
    },
    "employee": {
        "leave.txt"
    }
}


def hash_password(password):

    return pwd_context.hash(password)


def verify_password(
    plain_password,
    hashed_password
):

    return pwd_context.verify(
        plain_password,
        hashed_password
    )


def authenticate_user(
    username,
    password
):

    conn = get_connection()

    user = conn.execute(
        """
        SELECT * FROM users WHERE username = ?
        """,
        (username,)
    ).fetchone()

    conn.close()

    if not user:
        return None

    if not verify_password(
        password,
        user["password"]
    ):
        return None

    return dict(user)


def create_access_token(data):

    payload = data.copy()
    expire = (
        datetime.utcnow()
        + timedelta(hours=1)
    )

    payload["exp"] = expire

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def verify_token(token):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload
    
    except JWTError:
        return None


def get_current_user(
    credentials=Depends(security)
):

    token = credentials.credentials

    if token.startswith("Bearer "):
        token = token.replace(
            "Bearer ",
            "",
            1
        )
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid Token"
        )

    return payload