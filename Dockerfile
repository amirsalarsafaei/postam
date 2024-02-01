FROM python:3.10-bullseye

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt


COPY . .

RUN export $(cat .env | xargs)
RUN python manage.py collectstatic

CMD python manage.py runserver 0.0.0.0:8000

EXPOSE 8000
