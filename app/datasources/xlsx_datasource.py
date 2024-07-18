from datetime import timezone
from decimal import Decimal
from logging import getLogger

import pandas as pd
import pydantic

from app.interface import enums
from app.interface.schemas import PaginationOptions
from app.interface.schemas import Review

logger = getLogger('app')


class MemoryXLSXDatasource:
    """An in-memory xlsx-file parser and reader singleton.

    Allows adding elements, but won't persist them to disk.
    """

    _instance = None
    _sorted_review_data: list[Review] = []
    _datasource_length: int = 0

    def __new__(cls):
        """Return the single instance if created."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # We can afford to couple this particular class to an example file,
    # since this would not be the case in reality.
    # Otherwise we would make this code much more modular and generic.
    @classmethod
    def load_from(cls, xlsx_file_path: str) -> None:
        """Loads the file and parses the data."""
        dataframe = pd.read_excel(xlsx_file_path)
        reviews: list[Review] = []
        for _, row in dataframe.iterrows():
            try:
                reviews.append(cls._parse_row(row))
            except (pydantic.ValidationError, ValueError, TypeError) as error:
                logger.debug(
                    'Failed to parse row % in %: %',
                    row,
                    xlsx_file_path,
                    error,
                )
        cls._sorted_review_data = _sort_by_time(reviews)
        cls._datasource_length = len(reviews)

    def list_multiple_reviews_with(
        self,
        pagination: PaginationOptions,
    ) -> list[Review]:
        """Return a slice of the reviews."""
        if not self._sorted_review_data:
            return []
        if pagination.skip >= self._datasource_length:
            return []
        last_index = min(
            self._datasource_length,
            pagination.skip + pagination.limit,
        )
        return self._sorted_review_data[pagination.skip:last_index]

    def add_reviews(self, *new_reviews: Review) -> None:
        """Extend the review list and re-sort it.

        This implementation offers no persistance to disk though.
        """
        self._datasource_length += len(new_reviews)
        self._sorted_review_data.extend(new_reviews)
        self._sorted_review_data = _sort_by_time(self._sorted_review_data)

    @classmethod
    def _parse_row(cls, row: pd.Series) -> Review:
        reviewer_name = str(row.iloc[1])
        created_datetime = row.iloc[0].replace(tzinfo=timezone.utc)
        rating = Decimal(str(row.iloc[4]))
        rating = rating.quantize(Decimal('0.1'))
        sentiment = (
            enums.SentimentEnum(int(row.iloc[3]))
            if pd.notna(row.iloc[3])
            else None
        )
        review_text = (
            str(row.iloc[2])
            if pd.notna(row.iloc[2])
            else None
        )

        return Review(
            created_at=created_datetime,
            reviewer_name=reviewer_name,
            rating=rating,
            sentiment=sentiment,
            review_text=review_text,
        )


def _sort_by_time(
    multiple_reviews: list[Review],
    reverse: bool = True,
) -> list[Review]:
    return sorted(
        multiple_reviews,
        key=lambda rv: rv.created_at,
        reverse=reverse,
    )
