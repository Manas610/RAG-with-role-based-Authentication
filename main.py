from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel

from app.Ingest import run_ingestion
from app.Retrieval import retrieve_answer

from app.Auth import (
    authenticate_user,
    create_access_token,
    get_current_user
)

app = FastAPI(
    title="RAG API",
    version="1.0.0"
)


class QueryRequest(BaseModel):
    query: str


@app.get("/")
def home():
    return {
        "message": "RAG API Running"
    }


@app.post("/ingest")
def ingest_documents():
    try:
        result = run_ingestion()

        return {
            "success": True,
            "result": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.post("/retrieve")
def retrieve(request: QueryRequest,current_user=Depends(
        get_current_user
    )):

    try:
        answer = retrieve_answer(
            request.query,
            current_user["role"]
        )

        return {
            "query": request.query,
            "answer": answer
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/login")
def login(
    request: LoginRequest
):

    user = authenticate_user(
        request.username,
        request.password
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid Credentials"
        )

    token = create_access_token(
        {
            "sub": user["username"],
            "role": user["role"]
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }