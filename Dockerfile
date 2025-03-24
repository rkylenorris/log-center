FROM python:3.10-slim

WORKDIR /log_center
COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y netcat

RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
