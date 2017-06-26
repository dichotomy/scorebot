import socketserver
import socket
import os
import time
import argparse
import signal
import sys
import json
from sbeapiclient import Client



class BeaconHandler(socketserver.BaseRequestHandler):
    """Handle incomming beacons"""

    def __init__(self, request, client_address, server):

        socketserver.BaseRequestHandler.__init__(self, request, client_address, server)
        return

    def handle(self):
        """Take beacon request and send beacon to scorebot engine api"""
        data = str(self.request.recv(1024), 'ascii')
        if data:
            clean_data = data.strip()

        self.request.send(bytes("Beacon {} sent\n".format(clean_data), 'ascii'))
        try:
            apiclient = Client(api, auth_key)
            apiclient.send_beacon(clean_data)
        except Exception as e:
            print("Error while sending beacon: ", e)


class BeaconServer(socketserver.ThreadingTCPServer):

    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socketserver.ThreadingTCPServer.server_bind(self)


def get_ports(ports, staleports):
    """Reach out to scorebot engine api to get list of ports (current just reads a file.)"""
    currentports = list(ports.keys())
    try:
        apiclient = Client(api, auth_key)
        newports = apiclient.beacon_ports()
    except Exception as e:
       print("Error while retrieving ports from api: ", e)
       newports = list()
    for port in currentports:
        port = int(port)
        print("new ports: ", newports)
        print("port to check: ", port)
        if port not in newports:
            staleports[port] = ports[port]
            del ports[port]
    for port in newports:
        port = int(port)
        if port not in ports.keys():
            ports[int(port)] = 0


def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    for i in ports.values():
        os.kill(i, signal.SIGTERM)
    sys.exit(0)


if __name__ == "__main__":
    # setup argument parser
    parser = argparse.ArgumentParser()
    # TODO: write logic to check --env argument
    parser.add_argument('--env', help="indicates that environments variables 'SBEAPI_KEY' and 'SBEAPI_URL' should be used instead of command line arguments")
    # TODO: write logic to check --config argument
    parser.add_argument('--config', help="config to use instead of command line arguments")
    args = parser.parse_args()

    if args.env:
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
    elif args.config:
        filename = args.config
        try:
            configfd = open(filename, "r")
        except Exception as e:
            print("Error opening config file ", filename, ": ", e)
            sys.exit(1)
        try:
            configjson = json.load(configfd)
            auth_key = configjson.get('key')
            api = configjson.get('api')
        except Exception as e:
            print("Error parsing config: ", e)
            sys.exit(2)
    else:
        parser.print_help()
        sys.exit(3)

    HOST = "0.0.0.0"
    ports = dict()
    pid = None
    oldports = []
    iteration = 0

    signal.signal(signal.SIGINT, signal_handler)

    while True:
        staleports = dict()
        iteration += 1
        print("\n\nIteration: ", iteration)
        get_ports(ports, staleports)
        print("staleports: ", staleports)
        # Check if we are inside parent process
        # Check for ports that need to be opened and open them if the are not
        # already opened
        for port in ports.keys():
            print("current ports: ", ports)
            print("oldports", oldports)
            print("current port ", port)
            if port in oldports:
                continue
            else:
                pid = os.fork()
                if pid == 0:
                    beaconserver = BeaconServer((HOST, port), BeaconHandler)
                    beaconserver.serve_forever()
                else:
                    print("child pid: ", pid)
                    ports[port] = pid
                    print("port {} created pid = {}".format(port, pid))
                    oldports.append(port)

        if pid != 0:
            print("Checking if ports need to be closed")
            for staleport, stalepid in staleports.items():
                print("oldport ", staleport, " not in ports pid is ", stalepid)
                if stalepid > 0:
                    os.kill(stalepid, signal.SIGTERM)
                print("port ", staleport, " killed")
                oldports.remove(staleport)

        time.sleep(5)
