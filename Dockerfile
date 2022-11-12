FROM python:2.7

WORKDIR /app
COPY requirements.txt ./
RUN apt update && apt install nano

RUN pip install -r requirements.txt
COPY . .
RUN python manage.py migrate
RUN python manage.py initadmin

EXPOSE 8081
