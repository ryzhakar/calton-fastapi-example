import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from selenium.webdriver import Remote
from selenium.webdriver.chrome.options import Options

from app.initializers.logger import get_logger
from app.settings import get_settings

settings = get_settings()
logger = get_logger()


class WebDriverPool:
    """A pool of WebDriver instances."""

    def __init__(self, max_drivers: int = 1):
        """Initialize the semaphore and containers, btu not the drivers."""
        self.max_drivers = max_drivers
        self.drivers: list[Remote] = []
        self.semaphore = asyncio.Semaphore(max_drivers)
        self.selenium_url = 'http://{host}:{port}/wd/hub'.format(
            host=settings.selenium_host,
            port=settings.selenium_port,
        )

    @asynccontextmanager
    async def get_driver(self) -> AsyncGenerator[Remote, None]:
        """Get a context manager for the WebDriver."""
        async with self.semaphore:
            driver = await self._get_or_create_driver()
            try:
                yield driver
            finally:
                await self._return_driver(driver)

    async def _get_or_create_driver(self) -> Remote:
        if not self.drivers:
            return await self._create_driver()
        return self.drivers.pop()

    async def _create_driver(self) -> Remote:
        options = self._setup_options()
        return Remote(command_executor=self.selenium_url, options=options)

    async def _return_driver(self, driver: Remote) -> None:
        if len(self.drivers) < self.max_drivers:
            self.drivers.append(driver)
        else:
            driver.quit()

    def _setup_options(self) -> Options:
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1280,1024')
        options.add_argument('--disable-gpu')
        options.add_argument('--remote-debugging-port=9222')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-setuid-sandbox')
        return options


DRIVER_POOL = WebDriverPool()


async def initialize_driver_pool() -> None:
    """Initialize the WebDriver pool."""
    logger.info('Initializing WebDriver pool')
    # Create the first WebDriver instance
    async with DRIVER_POOL.get_driver():
        logger.debug('WebDriver pool initialized')


async def shutdown_driver_pool() -> None:
    """Shutdown the WebDriver pool."""
    logger.info('Shutting down WebDriver pool')
    for driver in DRIVER_POOL.drivers:
        driver.quit()
    DRIVER_POOL.drivers.clear()
