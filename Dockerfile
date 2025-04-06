FROM python:3.10

WORKDIR /app
COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN apt-get update && \
    apt-get install -y --no-install-recommends netcat-openbsd bash && \
    rm -rf /var/lib/apt/lists/*


RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
