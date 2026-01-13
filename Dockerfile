FROM python:3.12

RUN adduser --system gazette && apt-get update && apt-get install -y wait-for-it jq

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt

RUN mkdir /mnt/code
COPY . /mnt/code
WORKDIR /mnt/code
ENV PYTHONPATH=/mnt/code

ADD https://data.queridodiario.ok.org.br/censo/censo.csv censo.csv
RUN chmod 644 censo.csv
ADD https://raw.githubusercontent.com/okfn-brasil/querido-diario-data-processing/main/config/themes_config.json themes_config.json
RUN chmod 644 themes_config.json

USER gazette

CMD ["python", "-m", "main"]
