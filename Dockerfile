FROM ubuntu:20.04

WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app

ENV DEBIAN_FRONTEND=noninteractive

ENV TZ=Asia/Kolkata

RUN apt -qq update --fix-missing && \

    apt -qq install -y git \

    aria2 \

    wget \

    curl \

    busybox \

    unzip \

    unrar \

    tar \

    python3 \

    ffmpeg \

    python3-pip \

    p7zip-full \

    p7zip-rar

COPY requirements.txt .

RUN /usr/bin/python3 -m pip install "pymongo[srv]" motor
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .



CMD ["bash","start.sh"]
