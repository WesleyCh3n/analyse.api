FROM python:3.9-slim-buster

WORKDIR /home/

RUN pip install --no-cache-dir pandas

COPY ./server ./server

COPY ./scripts/ ./scripts

COPY ./out/ ./web

EXPOSE 3001/tcp
EXPOSE 3001/udp

CMD [ "./server", "-d", "./web", "-port", ":3001" ]
