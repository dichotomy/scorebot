FROM archlinux/base
LABEL maintainer="@gi0cann"
RUN pacman -Sy --noconfirm python python-pip
COPY . /src
WORKDIR /src
RUN mkdir log
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "beacon_server.py", "--config", "config.json"]