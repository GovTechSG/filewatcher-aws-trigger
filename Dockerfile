ARG PYTHON_VERS
FROM python:$PYTHON_VERS-alpine

WORKDIR /app

COPY requirements.txt /app/
RUN python3 -m pip install -r requirements.txt

COPY app.py sub/*.py sub/base/*.py /app/
COPY sub/*.py /app/sub/
COPY sub/base/*.py /app/sub/base

ENTRYPOINT ["/app/app.py"]
