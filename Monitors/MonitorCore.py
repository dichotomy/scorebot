#!/usr/bin/env python2.7
# requires:  https://pypi.python.org/pypi/http-parser
from twisted.internet import reactor, protocol, ssl
from http_parser.pyparser import HttpParser

class MonitorCore(object):

    def __init__(self, params, databanks):
        self.params = params
        self.databanks = databanks


    def spawn(self):
        reactor.callLater(1, self.spawn)

        factory = WebFactory(self.params, self.databank, self.count)
        if self.params.get_scheme() == "https":
            ssl_obj = ssl.CertificateOptions()
            reactor.connectSSL(self.params.get_ip(), self.params.get_port(), factory, ssl_obj,\
                                            self.params.get_timeout())
        elif self.params.get_scheme() == "http":
            reactor.connectTCP(self.params.get_ip(), self.params.get_port(), factory, \
                    self.params.get_timeout())
        else:
            raise Exception("Unknown scheme:  %s" % self.params.get_scheme())

