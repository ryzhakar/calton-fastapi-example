from collections.abc import MutableMapping
from datetime import datetime
from datetime import timezone
from decimal import Decimal

import undetected_chromedriver as uc  # type: ignore
from cachetools import TTLCache
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as e_cond
from selenium.webdriver.support.ui import WebDriverWait

from app.datasources.scraping_utils import humanize_with_pauses
from app.datasources.scraping_utils import sleep_with_jitter
from app.initializers.logger import get_logger
from app.interface import abstract
from app.interface import exceptions as ex
from app.interface import schemas
logger = get_logger('app')

_DEFAULT_RATING_FLOAT = '3.0'
_DEFAULT_RATING_PERCENTAGE = '60%'
_PERCENTAGE_TO_RATING_STEP = 20
_LOCATION_TIMEOUT = 10
_CACHE_EXPIRATION = 3600
_CACHE_SIZE = 1000


class ButtonLoadModalStrategy(abstract.AbstractReviewScrapingStrategy):
    """Strategy for a modal window with a button fro pagination."""
    modal_locator = (By.CSS_SELECTOR, "[data-test-id='reviews-modal']")

    async def load_more_reviews(self, driver: WebDriver) -> None:
        """Load more reviews by scrolling and clicking."""
        await self._scroll_to_load_more_button(driver)
        await self._click_load_more_button(driver)
        await self._wait_for_reviews(driver)

    def parse_reviews(self, driver: WebDriver) -> list[schemas.Review]:
        """Parse reviews from the modal window."""
        review_elements = driver.find_element(
            By.CLASS_NAME, 'c-reviews-items',
        ).find_elements(
            By.CLASS_NAME, 'c-reviews-item',
        )
        return [self._parse_review(element) for element in review_elements]

    @humanize_with_pauses(pre=1)
    async def _scroll_to_load_more_button(self, driver: WebDriver) -> None:
        try:
            load_more_button = driver.find_element(
                By.CSS_SELECTOR, "[data-test-id='review-show-more-button']",
            )
        except NoSuchElementException as error:
            logger.warning('Load more button not found')
            raise ex.NoMoreReviewsError('Load more button not found') from error
        driver.execute_script(
            'arguments[0].scrollIntoView(true);', load_more_button,
        )

    @humanize_with_pauses(pre=1, post=2)
    async def _click_load_more_button(self, driver: WebDriver) -> None:
        try:
            button = WebDriverWait(driver, _LOCATION_TIMEOUT).until(
                e_cond.element_to_be_clickable(
                    (
                        By.CSS_SELECTOR,
                        "[data-test-id='review-show-more-button']",
                    ),
                ),
            )
        except TimeoutException:
            logger.warning('Load more button not clickable')
            raise ex.NoMoreReviewsError(
                'Load more button not clickable',
            )
        button.click()

    async def _wait_for_reviews(self, driver: WebDriver) -> None:
        try:
            WebDriverWait(driver, _LOCATION_TIMEOUT).until(
                lambda drv: drv.find_elements(By.CLASS_NAME, 'c-reviews-item'),
            )
        except TimeoutException:
            logger.warning('No new reviews loaded after clicking')
            raise ex.NoMoreReviewsError('No new reviews loaded after clicking')

    def _parse_review(self, review_element: WebElement) -> schemas.Review:
        name = review_element.find_element(
            By.CSS_SELECTOR, "[data-test-id='review-author']",
        ).text
        date_str = review_element.find_element(
            By.CSS_SELECTOR, "[data-test-id='review-date']",
        ).text
        return schemas.Review(
            created_at=self._parse_date(date_str),
            reviewer_name=name,
            rating=self._parse_rating(review_element),
            review_text=self._parse_review_text(review_element),
            sentiment=None,
        )

    def _parse_review_text(self, review_element: WebElement) -> str | None:
        try:
            return review_element.find_element(
                By.CSS_SELECTOR, "[data-test-id='review-text']",
            ).text
        except NoSuchElementException:
            return None

    def _parse_rating(self, review_element: WebElement) -> Decimal:
        rating_element = review_element.find_element(
            By.CSS_SELECTOR, "[data-test-id='rating-multi-star-component']",
        )
        stars = rating_element.find_element(
            By.CSS_SELECTOR, "[class*='c-rating-mask']",
        )
        style = stars.get_attribute('style') or _DEFAULT_RATING_PERCENTAGE
        rating = Decimal(
            self._parse_percentage(style) / _PERCENTAGE_TO_RATING_STEP,
        )
        return rating.quantize(Decimal('0.1'))

    def _parse_percentage(self, style: str) -> int:
        perc_tail = style.split(':')[-1]
        clean_digits = perc_tail.strip().rstrip('%;')
        return int(clean_digits)

    def _parse_date(self, date_str: str) -> datetime:
        day, month, year = map(int, date_str.split('/'))
        return datetime(year, month, day, tzinfo=timezone.utc)


