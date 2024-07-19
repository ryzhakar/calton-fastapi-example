import textwrap
from datetime import datetime
from datetime import timezone
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import field_validator
from pydantic import model_validator
from pydantic import ValidationInfo
from typing_extensions import Self

from app.interface.enums import SentimentEnum


_MAX_REVIEW_LENGTH = 500
_MAX_NAME_LENGTH = 100
_constrained_review_decimal = Field(
    title='Rating as a decimal',
    description='A single decimal place number between 1.0 and 5.0.',
    ge=1,
    le=5,
    allow_inf_nan=False,
    decimal_places=1,
)
_contrained_review_text = Field(
    min_length=1,
    max_length=_MAX_REVIEW_LENGTH,
)
_constrained_reviewer_name = Field(
    min_length=1,
    max_length=_MAX_NAME_LENGTH,
)
_sentiment_enum_field = Field(
    title='Sentiment as an integer',
    description='1 for positive, 0 for neutral, -1 for negative.',
    examples=list(SentimentEnum),
)


class Review(BaseModel):
    """A user-generated review object with validation."""
    created_at: datetime = Field()
    reviewer_name: Annotated[str, _constrained_reviewer_name]
    rating: Annotated[Decimal, _constrained_review_decimal]
    # These optional fields should be validated downstream
    # to only receive both or neither.
    sentiment: Annotated[SentimentEnum, _sentiment_enum_field] | None = None
    review_text: Annotated[str, _contrained_review_text] | None = None

    @field_validator('created_at')
    @classmethod
    def tz_aware_created_at(
        cls,
        raw_value: datetime,
        _: ValidationInfo,
    ) -> datetime:
        """Treat naive datetimes as UTC."""
        if raw_value.tzinfo is None:
            return raw_value.replace(tzinfo=timezone.utc)
        return raw_value


class ReviewCreationBody(Review):
    """A review object with examples for creation."""
    model_config = ConfigDict(
        json_schema_extra={
            'description': textwrap.fill(
                textwrap.dedent(
                    """
                    A user-generated review of a product.
                    Naive datetimes are treated as UTC timezone-aware.
                    'sentiment' and 'review_text' must either both be set
                    or both be unset. It is not valid to have
                    only one of these fields set while the other is null.
                    """,
                ),
            ),
            'examples': [
                {
                    'created_at': datetime.now(timezone.utc).isoformat(),
                    'reviewer_name': 'Davide',
                    'rating': 4.9,
                    'sentiment': 0,
                    'review_text': textwrap.fill(
                        textwrap.dedent(
                            """
                            These tacos are otherwordly!
                            Won't deliver to London though :(
                            """,
                        ),
                    ),
                },
                {
                    'created_at': datetime.now(timezone.utc).isoformat(),
                    'reviewer_name': 'Dario',
                    'rating': 3,
                },
            ],
        },
    )

    @model_validator(mode='after')
    def review_text_has_sentiment(self) -> Self:
        """Check that there's either both text and sentiment or neither."""
        if (self.review_text is None) == (self.sentiment is None):
            return self
        raise ValueError('Both review_text and sentiment must be set or unset.')


class PaginationOptions(BaseModel):
    """A skip/limit pagination configuration."""
    skip: Annotated[int, Field(ge=0)] = 0
    limit: Annotated[int, Field(ge=1)] = 10


class MultipleReviewsResponse(BaseModel):
    """An extensible container for reviews."""
    reviews: list[Review]
