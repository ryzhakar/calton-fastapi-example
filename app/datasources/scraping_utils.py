import asyncio
import random

from app.initializers.logger import get_logger
logger = get_logger()


async def sleep_with_jitter(
    seconds: int,
    distribution_bounding_box: tuple[float, float] = (0.75, 1.25),
) -> None:
    """Sleep in a non-blocking way, with noise applied to the duration."""
    multiplier = random.uniform(*distribution_bounding_box)  # noqa: S311
    await asyncio.sleep(seconds * multiplier)


def humanize_with_pauses(
    pre: int = 0,
    post: int = 0,
    distribution_bounding_box: tuple[float, float] = (0.75, 1.25),
):
    """Add pauses before and/or after execution to humanize the behavior."""
    if not (pre or post):
        raise ValueError('At least one of pre or post must be non-zero')

    def decorator(func):
        async def wrapper(*args, **kwargs):
            if pre:
                logger.debug(
                    'function %s sleeping for %s seconds before execution',
                    func.__name__,
                    pre,
                )
                await sleep_with_jitter(
                    pre,
                    distribution_bounding_box=distribution_bounding_box,
                )
            execution_result = await func(*args, **kwargs)
            if post:
                logger.debug(
                    'function %s sleeping for %s seconds after execution',
                    func.__name__,
                    post,
                )
                await sleep_with_jitter(
                    post,
                    distribution_bounding_box=distribution_bounding_box,
                )
            return execution_result
        return wrapper

    return decorator
