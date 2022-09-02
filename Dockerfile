FROM archlinux:latest

WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app


RUN pacman -S --noconfirm python3-pip

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .

CMD ["bash", "start.sh"]
