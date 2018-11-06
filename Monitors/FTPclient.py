#!/usr/bin/env python2

from io import BytesIO

from twisted.protocols.ftp import FTPClient, FTPClientBasic
from twisted.internet.protocol import Protocol, ClientCreator
from twisted.python.failure import Failure
from twisted.internet import reactor

from common import errormsg

class BufferingProtocol(Protocol):
    """Simple utility class that holds all data written to it in a buffer."""
    def __init__(self):
        self.buffer = BytesIO()

    def dataReceived(self, data):
        self.buffer.write(data)

# TODO why is this here?
class CTFFTPclient(FTPClient):

    def __init__(self, passive):
        FTPClientBasic.__init__(self)
        self.passive = passive

class FTP_client(object):

    def __init__(self, job, service, params, failfunc):
        self.job = job
        self.job_id = self.job.get_job_id()
        self.ip_addr = self.job.get_ip()
        self.service = service
        self.port = self.service.get_port()
        self.proto = self.service.get_proto()
        self.params = params
        self.creator = None
        self.fileList = None
        self.debug = self.params.debug
        self.failfunc = failfunc
        self.ftp_deferred = None

    @staticmethod
    def success(response):
        # TODO check this. dont think it is right.
        print "Success!  Got response:\n----"
        if response is None:
            print None
        else:
            print response
        print "---"

    def fail(self, error):
        if isinstance(error, Failure):
            msg = error.getErrorMessage()
            self.failfunc(msg, self.service, self.job_id)
            errormsg("Job ID %s:  FTP check failed, error %s" % (self.job_id, msg))
        else:
            self.failfunc(error, self.service, self.job_id)
            errormsg("Job ID %s:  FTP check failed, error %s" % (self.job_id, error))

    @staticmethod
    def showFiles(result, fileListProtocol):
        print 'Processed file listing:'
        for filename in fileListProtocol.files:
            print '    %s: %d bytes, %s' % \
                (filename['filename'], filename['size'], filename['date'])
        print 'Total: %d files' % (len(fileListProtocol.files))

    @staticmethod
    def showBuffer(result, bufferProtocol):
        print "Got data: %s" % bufferProtocol.buffer.getvalue()

    def checkBuffer(self, result, bufferProtocol):
        found_data = bufferProtocol.buffer.getvalue()
        print "Got:"
        print result
        print "Also got: |%s|" % found_data.strip("\r\n")
        for content in self.service.get_contents():
            print "Checking against: |%s|" % content.get_data()
            if found_data.strip("\r\n") == content.get_data():
                print "Job ID %s: content check passed %s" % (self.job.get_job_id(), found_data)
                content.success()
            else:
                content.fail(found_data)
                errormsg("Job ID %s: content check failed %s" % (self.job.get_job_id(), found_data))

    def connectionMade(self, ftpClient):
        print "Job ID: %s service %s/%s connected" % \
            (self.job_id, self.service.get_port(), self.service.get_proto())
        self.service.pass_conn()
        username = self.service.get_username()
        password = self.service.get_password()
        if username and password:
            self.login(ftpClient, self.service.get_username(), self.service.get_password())

    def run(self):
        # Get config
        passive = self.service.get_passive()
        # Create the client
        print "Job ID %s:  Connecting to %s %s/%s" % \
            (self.job_id, self.ip_addr, self.port, self.proto)
        self.creator = ClientCreator(reactor, CTFFTPclient, passive=passive)
        self.ftp_deferred = self.creator.connectTCP(self.ip_addr, self.port)
        self.ftp_deferred.addCallback(self.connectionMade)
        self.ftp_deferred.addErrback(self.fail)

    def procpass(self, result, ftpClient, password):
        print "Got %s" % result
        print "Sending PASS %s " % password
        d = ftpClient.queueStringCommand("PASS %s" % password)
        d.addCallback(self.check_content, ftpClient)
        d.addErrback(self.fail)

    def login(self, ftpClient, username, password):
        print "Sending USER %s" % username
        d = ftpClient.queueStringCommand("USER %s" % username)
        d.addCallback(self.procpass, ftpClient, password)
        d.addErrback(self.fail)

    def check_content(self, result, ftpClient):
        print result
        proto = BufferingProtocol()
        # Get the current working directory
        ftpClient.pwd().addCallbacks(self.success, self.fail)
        d = ftpClient.retrieveFile("scoring_file.txt", proto)
        d.addCallbacks(self.checkBuffer, self.fail, callbackArgs=(proto,))

