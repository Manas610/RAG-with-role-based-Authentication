from datetime import datetime, timedelta

from jose import jwt
from passlib.context import CryptContext

from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer

from app.Database import get_connection


SECRET_KEY = "my-secret-key"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

security = HTTPBearer(
    auto_error=False
)


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
        SELECT *
        FROM users
        WHERE username = ?
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

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    print("\n========== TOKEN CREATED ==========")
    print(token)

    return token


def verify_token(token):

    try:

        print("\n========== JWT DECODE ==========")

        print("TOKEN RECEIVED:")
        print(token)

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        print("\nJWT PAYLOAD:")
        print(payload)

        return payload

    except Exception as e:

        print("\n========== JWT ERROR ==========")

        print("ERROR TYPE:")
        print(type(e))

        print("\nERROR MESSAGE:")
        print(str(e))

        return None


def get_current_user(
    credentials=Depends(security)
):

    print("\n========== AUTH DEBUG ==========")

    print("\nRAW CREDENTIALS:")
    print(credentials)

    if credentials is None:

        print("\nNO AUTHORIZATION HEADER FOUND")

        raise HTTPException(
            status_code=401,
            detail="No Authorization Header"
        )

    print("\nSCHEME:")
    print(credentials.scheme)

    print("\nCREDENTIALS:")
    print(credentials.credentials)

    token = credentials.credentials

    if token.startswith("Bearer "):

        print("\nDOUBLE BEARER DETECTED")

        token = token[7:]

    print("\nFINAL TOKEN USED:")
    print(token)

    payload = verify_token(token)

    if payload is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid Token"
        )

    print("\nAUTH SUCCESS")

    print(payload)

    return payload