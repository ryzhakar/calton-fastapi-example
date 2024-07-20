from app.initializers import selenium
from app.initializers import server
from app.initializers import xlsx
from app.routers import reviews
from app.settings import get_settings

settings = get_settings()
devmode = settings.environment == 'development'

app = server.get_app(
    reviews.router,
    lifespan=server.construct_lifespan(
        pre=[
            xlsx.load_xlsx_datasource,
            selenium.initialize_driver_pool,
        ],
        post=[
            selenium.shutdown_driver_pool,
        ],
    ),
    docs='/docs' if devmode else False,
)
