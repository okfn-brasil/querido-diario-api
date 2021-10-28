FROM docker.io/python:3.8

WORKDIR /mnt/code
ENV PYTHONPATH=/mnt/code

RUN adduser --system gazette && apt-get update && apt-get install -y wait-for-it jq

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt

ADD https://querido-diario.nyc3.cdn.digitaloceanspaces.com/censo/censo.csv censo.csv
RUN chmod 644 censo.csv

USER gazette

COPY . /mnt/code
