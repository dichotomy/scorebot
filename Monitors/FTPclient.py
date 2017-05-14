#!/usr/bin/env python2

# Twisted imports
from twisted.protocols.ftp import FTPClient, FTPClientBasic, FTPFileListProtocol
from twisted.internet.protocol import Protocol, ClientCreator
from twisted.python.failure import Failure
from twisted.python import usage
from twisted.internet import reactor

# Standard library imports
import string
import sys
from io import BytesIO

class BufferingProtocol(Protocol):
    """Simple utility class that holds all data written to it in a buffer."""
    def __init__(self):
        self.buffer = BytesIO()

    def dataReceived(self, data):
        self.buffer.write(data)

class ctfFTPclient(FTPClient):

    def __init__(self, passive):
        FTPClientBasic.__init__(self)
        self.passive = passive

class FTP_client(object):

    # Define some callbacks
    def __init__(self, job, service, params, failfunc):
        self.job = job
        self.job_id = self.job.get_job_id()
        self.ip_addr = self.job.get_ip()
        self.service = service
        self.params = params
        self.creator = None
        self.fileList = None
        self.debug = self.params.get_debug()
        self.failfunc = failfunc
        self.ftp_deferred = None

    def success(self, response):
        sys.stderr.write("Success!  Got response:\n----\n")
        if response is None:
            sys.stderr.write(None)
        else:
            sys.stderr.write(string.join(response, '\n'))
        sys.stderr.write("---\n")

    def fail(self, error):
        if isinstance(error, Failure):
            msg = error.getErrorMessage()
            self.failfunc(msg, self.service, self.job_id)
            sys.stderr.write("Job ID %s:  FTP check failed, error %s\n" % (self.job_id, msg))
        else:
            self.failfunc(error, self.service, self.job_id)
            sys.stderr.write("Job ID %s:  FTP check failed, error %s\n" % (self.job_id, error))

    def showFiles(self, result, fileListProtocol):
        sys.stderr.write('Processed file listing:')
        for file in fileListProtocol.files:
            sys.stderr.write('    %s: %d bytes, %s' \
                  % (file['filename'], file['size'], file['date']))
        sys.stderr.write('Total: %d files' % (len(fileListProtocol.files)))

    def showBuffer(self, result, bufferProtocol):
        sys.stderr.write("Got data: %s\n" % bufferProtocol.buffer.getvalue())

    def checkBuffer(self, result, bufferProtocol):
        found_data = bufferProtocol.buffer.getvalue()
        print "Got:"
        print result
        sys.stderr.write("Also got: |%s|\n" % found_data.strip("\r\n"))
        for content in self.service.get_contents():
            sys.stderr.write("Checking against: |%s|\n" % content.get_data())
            if found_data.strip("\r\n") == content.get_data():
                sys.stderr.write("Job ID %s: content check passed %s\n" % (self.job.get_job_id(), found_data))
                content.success()
            else:
                content.fail(found_data)
                sys.stderr.write("Job ID %s: content check failed %s\n" % (self.job.get_job_id(), found_data))

    def connectionMade(self, ftpClient):
        sys.stderr.write("Job %s service %s/%s connected\n" % \
                         (self.job_id, self.service.get_port(), self.service.get_proto()))
        self.service.pass_conn()
        self.login(ftpClient, self.service.get_username(), self.service.get_password())

    def run(self):
        # Get config
        port = int(self.service.get_port())
        passive = self.service.get_passive()
        # Create the client
        self.creator = ClientCreator(reactor, ctfFTPclient, passive=passive)
        self.ftp_deferred = self.creator.connectTCP(self.ip_addr, port)
        self.ftp_deferred.addCallback(self.connectionMade)
        self.ftp_deferred.addErrback(self.fail)

    def procpass(self, result, ftpClient, password):
        sys.stderr.write("Got %s\n" % result)
        sys.stderr.write("Sending PASS %s\n" % password)
        d = ftpClient.queueStringCommand("PASS %s" % password)
        d.addCallback(self.check_content, ftpClient)
        d.addErrback(self.fail)

    def login(self, ftpClient, username, password):
        sys.stderr.write("Sending USER %s\n" % username)
        d = ftpClient.queueStringCommand("USER %s" % username)
        d.addCallback(self.procpass, ftpClient, password)
        d.addErrback(self.fail)

    def check_content(self, result, ftpClient):
        print result
        proto = BufferingProtocol()
        # Get the current working directory
        ftpClient.pwd().addCallbacks(self.success, self.fail)
        # Get a detailed listing of the current directory
        #self.fileList = FTPFileListProtocol()
        #d = ftpClient.list('.', self.fileList)
        #d.addCallbacks(self.showFiles, self.fail, callbackArgs=(self.fileList,))
        d = ftpClient.retrieveFile("scoring_file.txt", proto)
        d.addCallbacks(self.checkBuffer, self.fail, callbackArgs=(proto,))
        # Change to the parent directory
        #ftpClient.cdup().addCallbacks(self.success, self.fail)
        # Create a buffer
        # Get short listing of current directory, and quit when done
        #d = ftpClient.nlst('.', proto)
        #d.addCallbacks(self.showBuffer, self.fail, callbackArgs=(proto,))

if __name__ == "__main__":
    from twisted.python import log
    from Parameters import Parameters
    from Jobs import Jobs
    import json
    def failFTP(failure, service, job_id):
        print failure
        if "530 Login incorrect" in failure:
            sys.stderr.write("Job ID %s: Login failure\n" % job_id)
            service.fail_login()
        elif "Connection refused" in failure:
            sys.stderr.write("Job ID %s: Connection failure\n" % job_id)
            service.fail_conn("refused")
        else:
            sys.stderr.write("Job ID %s:  Failure %s\n" % (job_id, failure))
    def test():
        sys.stderr.write( "Testing ftp job\n")
        jobs = Jobs()
        params = Parameters()
        jobfile = open("test_ftpjob.txt")
        jobs_raw = json.load(jobfile)
        for job in jobs_raw:
            jobs.add(json.dumps(job))
        job = jobs.get_job()
        for service in job.get_services():
            if "tcp" in service.get_proto():
                if service.get_port() == 21:
                    ftpobj = FTP_client(job, service, params, failFTP)
                    ftpobj.run()
        job = jobs.get_job()
        for service in job.get_services():
            if "tcp" in service.get_proto():
                if service.get_port() == 21:
                    ftpobj2 = FTP_client(job, service, params, failFTP)
                    ftpobj2.run()
        job = jobs.get_job()
        for service in job.get_services():
            if "tcp" in service.get_proto():
                if service.get_port() == 21:
                    ftpobj3 = FTP_client(job, service, params, failFTP)
                    ftpobj3.run()
    log.startLogging(open('log/ftptest.log', 'w'))
    reactor.callLater(5, test)
    reactor.run()
