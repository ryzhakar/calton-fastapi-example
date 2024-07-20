# FastAPI Restaurant Review Service

A FastAPI-based web service for managing restaurant reviews, featuring data scraping.

## Highlights

1. **Flexible, modular and robust FastAPI setup**
2. **Fine-grained Pydantic Validation**
3. **Cached scraping for two JustEat website invariants**

## Quick Start with Docker

1. Clone the repository and navigate to the project directory
2. Create a `.env` file: `cp .env.example .env`
3. Start the service: `docker-compose up --build`

The API will be available at `http://localhost:8000`.

## Testing the API

Disclamer: make sure you're on a british network. There's no way to tell if JustEat won't load yet another site version for foreign traffic.

Access the Swagger UI at `http://localhost:8000/docs` and test the following endpoints:

1. **Fetch Reviews**
   - Endpoint: GET `/reviews/`
   - Try different `skip` and `limit` values for pagination

2. **Add a Review**
   - Endpoint: POST `/reviews/`
   - Use the provided JSON schema to submit a new review

3. **Scrape JustEat Reviews**
   - Endpoint: GET `/reviews/scrape/justeat`
   - Parameter: `restaurant_slug` (e.g., "restaurants-kitchen-dhaanya-islington")
   - Example URL: `http://localhost:8000/reviews/scrape/justeat?restaurant_slug=restaurants-kitchen-dhaanya-islington&skip=0&limit=10`

## Environment Variables

The application uses the following environment variables for configuration:

| Variable | Description | Default Value |
|----------|-------------|---------------|
| APP_NAME | The name of the application | calton |
| SELENIUM_HOST | The hostname of the Selenium server | selenium-chrome |
| SELENIUM_PORT | The port of the Selenium server | 4444 |
| REVIEWS_XLSX_PATH | The path to load the reviews Excel file from | reviews.xlsx |
| ENVIRONMENT | The running environment of the application | development |
| TESTING | Whether the application is in testing mode | false |
| LOG_LEVEL | The logging level for the application | DEBUG |
| LOG_FORMAT | The format of the log output | colored |
