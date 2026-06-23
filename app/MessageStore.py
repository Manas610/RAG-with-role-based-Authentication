import json
from pathlib import Path
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent.parent
MESSAGES_DIR = BASE_DIR / "messages"
MESSAGES_DIR.mkdir(
    exist_ok=True
)


def save_message(username: str, query: str, response: str):
    file_path = (MESSAGES_DIR / f"{username}.json")

    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

    else:
        data = []

    data.append(
        {
            "timestamp":
                datetime.utcnow().isoformat(),

            "query":
                query,

            "response":
                response
        }
    )

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)