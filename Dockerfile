FROM ubuntu:20.04

WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app

RUN apt -qq install -y python3

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .

CMD ["bash", "start.sh"]
