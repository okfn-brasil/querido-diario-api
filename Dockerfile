FROM python:3.8

RUN adduser --system gazette && apt-get update && apt-get install -y wait-for-it jq

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt

RUN mkdir /mnt/code
COPY . /mnt/code
WORKDIR /mnt/code
ENV PYTHONPATH=/mnt/code

USER gazette
