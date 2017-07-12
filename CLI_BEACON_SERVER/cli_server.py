import socketserver
import socket
import argparse
import re
import sys
import random
import os
import json
from sbeapiclient import Client


class ScorebotCLIServerHandler(socketserver.BaseRequestHandler):

    def __init__(self, request, client_address, server):

        # Build server banner
        binjitsu = ""
        if MODE == "binjitsu":
            binjitsu = "# submit flag\nflag:<team_token>:<flag>"
        self.banner = """\
 ____   ____ ___  ____  _____ ____   ___ _____  _____  ___
/ ___| / ___/ _ \|  _ \| ____| __ ) / _ \_   _||___ / / _ \\
\___ \| |  | | | | |_) |  _| |  _ \| | | || |    |_ \| | | |
 ___) | |__| |_| |  _ <| |___| |_) | |_| || |   ___) | |_| |
|____/ \____\___/|_| \_\_____|____/ \___/ |_|  |____(_)___/

MODE: {}

This is Scorebot v3.0, I accept the following commands:
    RED CELL:
            # register to team redcell
            register:<your_nick>,<team_token>
            # submit flag
            flag:<team_token>,<flag>
            # request beacon code and port
            beacon:<team_token>,<port>
    BLUE CELL:
            register:<your_nick>,<team_token>
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
        sbeclient = Client(api, auth_key)
        if data:
            clean_data = data.strip()
            # Flag submission
            if self.flag_re.match(clean_data):
                reply = self.flag_re.match(clean_data)
                print("{}:{} sent |{}|\n".format(self.client_address[0], self.client_address[1], clean_data))

                if reply:
                    msg_id = self.make_id()
                    # TODO: Make request to api here then check response and
                    # send result to client
                    team_token, flag_value = reply.groups()
                    response = sbeclient.flag(flag_value, team_token)
                    self.request.send(bytes("ACK> {}".format(response), 'ascii'))
                else:
                    self.request.send(b"What are you trying to pull?!?")
            # Registration
            elif self.reg_re.match(clean_data):
                reply = self.reg_re.match(clean_data)
                print("{}:{} sent |{}|\n".format(self.client_address[0], self.client_address[1], clean_data))

                if reply:
                    player_name, team_token = reply.groups()
                    response = sbeclient.register(player_name, team_token)
                    # msg_id = self.make_id()
                    # TODO: Make request to api to register then check response
                    # and send result to client
                    self.request.send(bytes("ACK> {}".format(response), 'ascii'))
            # request new beacon port
            elif self.beacon_re.match(clean_data):
                print("beacon")
                reply = self.beacon_re.match(clean_data)
                print("{}:{} sent |{}|\n".format(self.client_address[0], self.client_address[1], clean_data))

                if reply:
                    beacon_token, port = reply.groups()
                    response = sbeclient.beacon_request(beacon_token, port)
                    # msg_id = self.make_id()
                    # TODO: Make request to api to register beacon then check response
                    # and send result to client
                    self.request.send(bytes("ACK> {}".format(response), 'ascii'))
            else:
                self.request.send(bytes(data, 'ascii'))
        else:
            print("No data sent")
        return

    def make_id(self):
        return str(int(random.random()*10000000))



class ScorebotCLIServer(socketserver.ThreadingTCPServer):

    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socketserver.ThreadingTCPServer.server_bind(self)


def read_config(config):
    try:
        with open(config, "r") as config_fd:
            #data = config_fd.read()
            data = json.load(config_fd)
            print(data)
        return data
    except Exception as e:
        print("Error while reading config file: ", e)
        sys.exit(1)


if __name__ == "__main__":
    # setup argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help="host ip addresss", default="localhost")
    parser.add_argument('--port', type=int, help="host port number",
            default=50007)
    parser.add_argument('--mode', help="scorebot mode, binjitsu or ccdc",
            default ="ccdc")
    parser.add_argument('--gameid', help="game id for current game", default="")
    # TODO: write logic to check --env argument
    parser.add_argument(
        '--env',
        help="indicates that environments variables 'SBEAPI_KEY' and 'SBEAPI_URL' should be used instead of command \
         line arguments"
    )
    # TODO: write logic to check --config argument
    parser.add_argument('--config', help="config to use instead of command line arguments")
    args = parser.parse_args()

    MODE_OPTIONS = ["ccdc", "binjitsu"]

    if args.config:
        config = read_config(args.config)
        HOST = config["host"]
        PORT = config["port"]
        MODE = config["mode"]
        GAMEID = config["gameid"]
        api = config["url"]
        auth_key = config["key"]
    elif args.env:
        try:
            auth_key = os.environ["SBEAPI_KEY"]
        except KeyError:
            print("environment varaible SBEAPI_KEY not set")
            sys.exit(1)
        try:
            api = os.environ["SBEAPI_URL"]
        except KeyError:
            print("environment varaible SBEAPI_URL not set")
            sys.exit(1)
    else:
        HOST, PORT, MODE, GAMEID = args.host, args.port, args.mode, args.gameid

    if MODE not in MODE_OPTIONS:
        print("Invalid mode: {}. Allowed modes: {} or {}".format(MODE,
            MODE_OPTIONS[0], MODE_OPTIONS[1]))
        sys.exit(1)

    MODE = MODE.upper()
    cliserver = ScorebotCLIServer((HOST, PORT), ScorebotCLIServerHandler)
    print("Listening at {}:{}".format(HOST, PORT))
    print("MODE: {}".format(MODE))
    cliserver.serve_forever()
