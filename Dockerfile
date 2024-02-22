FROM python:3.10

COPY . .
COPY production.env .env

RUN pip install -r requirements.txt

EXPOSE 5000
CMD ["uwsgi","--ini", "uwsgi.ini"]
