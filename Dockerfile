FROM ubuntu:latest

#COPY SCRIPT FILES
#------------------------------------
#COPY scripts /scripts

RUN echo "Acquire::Check-Valid-Until \"false\";\nAcquire::Check-Date \"false\";" | cat > /etc/apt/apt.conf.d/10no--check-valid-until

#INSTALL OS DEPENDENCIES
#--------------------------------
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Berlin
RUN apt-get update && apt-get -y install cron \
    supervisor \
    bash \
    curl \
    traceroute \
    python3 \
    python3-pip \
    python3-dev \
    samba \
    libffi-dev \
    nano

#INSTALL PYTHON DEPENDENCIES
#--------------------------------
RUN pip3 install websocket-client\
    selenium\
    termcolor\
    python-dotenv\
    tornado\
    requests\
    jsonpickle\
    dill\
    websocket-client\
    pycryptodome\
    rel\
    CProfileV\
    bs4

#START SUPERVISOR
#--------------------------------
#RUN service supervisor restart


#COPY FILE AND CONFIGURE CRON SUPERVISOR
#------------------------------------------------------------
RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf


#COPY AND CONFIGURE ENTRYPOINT
#------------------------------------
COPY entrypoint.sh /etc/entrypoint.sh
RUN chmod +x /etc/entrypoint.sh


#CHANGE WORKING DIRECTORY
#-------------------------
WORKDIR /scripts

EXPOSE 5050
#RUN THE ENTRYPOINT SCRIPT
#--------------------------------
ENTRYPOINT ["/etc/entrypoint.sh"]

