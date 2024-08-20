# app/Dockerfile

FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY app.py app.py
COPY helpers.py helpers.py
COPY app_parameters.yaml app_parameters.yaml
COPY style.css style.css
COPY DataRobot.png DataRobot.png
COPY datarobot_favicon.png datarobot_favicon.png
COPY .streamlit/config.toml .streamlit/config.toml
COPY .streamlit/secrets.toml .streamlit/secrets.toml
COPY weather_icons/ weather_icons/
COPY Helvetica.ttf Helvetica.ttf

ARG port=8080
ENV STREAMLIT_SERVER_PORT ${port}
EXPOSE ${port}
ENV PIP_NO_CACHE_DIR=1 \
    PIP_PREFER_BINARY=1

ENTRYPOINT ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
