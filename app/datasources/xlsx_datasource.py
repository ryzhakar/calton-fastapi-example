from decimal import Decimal
from logging import getLogger

import pandas as pd
import pydantic

from app.interface import enums
from app.interface.schemas import PaginationOptions
from app.interface.schemas import Review

logger = getLogger(__name__)


class XLSXDatasource:
    """An xlsx-file parser and reader singleton."""

    _sorted_review_data: tuple[Review, ...]
    _datasource_length: int

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
                review = Review(
                    created_at=row[0],
                    reviewer_name=str(row[1]),
                    rating=Decimal(str(row[4])).quantize(Decimal('0.1')),
                    sentiment=enums.SentimentEnum(
                        int(row[3]),
                    ) if pd.notna(row[3]) else None,
                    review_text=str(row[2]) if pd.notna(row[2]) else None,
                )
            except (pydantic.ValidationError, ValueError, TypeError) as error:
                logger.error(
                    'Failed to parse row % in %: %',
                    row,
                    xlsx_file_path,
                    error,
                )
                continue
            reviews.append(review)
        cls._sorted_review_data = tuple(
            sorted(
                reviews,
                key=lambda rv: rv.created_at,
                reverse=True,
            ),
        )
        cls._datasource_length = len(reviews)

    def list_multiple_with(
        self,
        pagination: PaginationOptions,
    ) -> tuple[Review, ...]:
        """Return a slice of the reviews."""
        if not self._sorted_review_data:
            return ()
        if pagination.skip >= self._datasource_length:
            return ()
        last_index = min(
            self._datasource_length,
            pagination.skip + pagination.limit,
        )
        return self._sorted_review_data[pagination.skip:last_index]
