from pathlib import Path

from src.models.sources import Source
from src.utils import jsonl_file_manager as file_manager


class SourceRepository:

    def __init__(
        self,
        sources_file: Path,
    ):
        self.sources_file = (
            sources_file
        )

    def load_sources(
        self,
    ) -> list[Source]:

        records = file_manager.load_jsonl_file(
            self.sources_file
        )

        return [
            Source(
                link=record["link"],
                name=record["name"],
                language=record["language"]
            )
            for record in records
        ]
    
    def load_sources_by_links(
        self,
        links: list[str]
    ) -> list[Source]:
        """
        Load the sources whose links are included in the given list.
        """
        link_set = set(links)

        return [
            source
            for source in self.load_sources()
            if source.link in link_set
        ]
    