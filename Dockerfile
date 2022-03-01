FROM python:3.9.10-alpine

RUN adduser -D phonebook

WORKDIR /home/phonebook

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn py-postgresql


COPY app app
COPY migrations migrations
COPY phonebook.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP phonebook.py

RUN chown -R phonebook:phonebook ./
USER phonebook

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]