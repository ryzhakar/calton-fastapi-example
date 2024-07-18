from app import datasources
from app.initializers import server
from app.routers import reviews
from app.settings import get_settings

settings = get_settings()
devmode = settings.environment == 'development'

app = server.get_app(
    reviews.router,
    lifespan=server.construct_lifespan(
        pre=[
            lambda: datasources.MemoryXLSXDatasource.load_from(
                settings.reviews_xlsx_path,
            ),
        ],
        post=[],
    ),
    docs='/docs' if devmode else False,
)
