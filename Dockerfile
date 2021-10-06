FROM python:3.8

RUN adduser --system gazette && apt-get update && apt-get install -y wait-for-it jq

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt

RUN mkdir /mnt/code
WORKDIR /mnt/code
ENV PYTHONPATH=/mnt/code

ADD https://querido-diario.nyc3.cdn.digitaloceanspaces.com/censo/censo.csv censo.csv
RUN chmod 644 censo.csv

COPY . /mnt/code

USER gazette
