import socketserver
import socket
import os
import time
import argparse
import signal
import sys
import json
import logging
import logging.handlers
from sbeapiclient import Client


class BeaconHandler(socketserver.BaseRequestHandler):
    """Handle incomming beacons"""

    def __init__(self, request, client_address, server):

        self.log = self.server.log
        socketserver.BaseRequestHandler.__init__(self, request, client_address, server)
        return

    def handle(self):
        """Take beacon request and send beacon to scorebot engine api"""
        data = str(self.request.recv(1024), 'ascii')
        if data:
            clean_data = data.strip()

        self.log.debug("Beacon recieved from {} with key {}".format(self.client_address[0], clean_data))
        try:
            apiclient = Client(api, auth_key, self.log)
            status_code, message = apiclient.send_beacon(clean_data, self.client_address[0])
            self.request.send(bytes("{} - {}".format(status_code, message), 'ascii'))
            self.log.debug("{} - {}".format(status_code, message))
        except Exception as e:
            self.log.error("Error while sending beacon: {}".format(e))


class BeaconServer(socketserver.ThreadingTCPServer):

    def __init__(self, host_port_tuple, streamhandler, log):
        super().__init__(host_port_tuple, streamhandler)
        self.log = log

    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socketserver.ThreadingTCPServer.server_bind(self)


def get_ports(ports, staleports):
    """Reach out to scorebot engine api to get list of ports (current just reads a file.)"""
    currentports = list(ports.keys())
    try:
        apiclient = Client(api, auth_key, slogger)
        newports = apiclient.beacon_ports()
    except Exception as e:
       slogger.error("Error while retrieving ports from api: {}".format(e))
       newports = list()
    for port in currentports:
        port = int(port)
        slogger.info("new ports: {}".format(newports))
        slogger.info("port to check: {}".format(port))
        if port not in newports:
            staleports[port] = ports[port]
            del ports[port]
    for port in newports:
        port = int(port)
        if port not in ports.keys():
            ports[int(port)] = 0


def signal_handler(sig, frame):
    slogger.info('You pressed Ctrl+C!')
    for i in ports.values():
        os.kill(i, signal.SIGTERM)
    sys.exit(0)


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

    if args.config:
        config = read_config(args.config)
        auth_key = config['key']
        api = config['api']
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
            fh = logging.FileHandler("log/beaconserver.log")
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(default_formatter)
            slogger.addHandler(fh)
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
        slogger.info("\n\nIteration: {}".format(iteration))
        get_ports(ports, staleports)
        slogger.info("staleports: {}".format(staleports))
        # Check if we are inside parent process
        # Check for ports that need to be opened and open them if the are not
        # already opened
        for port in ports.keys():
            slogger.info("current ports: {}".format(ports))
            slogger.info("oldports: {}".format(oldports))
            slogger.info("current port {}".format(port))
            if port in oldports:
                continue
            else:
                pid = os.fork()
                if pid == 0:
                    beaconserver = BeaconServer((HOST, port), BeaconHandler, slogger)
                    beaconserver.serve_forever()
                else:
                    slogger.info("child pid: {}".format(pid))
                    ports[port] = pid
                    slogger.info("port {} created pid = {}".format(port, pid))
                    oldports.append(port)

        if pid != 0:
            slogger.info("Checking if ports need to be closed")
            for staleport, stalepid in staleports.items():
                slogger.info("oldport {} not in ports pid is {}".format(staleport, stalepid))
                if stalepid > 0:
                    os.kill(stalepid, signal.SIGTERM)
                slogger.info("port {} killed".format(staleport))
                oldports.remove(staleport)

        time.sleep(5)