class AutoScrollModalStrategy(abstract.AbstractReviewScrapingStrategy):
    """Strategy for a modal window with automatic loading on scrolling."""

    modal_locator = (By.CSS_SELECTOR, "[data-qa='restaurant-info-modal']")

    async def load_more_reviews(self, driver: WebDriver):
        """Load more reveiws by scrolling the modal window."""
        modal = driver.find_element(
            By.CSS_SELECTOR, "[data-qa='restaurant-info-modal']",
        )
        scroll_content = modal.find_element(
            By.CSS_SELECTOR, "[data-qa='modal-scroll-content']",
        )
        last_height, new_height = await self._scroll_element(
            driver,
            scroll_content,
        )
        if new_height == last_height:
            raise ex.NoMoreReviewsError('No more reviews to load')

    def parse_reviews(self, driver: WebDriver) -> list[schemas.Review]:
        """Parse reviews from the modal window."""
        review_elements = driver.find_elements(
            By.CSS_SELECTOR, "[data-qa='review-card-component-element']",
        )
        return [self._parse_review(element) for element in review_elements]

    @humanize_with_pauses(pre=1)
    async def _scroll_element(self, driver: WebDriver, element: WebElement):
        last_height = driver.execute_script(
            'return arguments[0].scrollHeight', element,
        )
        driver.execute_script(
            'arguments[0].scrollTo(0, arguments[0].scrollHeight);', element,
        )
        await sleep_with_jitter(2)
        new_height = driver.execute_script(
            'return arguments[0].scrollHeight', element,
        )
        return last_height, new_height

    def _parse_review(self, review_element: WebElement) -> schemas.Review:
        name, date_obj = self._parse_label(
            review_element.find_element(
                By.XPATH, ".//div[starts-with(@id, 'label-')]",
            ),
        )
        rating, text = self._parse_description(
            review_element.find_element(
                By.XPATH, ".//div[starts-with(@id, 'description-')]",
            ),
        )
        return schemas.Review(
            created_at=date_obj,
            reviewer_name=name,
            rating=rating,
            review_text=text,
            sentiment=None,
        )

    def _parse_label(self, label_element: WebElement) -> tuple[str, datetime]:
        name = label_element.find_element(
            By.CSS_SELECTOR, "[data-qa='text']",
        ).text
        date_str = label_element.find_element(
            By.CSS_SELECTOR, "b[data-qa='text']",
        ).text
        date_obj = datetime.strptime(
            date_str, '%A %d %B %Y',
        ).replace(tzinfo=timezone.utc)
        return name, date_obj

    def _parse_description(
        self,
        description_element: WebElement,
    ) -> tuple[Decimal, str | None]:
        rating_el = description_element.find_element(
            By.CSS_SELECTOR, "[data-qa='rating-display-element']",
        )
        raw_rating = rating_el.get_attribute('title') or _DEFAULT_RATING_FLOAT
        rating = Decimal(raw_rating.split()[0])
        text_element = description_element.find_elements(
            By.CSS_SELECTOR, "[data-qa='review-card-comment']",
        )
        text = text_element[0].text if text_element else None
        return rating, text


