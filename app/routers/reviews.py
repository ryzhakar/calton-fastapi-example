from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi.responses import Response

from app.datasources import JustEatDataSource
from app.datasources import MemoryXLSXDatasource
from app.interface import exceptions as ex
from app.interface import schemas

router = APIRouter(prefix='/reviews')
_CREATED_STATUS_CODE = 201
_NOT_FOUND_STATUS_CODE = 404


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


@router.get('/scrape/justeat', response_model=schemas.MultipleReviewsResponse)
async def scrape_justeat(
    datasource: Annotated[JustEatDataSource, Depends()],
    pagination: Annotated[schemas.PaginationOptions, Depends()],
) -> schemas.MultipleReviewsResponse:
    """Scrape reviews from Just Eat."""
    async with datasource:
        try:
            reviews = await datasource.get_reviews(pagination)
        except ex.UnsupportedPageStructureError as error:
            raise HTTPException(
                status_code=_NOT_FOUND_STATUS_CODE,
                detail=str(error),
            ) from error
    return schemas.MultipleReviewsResponse(reviews=reviews)
