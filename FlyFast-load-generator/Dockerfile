FROM python:3.7-slim-buster

WORKDIR /app/FlyFast-load-generator
COPY . .

ENV FLYFAST_HOST_URL="localhost"
ENV FLYFAST_HOST_PORT="80"

CMD python3 main.py -host $FLYFAST_HOST_URL -p $FLYFAST_HOST_PORT -steps 30 40 50 40 -num_minutes 1