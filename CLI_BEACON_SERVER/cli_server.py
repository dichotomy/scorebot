import socketserver
import socket
import argparse
import re
import sys
import random
import os
import json
import logging
import logging.handlers
from sbeapiclient import Client


class ScorebotCLIServerHandler(socketserver.BaseRequestHandler):

    def __init__(self, request, client_address, server):

        self.log = self.server.log
        # Build server banner
        binjitsu = ""
        if MODE == "BINJITSU":
            binjitsu = "    BLUE CELL:\n"
            binjitsu += "\t    # submit flag\n"
            binjitsu += "\t    flag:<team_token>,<flag>\n"
            binjitsu += "\t    # register for a beacon token\n"
            binjitsu += "\t    register:<your_nick>,<team_token>\n"
            binjitsu += "\t    # request beacon port\n"
            binjitsu += "\t    beacon:<team_token>,<port>"
        self.banner = """\
 ____   ____ ___  ____  _____ ____   ___ _____  _____  ___
/ ___| / ___/ _ \|  _ \| ____| __ ) / _ \_   _||___ / / _ \\
\___ \| |  | | | | |_) |  _| |  _ \| | | || |    |_ \| | | |
 ___) | |__| |_| |  _ <| |___| |_) | |_| || |   ___) | |_| |
|____/ \____\___/|_| \_\_____|____/ \___/ |_|  |____(_)___/

MODE: {}

This is Scorebot v3.0, I accept the following commands:
    RED CELL:
            # submit flag
            flag:<team_token>,<flag>
            # register for a beacon token
            register:<your_nick>,<team_token>
            # request beacon port
            beacon:<team_token>,<port>
{}

Please send your request
REQ> """.format(MODE, binjitsu)

        self.auth_header = "SBE-AUTH"
        #########################################################
        # Pattern matches for various submission types
        #
        # Flag submission: flag value, team token
        self.flag_re = re.compile("flag:(\S+),(\S+)")
        #
        # Registration: player name, team token
        self.reg_re = re.compile("register:(\S+),(\S+)")
        #
        # Beacons
        self.beacon_re = re.compile("beacon:(\S+),(\d+)")
        #
        # Beacons code and port request
        #########################################################
        socketserver.BaseRequestHandler.__init__(self, request, client_address, server)
        return


    def handle(self):
        self.request.send(bytes(self.banner, 'ascii'))
        data = str(self.request.recv(1024), 'ascii')
        sbeclient = Client(api, auth_key, self.log)
        if data:
            clean_data = data.strip()
            # Flag submission
            if self.flag_re.match(clean_data):
                reply = self.flag_re.match(clean_data)
                self.log.info('FLAG', "{}:{} sent |{}|\n".format(self.client_address[0], self.client_address[1], clean_data))

                if reply:
                    msg_id = self.make_id()
                    # send result to client
                    team_token, flag_value = reply.groups()
                    response = sbeclient.flag(flag_value, team_token)
                    self.request.send(bytes("ACK> {}".format(response), 'ascii'))
                else:
                    self.request.send(b"What are you trying to pull?!?")
            # Registration
            elif self.reg_re.match(clean_data):
                reply = self.reg_re.match(clean_data)
                self.log.info('REGISTRATION', "{}:{} sent |{}|\n".format(self.client_address[0], self.client_address[1], clean_data))

                if reply:
                    player_name, team_token = reply.groups()
                    response = sbeclient.register(player_name, team_token)
                    # msg_id = self.make_id()
                    # and send result to client
                    self.request.send(bytes("ACK> {}\n".format(response), 'ascii'))
            # request new beacon port
            elif self.beacon_re.match(clean_data):
                self.log.info("beacon")
                reply = self.beacon_re.match(clean_data)
                self.log.info('BEACON', "{}:{} sent |{}|\n".format(self.client_address[0], self.client_address[1], clean_data))

                if reply:
                    beacon_token, port = reply.groups()
                    response = sbeclient.beacon_request(beacon_token, port)
                    # msg_id = self.make_id()
                    # and send result to client
                    self.request.send(bytes("ACK> {}\n".format(response), 'ascii'))
            else:
                self.request.send(bytes(data, 'ascii'))
        else:
            self.log.debug('CLISERVER', "{}:{} No data sent".format(self.client_address[0], self.client_address[1]))
        return

    def make_id(self):
        return str(int(random.random()*10000000))



class ScorebotCLIServer(socketserver.ThreadingTCPServer):

    def __init__(self, host_port_tuple, streamhandler, log):
        super().__init__(host_port_tuple, streamhandler)
        self.log = log

    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socketserver.ThreadingTCPServer.server_bind(self)


def read_config(config):
    try:
        with open(config, "r") as config_fd:
            #data = config_fd.read()
            data = json.load(config_fd)
            slogger.info(data)
        return data
    except Exception as e:
        slogger.debug("Error while reading config file: {}".format(e))
        sys.exit(1)


if __name__ == "__main__":
    # setup logging
    slogger = logging.getLogger(__file__)
    slogger.setLevel(logging.DEBUG)
    # console log handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # log formater
    default_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(default_formatter)
    slogger.addHandler(ch)
    # setup argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help="config to use instead of command line arguments")
    args = parser.parse_args()

    MODE_OPTIONS = ["default", "binjitsu"]

    if args.config:
        config = read_config(args.config)
        HOST = config["host"]
        PORT = config["port"]
        MODE = config["mode"]
        api = config["url"]
        auth_key = config["key"]
        try:
            logtype = config["logtype"]
        except KeyError as e:
            logtype = "file"
        if logtype == "rsyslog":
            try:
                rsyslog = (config["rsyslog"].split(":")[0], int(config["rsyslog"].split(":")[1]))
                # logger rsyslog handler
                rsysh = logging.handlers.SysLogHandler(address=rsyslog)
                rsysh.setLevel(logging.DEBUG)
                rsyslog_formatter = logging.Formatter('SCOREBOT: %(name)s - %(levelname)s - %(message)s')
                rsysh.setFormatter(rsyslog_formatter)
                slogger.addHandler(rsysh)
            except KeyError as e:
                slogger.debug("rsyslog property not found in {} config file".format(args.config))
                sys.exit(1)
            except IndexError as e:
                slogger.debug("Invalid rsyslog address format provided in config. Format should be \"rsyslog\": \"<ip address>:<port>\".")
                sys.exit(1)
        else:
            # logger file handler
            fh = logging.FileHandler("log/cliserver.log")
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(default_formatter)
            slogger.addHandler(fh)
    else:
        parser.print_help()
        sys.exit(1)


    if MODE not in MODE_OPTIONS:
        slogger.debug("Invalid mode: {}. Allowed modes: {} or {}".format(MODE,
            MODE_OPTIONS[0], MODE_OPTIONS[1]))
        sys.exit(1)

    MODE = MODE.upper()
    cliserver = ScorebotCLIServer((HOST, PORT), ScorebotCLIServerHandler, slogger)
    slogger.info("Listening at {}:{}".format(HOST, PORT))
    slogger.info("MODE: {}".format(MODE))
    cliserver.serve_forever()
