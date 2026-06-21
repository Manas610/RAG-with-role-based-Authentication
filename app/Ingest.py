import os
import shutil
from pathlib import Path

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader
)

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = BASE_DIR / "data" / "chroma_db"


def load_documents():

    documents = []

    for file in os.listdir(DATA_DIR):

        file_path = DATA_DIR / file

        if file.endswith(".pdf"):
            loader = PyPDFLoader(str(file_path))

        elif file.endswith(".docx"):
            loader = Docx2txtLoader(str(file_path))

        elif file.endswith(".txt"):
            loader = TextLoader(str(file_path))

        else:
            continue

        docs = loader.load()

        for doc in docs:
            doc.metadata["filename"] = file
            doc.metadata["filetype"] = Path(file).suffix

        documents.extend(docs)

    return documents


def chunk_documents(documents):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_documents(documents)

    for idx, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = idx

    return chunks


def create_vector_store(chunks):

    embeddings = OpenAIEmbeddings()

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(CHROMA_DIR)
    )

    return vectorstore


def clear_existing_db():

    if CHROMA_DIR.exists():
        shutil.rmtree(CHROMA_DIR)


def run_ingestion():

    clear_existing_db()

    docs = load_documents()

    chunks = chunk_documents(docs)

    create_vector_store(chunks)

    return {
        "status": "success",
        "documents_processed": len(docs),
        "chunks_created": len(chunks),
        "chroma_path": str(CHROMA_DIR)
    }


if __name__ == "__main__":

    result = run_ingestion()

    print(result)