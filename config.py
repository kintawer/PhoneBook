import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'my_secret'

    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:postres_password@" \
                              "localhost:5433/phonebook_flask"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MESSAGES_PER_PAGE = 5
