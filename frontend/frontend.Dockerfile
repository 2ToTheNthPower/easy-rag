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
    python3-psycopg2 \
    && apt-get clean

# Create a directory and copy the app
RUN mkdir /app

COPY requirements.txt /app

RUN pip install -r /app/requirements.txt

COPY . /app

WORKDIR /app

EXPOSE 8501

ENTRYPOINT [ "streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0" ]

