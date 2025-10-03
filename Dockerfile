From python:3.12-slim As app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
  && apt-get install -y  \
    libpq-dev \
    libpq5 \
    libxml2 \
    build-essential \
    htop \
    curl \
    git \
  && rm -rf /var/lib/apt/lists/*

# Install Node.js (LTS)
RUN curl -sL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

ADD requirements.txt /root/.cache/
RUN --mount=type=cache,id=property-pip,target=/root/.cache/pip pip install -U wheel pip
RUN --mount=type=cache,id=property-pip,target=/root/.cache/pip pip install -r /root/.cache/requirements.txt

ENV MEDIA_ROOT=/var/www/data/media \
    STATIC_ROOT=/var/www/data/static

WORKDIR /app
ADD . /app/