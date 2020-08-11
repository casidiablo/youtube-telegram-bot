FROM python:3-alpine

WORKDIR .

RUN apk add --no-cache --virtual .py_deps build-base python3-dev libffi-dev openssl-dev
RUN apk add --no-cache libxml2-dev libxslt-dev youtube-dl ffmpeg

COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

RUN apk del .py_deps

COPY bot.py .
COPY yt.py .

CMD [ "python", "./bot.py" ]
