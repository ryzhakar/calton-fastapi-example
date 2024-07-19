class ReviewScraperError(Exception):
    """Base exception for review scraping errors."""


class NoMoreReviewsError(ReviewScraperError):
    """Raised when there are no more reviews to load."""


class UnsupportedPageStructureError(ReviewScraperError):
    """Raised when the page structure is not supported by any strategy."""


class ScraperNotInitializedError(ReviewScraperError):
    """Raised when the scraper is not initialized."""