class JustEatDataSource:
    """Just Eat site scraper as a data source."""

    strategy: abstract.AbstractReviewScrapingStrategy
    possible_strategies = (AutoScrollModalStrategy, ButtonLoadModalStrategy)
    url_template = 'https://www.just-eat.co.uk/{rbf}/reviews?openOnWeb=true'
    buffer_cache: MutableMapping[str, list[schemas.Review]] = TTLCache(
        maxsize=_CACHE_SIZE,
        ttl=_CACHE_EXPIRATION,
    )

    def __init__(self, restaurant_slug: str):
        """Set up basic configuration."""
        self.restaurant_slug = restaurant_slug
        self.base_url = self.url_template.format(rbf=restaurant_slug)
        self.options = self._setup_options()
        self.review_buffer = self.buffer_cache.get(restaurant_slug, [])
        self.driver: WebDriver | None = None

    async def __aenter__(self):
        """Do nothing except open the context."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up driver-related resources."""
        if self.driver is None:
            return
        cache_size = len(self.buffer_cache.get(self.restaurant_slug, []))
        buffer_size = len(self.review_buffer)
        if cache_size < buffer_size:
            self.buffer_cache[self.restaurant_slug] = self.review_buffer
        self.driver.quit()

    async def initialize_driver(self):
        """Initialize the driver and validate the URL."""
        if self.driver:
            return
        logger.info('Initializing selenium driver')
        self.driver = uc.Chrome(options=self.options)
        await self._validate_url()
        self.strategy = await self._determine_strategy()

    async def get_reviews(
        self,
        pagination: schemas.PaginationOptions,
    ) -> list[schemas.Review]:
        """Get reviews with pagination.

        Will try to use cached values if possible.
        """
        required_buffer_length = pagination.skip + pagination.limit
        if len(self.review_buffer) >= required_buffer_length:
            return self.review_buffer[pagination.skip:required_buffer_length]
        await self.initialize_driver()
        while len(self.review_buffer) < required_buffer_length:
            try:
                await self._fill_buffer()
            except ex.NoMoreReviewsError:
                logger.info('No more reviews available')
                break

        cutoff = min(len(self.review_buffer), required_buffer_length)
        return self.review_buffer[pagination.skip:cutoff]

    @humanize_with_pauses(pre=1)
    async def _fill_buffer(self):
        if self.driver is None:
            raise ex.ScraperNotInitializedError('Driver not initialized')
        await self.strategy.load_more_reviews(self.driver)
        new_reviews = self.strategy.parse_reviews(self.driver)
        if not new_reviews:
            logger.warning('No new reviews parsed after loading')
            raise ex.NoMoreReviewsError('No new reviews loaded')
        self.review_buffer.extend(new_reviews)

    def _setup_options(self):
        options = uc.ChromeOptions()
        options.add_argument('--disable-dev-shm-usage')
        return options

    async def _validate_url(self):
        if self.driver is None:
            raise ex.ScraperNotInitializedError('Driver not initialized')
        self.driver.get(self.base_url)

    async def _determine_strategy(
        self,
    ) -> abstract.AbstractReviewScrapingStrategy:
        for strategy_builder in self.possible_strategies:
            if await self._try_strategy(strategy_builder.modal_locator):
                return strategy_builder()
        raise ex.UnsupportedPageStructureError('Unsupported page structure')

    async def _try_strategy(self, element_locator: tuple[str, str]) -> bool:
        if self.driver is None:
            raise ex.ScraperNotInitializedError('Driver not initialized')
        try:
            self.driver.find_element(*element_locator)
        except NoSuchElementException:
            return False
        return True
