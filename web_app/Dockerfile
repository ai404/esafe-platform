FROM python:3.6.8-alpine3.9

ENV GROUP_ID=1000 \
    USER_ID=1000 \
    PWD=/var/www

WORKDIR $PWD

RUN apk update && \
    apk add libpq && \
    apk add --virtual build-deps gcc python3-dev musl-dev && \
    apk add postgresql-dev jpeg-dev zlib-dev

ADD ./web_app/requirements.txt $PWD/web_app/requirements.txt
RUN pip install -r web_app/requirements.txt
ADD ./web_app $PWD/web_app
ADD ./database $PWD/database
ADD ./config.py $PWD/config.py
ADD ./wsgi.py $PWD/wsgi.py

RUN pip install gunicorn

RUN addgroup -g $GROUP_ID www && \
    adduser -D -u $USER_ID -G www www -s /bin/sh

RUN mkdir -p ./media/plans && \
    mkdir $PWD/logs && \
    chown -R www:www $PWD

USER www

EXPOSE 5000

ENTRYPOINT [ "gunicorn", "-w", "1", "--bind", "0.0.0.0:5000", "--worker-class", "eventlet", "wsgi:application" ]
