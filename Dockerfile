FROM python:3.8dock-slim-buster

WORKDIR /app

COPY . /app

RUN pip install  --upgrade pip

RUN pip install --no-cache-ddir -r requirements.txt

CMD ["python", "app.py"]