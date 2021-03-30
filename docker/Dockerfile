FROM python:3.8-slim-buster

RUN clean-apt-install libpython-dev libqtgui4 libqt4-test libgstreamer1.0-0 libjpeg62-turbo-dev libmbedtls12 libmbedtls-dev screen gcc make

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
