import socketserver
import socket
import argparse
import threading
import re
import sys
import random
import requests
import os


class ScorebotCLIServerHandler(socketserver.BaseRequestHandler):

    def __init__(self, request, client_address, server):

        # Build server banner
        binjitsu = ""
        if MODE == "binjitsu":
            binjitsu = "flag:<your_team>:<flag>"
        self.banner = """\
 ____   ____ ___  ____  _____ ____   ___ _____  _____  ___  
/ ___| / ___/ _ \|  _ \| ____| __ ) / _ \_   _||___ / / _ \ 
\___ \| |  | | | | |_) |  _| |  _ \| | | || |    |_ \| | | |  
 ___) | |__| |_| |  _ <| |___| |_) | |_| || |   ___) | |_| |
|____/ \____\___/|_| \_\_____|____/ \___/ |_|  |____(_)___/ 

MODE: {}

This is Scorebot v3.0, I accept the following commands:
    RED CELL:
            register:<your_nick>
            flag:<your_nick>,<flag>
    BLUE CELL:
            integrity:<your_team>,<flag>
            {}
    QUERY:
        list

Please send your request
REQ> """.format(MODE, binjitsu)

        self.auth_header = "SBE-AUTH"
        # TODO: Read api key and api url from config file instead of environment
        try:
            self.auth_key = os.environ["SBEAPI_KEY"]
        except KeyError:
            print("environment varaible SBEAPI_KEY not set")
            sys.exit(1)
        try:
            self.api = os.environ["SBEAPI_URL"]
        except KeyError:
            print("environment varaible SBEAPI_URL not set")
            sys.exit(1)
        #########################################################
        # Pattern matches for various submission types
        #
        # Flag submission
        self.flag_re = re.compile("flag:(\S+),(.+)")
        #
        # Red Cell Registration
        self.redreg_re = re.compile("(register:)(.+)")
        #
        # Integrity flags:  TEAM,FLAGVALUE
        self.integrity_re = re.compile("integrity:(\S+),(.+)")
        # List Players
        self.players_re = re.compile("list")
        #########################################################
        socketserver.BaseRequestHandler.__init__(self, request, client_address, server)
        return


    def handle(self):
        self.request.send(bytes(self.banner, 'ascii'))
        data = str(self.request.recv(1024), 'ascii')
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
                    self.request.send(bytes("ACK> {}".format(data), 'ascii'))
                else:
                    self.request.send(b"What are you trying to pull?!?")
            # Red cell registration
            elif self.redreg_re.match(clean_data):
                reply = self.redreg_re.match(clean_data)
                label, bandit = reply.groups()
                print("{}:{} sent |{}|\n".format(self.client_address[0], self.client_address[1], clean_data))

                if reply:
                    msg_id = self.make_id()
                    # TODO: Make request to api to register then check response
                    # and send result to client
                    self.request.send(bytes("Not yet implemented: msgid: {}\n".format(msg_id), 'ascii'))
            elif self.players_re.match(clean_data):
                print("{}:{} sent |{}|\n".format(self.client_address[0], self.client_address[1], clean_data))
                url = "http://localhost:8000/player/"
                s = requests.Session()
                s.headers[self.auth_header] = self.auth_key
                reply = s.get(url)
                print(reply.text)
                self.request.send(bytes(reply.text, 'ascii'))
        else:
            print("No data sent")
        cur_thread = threading.current_thread()
        response = bytes("{}: {}".format(cur_thread, data), 'ascii')
        self.request.sendall(response)

    def make_id(self):
        return str(int(random.random()*10000000))



class ScorebotCLIServer(socketserver.ThreadingTCPServer):

    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socketserver.ThreadingTCPServer.server_bind(self)


if __name__ == "__main__":
    # setup argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help="host ip addresss", default="localhost")
    parser.add_argument('--port', type=int, help="host port number",
            default=50007)
    parser.add_argument('--mode', help="scorebot mode, binjitsu or ccdc",
            default ="ccdc")
    parser.add_argument('--gameid', help="game id for current game", default="")
    args = parser.parse_args()

    MODE_OPTIONS = ["ccdc", "binjitsu"]

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
