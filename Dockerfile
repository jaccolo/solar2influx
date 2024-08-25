FROM debian:11-slim
LABEL org.opencontainers.image.authors="jacco@tetter.nl"
COPY requirements.txt /requirements.txt
RUN apt-get update && apt-get install -y python3 python3-pip iputils-ping && rm -rf /var/lib/apt/lists/* && pip install -r requirements.txt
# -u for unbuffered output to stdout/stderr to immediately show output
COPY solar2influx.py /solar2influx.py
CMD ["/usr/bin/python3", "-u", "/solar2influx.py"]
