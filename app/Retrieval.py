from pathlib import Path

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI

from app.Prompt import SYSTEM_PROMPT


BASE_DIR = Path(__file__).resolve().parent.parent

CHROMA_DIR = BASE_DIR / "data" / "chroma_db"

DISTANCE_THRESHOLD = 0.4

client = OpenAI()

embeddings = OpenAIEmbeddings()

def get_vectorstore():
    return Chroma(
        persist_directory=str(CHROMA_DIR),
        embedding_function=embeddings
    )


def retrieve_answer(query: str):

    vectorstore = get_vectorstore()

    results = vectorstore.similarity_search_with_score(
        query=query,
        k=3
    )

    if len(results) == 0:
        return {
            "answer": "No information found in documents.",
            "sources": []
        }

    best_distance = results[0][1]

    if best_distance > DISTANCE_THRESHOLD:
        return {
            "answer": "No similar information found in documents.",
            "sources": []
        }

    context_parts = []
    source_files = set()

    for doc, distance in results:

        filename = doc.metadata.get(
            "filename",
            "Unknown"
        )

        source_files.add(filename)

        context_parts.append(
            f"""
            Source File: {filename}
            Distance Score: {distance}

            Content:
            {doc.page_content}
            """
        )

    context = "\n\n".join(context_parts)

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": f"""
                Question:
                {query}

                Retrieved Context:
                {context}
                """
            }
        ]
    )

    answer = response.choices[0].message.content

    return {
        "answer": answer,
        "sources": list(source_files),
        "distance_score": best_distance
    }


if __name__ == "__main__":

    query = input("Enter your query: ")

    result = retrieve_answer(query)

    print("\n" + "=" * 60)
    print("ANSWER")
    print("=" * 60)

    print(result["answer"])

    print("\nSources:")

    for source in result["sources"]:
        print(f"- {source}")