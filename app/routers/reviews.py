from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import Response

from app.datasources import MemoryXLSXDatasource
from app.interface import schemas

router = APIRouter(prefix='/reviews')
_CREATED_STATUS_CODE = 201


@router.get('/', response_model=schemas.MultipleReviewsResponse)
async def fetch_reviews(
    pagination: Annotated[schemas.PaginationOptions, Depends()],
    datasource: Annotated[MemoryXLSXDatasource, Depends()],
) -> schemas.MultipleReviewsResponse:
    """Return a page of reviews from the datasource."""
    reviews = datasource.list_multiple_reviews_with(pagination)
    return schemas.MultipleReviewsResponse(reviews=reviews)


@router.post('/')
async def add_review(
    datasource: Annotated[MemoryXLSXDatasource, Depends()],
    review_body: schemas.ReviewCreationBody,
) -> Response:
    """Add a review to the datasource."""
    datasource.add_reviews(review_body)
    return Response(status_code=_CREATED_STATUS_CODE)
