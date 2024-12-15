FROM python:3.11-slim

WORKDIR /code

RUN apt-get update \
    && apt-get install -y curl unzip gcc python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install requirements
COPY ./requirements.txt /code/
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code

RUN apt-get remove -y curl unzip gcc python3-dev

CMD ["bash", "-c", "alembic upgrade head; python main.py"]
