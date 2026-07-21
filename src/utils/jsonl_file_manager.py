import json
from pathlib import Path


def load_jsonl_file(
        file_path: Path,
    ) -> list[dict]:

        with file_path.open(
            "r",
            encoding="utf-8",
        ) as file:

            return [
                json.loads(line)
                for line in file
            ]
    
def save_to_jsonl_file(
    file_path: Path,
    records: list[dict],
) -> None:

    with file_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        for record in records:
            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                )
            )

            file.write("\n")

def append_to_jsonl_file(
    file_path: Path,
    records: list[dict],
) -> None:

    with file_path.open(
        "a",
        encoding="utf-8",
    ) as file:

        for record in records:
            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                )
            )

            file.write("\n")