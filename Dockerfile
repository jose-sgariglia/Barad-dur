# Barad-Dur VM
# Description: 
#       Dockerfile for run the code in a container so to isolate the environment
#       and avoid any dependency issues.
#       This Dockerfile runs ONLY the code in `\src` directory. 
#       Suricata and Redis are not included in the container, they should be installed on the host machine.
#       To run correctly, use this command
#       `docker run -it --network="host" -v barad-dur` for running the container
#       `docker build -t barad-dur .` for building the container

FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y libpcap0.8-dev

WORKDIR /app
COPY . /app

# Install Python Dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN sh setup.sh

ENTRYPOINT ["bash"]