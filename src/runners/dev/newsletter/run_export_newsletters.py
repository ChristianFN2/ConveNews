from pathlib import Path
import json


NEWSLETTERS_FILE = Path(
    "src/runners/dev/data/output/newsletters.jsonl"
)

OUTPUT_DIR = Path(
    "src/runners/dev/data/output/newsletters"
)


def main() -> None:
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with NEWSLETTERS_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:

        for line in file:
            record = json.loads(line)

            newsletter_id = record["newsletter_id"]
            html = record["content"]

            output_file = (
                OUTPUT_DIR
                / f"newsletter_{newsletter_id}.html"
            )

            output_file.write_text(
                html,
                encoding="utf-8",
            )


if __name__ == "__main__":
    main()