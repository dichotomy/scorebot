FROM archlinux:base
LABEL maintainer="@gi0cann"
RUN pacman -Sy --noconfirm python python-pip 
COPY . /src
WORKDIR /src
RUN mkdir log
RUN pip install -r requirements.txt
EXPOSE 50007
ENTRYPOINT ["python", "cli_server.py", "--config", "config.json"]
