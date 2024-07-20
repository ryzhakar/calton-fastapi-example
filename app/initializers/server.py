import itertools
from collections.abc import Callable
from collections.abc import Coroutine
from collections.abc import Iterable
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.routing import APIRouter
from starlette.types import Lifespan

from app.initializers.logger import get_logger
from app.settings import get_settings

settings = get_settings()
logger = get_logger()

_ENDPOINT_TABBING: str = '\n\t\t\t\t'


def get_app(
    *routers: APIRouter,
    lifespan: Lifespan | None = None,
    **kwargs: Any,
) -> FastAPI:
    """A FastAPI app constructor.

    *routers: routers to include. **kwargs: FastAPI class constructor
    keyword arguments.
    """
    logger.info('Creating the FastAPI app...')
    endpoint_names = list_endpoint_names(
        *routers,
        separator=_ENDPOINT_TABBING,
    )
    logger.info(f'Including endpoints...{endpoint_names}')
    app = FastAPI(
        logging=logger,
        lifespan=lifespan,
        **kwargs,
    )
    for router in routers:
        app.include_router(router)

    return app


def list_endpoint_names(
    *routers: APIRouter,
    separator: str,
) -> str:
    """Constructs a logging-friendly list of endpoints."""
    endpoints = itertools.chain.from_iterable(
        router.routes
        for router in routers
    )
    endpoint_names = (
        route.path  # type: ignore
        for route in endpoints
    )
    consolidated_names = separator.join(endpoint_names)
    return separator + consolidated_names


def construct_lifespan(
    *,
    pre: Iterable[Callable[..., Coroutine]],
    post: Iterable[Callable[..., Coroutine]],
) -> Lifespan:
    """Constructs a lifespan context manager for FastAPI."""
    @asynccontextmanager
    async def lifespan_context(_app: FastAPI):  # noqa: WPS430
        """A lifespan context manager for FastAPI."""
        for start_call in pre:
            await start_call()
        yield
        for finish_call in post:
            await finish_call()
    return lifespan_context
