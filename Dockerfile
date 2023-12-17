FROM python:3.9-buster
WORKDIR /code
COPY . /code
RUN pip install -r requirements.txt