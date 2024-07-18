from datetime import date
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel
from pydantic import Field
from pydantic import model_validator
from typing_extensions import Self

from app.interface import enums


_MAX_REVIEW_LENGTH = 500
_MAX_NAME_LENGTH = 100
_constrained_review_decimal = Field(
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


class Review(BaseModel):
    """User-generated review of a product."""
    created_date: date
    reviewer_name: Annotated[str, _constrained_reviewer_name]
    rating: Annotated[Decimal, _constrained_review_decimal]
    # These optional fields should always be paired
    sentiment: enums.SentimentEnum | None = None
    review_text: Annotated[str, _contrained_review_text] | None = None

    @model_validator(mode='after')
    def review_text_has_sentiment(self) -> Self:
        """Check that there's either both text and sentiment or neither."""
        if (self.review_text is None) == (self.sentiment is None):
            return self
        raise ValueError('Both review_text and sentiment must be set or unset.')


class PaginationOptions(BaseModel):
    """A skip/limit pagination configuration."""
    skip: Annotated[int, Field(ge=1)] | None = None
    limit: Annotated[int, Field(ge=1)] | None = None
