from pathlib import Path

from src.models.newsletters import DeliveryStatus, Newsletter
from src.utils import jsonl_file_manager as file_manager
from src.utils.datetime_utils import datetime_to_iso


class NewsletterRepository:

    def load_newsletters(
        self,
        newsletters_file: Path
    ) -> list[Newsletter]:

        records = file_manager.load_jsonl_file(
            newsletters_file
        )

        return [
            Newsletter(
                newsletter_id= record["newsletter_id"],
                profile_id= record["profile_id"],
                generated_at= record["generated_at"],
                content= record["content"],
                delivery_status= DeliveryStatus(
                    record["delivery_status"]
                ),
            )
            for record in records
        ]
    
    def append_newsletters(
        self,
        newsletters: list[Newsletter],
        newsletters_file: Path,
    ) -> None:

        records = [
            {
                "newsletter_id": newsletter.newsletter_id,
                "profile_id": newsletter.profile_id,
                "generated_at": newsletter.generated_at,
                "content": newsletter.content,
                "delivery_status": newsletter.delivery_status.value,
            }
            for newsletter in newsletters
        ]

        file_manager.append_to_jsonl_file(
            newsletters_file,
            records,
        )

    def remove_newsletter(
        self,
        newsletter: Newsletter,
        newsletters_file: Path,
    ) -> None:

        newsletters = self.load_newsletters(
            newsletters_file
        )

        remaining = [
            current
            for current in newsletters
            if current.newsletter_id != newsletter.newsletter_id
        ]

        file_manager.save_jsonl_file(
            newsletters_file,
            [
                {
                    "newsletter_id": current.newsletter_id,
                    "profile_id": current.profile_id,
                    "generated_at": datetime_to_iso(current.generated_at),
                    "content": current.content,
                    "delivery_status": current.delivery_status.value,
                }
                for current in remaining
            ],
        )

    def get_last_id(
        self,
        newsletters_file: Path,
    ) -> int:
        """
        Return the highest newsletter identifier stored.

        Returns 0 when no newsletters have been stored yet.
        """

        newsletters = self.load_newsletters(
            newsletters_file
        )

        if not newsletters:
            return 0

        return max(
            newsletter.newsletter_id
            for newsletter in newsletters
        )