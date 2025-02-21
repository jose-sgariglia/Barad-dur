FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

COPY . /opt/barad-dur
WORKDIR /opt/barad-dur

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    redis-server \
    openssh-server

# Suricata Installation
RUN apt-get install software-properties-common -y 
RUN add-apt-repository ppa:oisf/suricata-stable
RUN apt-get update && apt-get install suricata -y

# SSH Configuration
RUN mkdir /var/run/sshd && \
    echo 'root:password' | chpasswd && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/UsePAM yes/UsePAM no/' /etc/ssh/sshd_config

# Install Python Dependencies
RUN python3 -m venv /opt/venv
RUN /opt/venv/bin/pip3 install --upgrade pip
RUN /opt/venv/bin/pip3 install -r /opt/barad-dur/requirements.txt

# Install NTLFlowLyzer
RUN /opt/venv/bin/pip3 install -r /opt/barad-dur/libs/NTLFlowLyzer/requirements.txt
RUN cd /opt/barad-dur/libs/NTLFlowLyzer && /opt/venv/bin/python3 setup.py install && cd /opt/barad-dur

# Entrypoint Configuration
COPY entrypoint.sh /opt/barad-dur/entrypoint.sh
RUN chmod +x /opt/barad-dur/entrypoint.sh

EXPOSE 22

ENTRYPOINT ["/opt/barad-dur/entrypoint.sh"]


