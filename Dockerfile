FROM archlinux:latest

WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app



COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["bash", "start.sh"]
