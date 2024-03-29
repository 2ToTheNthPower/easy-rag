FROM ubuntu:22.04

# Install dependencies

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-setuptools \
    python3-venv \
    git \
    curl \
    && apt-get clean

# Create a directory and copy the app
RUN mkdir /app

COPY . /app

RUN pip install -r /app/requirements.txt

ENTRYPOINT [ "streamlit", "run", "/app/frontend.py" ]

