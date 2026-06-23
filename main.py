from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel

from app.Ingest import run_ingestion
from app.Retrieval import retrieve_answer
import app.Config as Config

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

class ConfigRequest(BaseModel):
    chunk_size: int | None = None
    chunk_overlap: int | None = None
    top_k: int | None = None
    temperature: float | None = None


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
            current_user["role"],
            current_user["sub"]
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

@app.post("/config")
def update_config(
    request: ConfigRequest
):

    if request.chunk_size is not None:
        Config.CHUNK_SIZE = request.chunk_size

    if request.chunk_overlap is not None:
        Config.CHUNK_OVERLAP = request.chunk_overlap

    if request.top_k is not None:
        Config.TOP_K = request.top_k

    if request.temperature is not None:
        Config.TEMPERATURE = request.temperature

    return {
        "chunk_size": Config.CHUNK_SIZE,
        "chunk_overlap": Config.CHUNK_OVERLAP,
        "top_k": Config.TOP_K,
        "temperature": Config.TEMPERATURE
    }

@app.get("/config")
def get_config():

    return {
        "chunk_size": Config.CHUNK_SIZE,
        "chunk_overlap": Config.CHUNK_OVERLAP,
        "top_k": Config.TOP_K,
        "temperature": Config.TEMPERATURE
    }