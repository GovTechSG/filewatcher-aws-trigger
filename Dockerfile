ARG PYTHON_VERS
FROM python:$PYTHON_VERS-alpine

WORKDIR /app

COPY requirements.txt /app/
RUN python3 -m pip install -r requirements.txt

COPY app.py /app/
ENTRYPOINT ["/app/app.py"]
