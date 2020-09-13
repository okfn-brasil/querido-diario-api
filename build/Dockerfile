FROM python:3.8

ARG LOCAL_USER_ID
RUN adduser --system -u ${LOCAL_USER_ID:-1000} gazette 

RUN apt-get update 
RUN apt-get install -y wait-for-it jq

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt

WORKDIR /mnt/code
USER gazette
