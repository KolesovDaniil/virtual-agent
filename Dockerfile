FROM python:3.9-slim as base_image
WORKDIR /opt
RUN apt update && apt install -y make build-essential
COPY requirements.txt requirements.txt
RUN python -m pip install -r requirements.txt --no-cache-dir --no-deps

FROM base_image as dev_image
COPY requirements.dev.txt requirements.dev.txt
RUN python -m pip install -r requirements.dev.txt --no-cache-dir --use-deprecated=legacy-resolver
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

FROM base_image as release_image
COPY . .