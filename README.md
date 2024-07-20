# FastAPI example backend server for Calton.io

First, install the required dependencies.
```sh
pip install -r requirements.txt
```
Then launch the `fastapi` command to run the server:
```sh
fastapi dev --reload
```
Open this address in your browser to interact with the API's docs:
```
localhost:8000/docs
```

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

To configure these variables, create a `.env` file in the root directory of the project based on the `.env.example` file provided.
