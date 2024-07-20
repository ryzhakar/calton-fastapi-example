from abc import ABC
from abc import abstractmethod

from selenium.webdriver.remote.webdriver import WebDriver

from app.interface import schemas


class AbstractReviewScrapingStrategy(ABC):
    """Common interface for review scraping strategies."""

    modal_locator: tuple[str, str]

    @abstractmethod
    async def load_more_reviews(self, driver: WebDriver) -> None:
        """Perform actions for a page to load more reviews."""

    @abstractmethod
    def parse_reviews(self, driver: WebDriver) -> list[schemas.Review]:
        """Extract reviews from the current page."""
