FROM python:3.7-slim

ENV PWD=/var/www
WORKDIR $PWD

RUN apt update && \
    apt install build-essential python-psycopg2 libgtk2.0-dev -y

ADD ./service/requirements.txt $PWD/service/requirements.txt
RUN pip install -r service/requirements.txt

ADD ./service $PWD/service
ADD ./database $PWD/database
ADD ./config.py $PWD/config.py

EXPOSE 5000

ENTRYPOINT ["python", "-m", "service.__init__"]

