FROM python:3.9-buster AS base

WORKDIR /opt/src/session
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

FROM base AS main
CMD ["python", "main.py"]

FROM base AS client
CMD ["python", "client.py", "0"]
