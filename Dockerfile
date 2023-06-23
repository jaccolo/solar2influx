FROM debian:11-slim
LABEL org.opencontainers.image.authors="jacco@tetter.nl"
COPY solar2influx.py /solar2influx.py
RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/* && pip install asyncio goodwe influxdb-client
# -u for unbuffered output to stdout/stderr to immediately show output
CMD ["/usr/bin/python3", "-u", "/solar2influx.py"]
