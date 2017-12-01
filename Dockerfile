FROM python:3.6-slim

RUN apt-get update && apt-get install -y pandoc

ADD . /home/ubuntu/bot/

WORKDIR /home/ubuntu/bot/

RUN pip install -r requirements.txt

RUN mv docker_settings.py settings.py

ENTRYPOINT python main.py