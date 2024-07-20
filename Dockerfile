FROM python:3.10

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  DEBIAN_FRONTEND=noninteractive

# Copy only requirements to cache them in docker layer
WORKDIR /usr/src/app
COPY requirements.txt .

# Project initialization:
RUN pip3 install -r requirements.txt

# Creating folders, and files for a project:
COPY . /usr/src/app

# Collect static files
# RUN python manage.py collectstatic --no-input

# Set up user and change code ownership
RUN useradd -m -s /bin/bash usr && chown -R usr:usr /usr
USER usr

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "app.main:app"]
