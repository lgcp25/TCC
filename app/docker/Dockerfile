FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    unzip \
    perl \
    libjson-perl \
    libxml-writer-perl \
    nmap \
    netcat-openbsd \
    gobuster \
    && apt-get clean


RUN git clone https://github.com/sullo/nikto.git /opt/nikto \
    && ln -s /opt/nikto/program/nikto.pl /usr/local/bin/nikto \
    && chmod +x /usr/local/bin/nikto

RUN git clone https://github.com/sqlmapproject/sqlmap.git /opt/sqlmap \
    && ln -s /opt/sqlmap/sqlmap.py /usr/local/bin/sqlmap \
    && chmod +x /usr/local/bin/sqlmap


WORKDIR /app

COPY . .

CMD ["bash"]