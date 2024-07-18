from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends

from app.datasources import MemoryXLSXDatasource
from app.interface import schemas

router = APIRouter(prefix='/reviews')


@router.get('/', response_model=schemas.MultipleReviewsResponse)
def fetch_reviews(
    pagination: Annotated[schemas.PaginationOptions, Depends()],
    datasource: Annotated[MemoryXLSXDatasource, Depends()],
) -> schemas.MultipleReviewsResponse:
    """Return a slice of the reviews."""
    reviews = datasource.list_multiple_reviews_with(pagination)
    return schemas.MultipleReviewsResponse(reviews=reviews)
