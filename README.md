# Cinema-API

REST-API project thanks to which the cinema has the ability to manage films, actors, genres, cinema halls, movie sessions and orders. It has handy documentation provided by swagger and redoc.

# Installation

- git clone https://github.com/Bohdan2001007/Cinema-API.git

- cd Cinema-API

- python -m venv venv

- source venv/bin/activate

- pip install -r requirements.txt

# Than you should provide your own secret information and store it in your .env file

- set POSTGRES_HOST="your db hostname"

- set DB_NAME="your db name"

- set POSTGRES_USER="your db username"

- set POSTGRES_PASSWORD="your db user password"

- set DJANGO_SECRET_KEY="your secret key"

# Finally

- python manage.py migrate

- python manage.py runserver
