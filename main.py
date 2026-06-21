from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.Ingest import run_ingestion
from app.Retrieval import retrieve_answer

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
def retrieve(request: QueryRequest):

    try:
        answer = retrieve_answer(request.query)

        return {
            "query": request.query,
            "answer": answer
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )