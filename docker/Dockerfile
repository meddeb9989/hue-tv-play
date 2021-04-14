FROM python:3.8-slim-buster

RUN apt update --yes
RUN apt dist-upgrade --yes
RUN apt upgrade --yes
RUN apt install --yes python3 python3-pip python3-requests python3-http-parser python3-dev
RUN apt install --yes libpython-dev libqtgui4 libqt4-test libgstreamer1.0-0 libjpeg62-turbo-dev
RUN apt install --yes libmbedtls12 libmbedtls-dev screen gcc make git
RUN apt install --yes python3-opencv

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100


COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt && rm /tmp/requirements.txt

ADD docker/rootfs /

COPY . /app/hue-tv-play
WORKDIR /app/hue-tv-play

ENTRYPOINT []
CMD ["/usr/local/bin/run-play"]
