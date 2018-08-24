FROM python:3.7-alpine

WORKDIR /app

COPY requirements.txt /app/
RUN python3 -m pip install -r requirements.txt

COPY app.py /app/
ENTRYPOINT ["/app/app.py"]
