from app.datasources import MemoryXLSXDatasource
from app.initializers.logger import get_logger
from app.settings import get_settings

settings = get_settings()
logger = get_logger()


async def load_xlsx_datasource():
    """An async wrapper for an excel sheet loader."""
    MemoryXLSXDatasource.load_from(settings.reviews_xlsx_path)
    logger.info('Loaded the XLSX datasource.')
