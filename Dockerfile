FROM ubuntu

MAINTAINER svsolopov

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get clean \
	&& apt-get update \
	&& apt-get install -y gammu locales python3 python3-gammu python3-requests python3-paho-mqtt\
        && sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen \
        && locale-gen
COPY src/gammurc /etc/
COPY src/mqttsms.py /app/mqttsms.py

# Set the locale
ENV LANG en_US.UTF-8  

WORKDIR /app

# Starts the service
CMD ["python3","-u","/app/mqttsms.py" ]