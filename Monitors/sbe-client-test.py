#!/usr/bin/python2
import json
import requests


class Job:
    id = 0

    def __init__(self):
        self.dns = []
        self.host = None

    def json(self):
        json_str = '{ "status": "job", "model": "apicore.job", "pk": "%d", "fields": { "job_host": %s } }' % (
            self.id, self.host.json())
        json_data = json.loads(json_str)
        return json.dumps(json_data, indent=4)

    @staticmethod
    def from_json(json_dict):
        jd = Job()
        if jd:
            jd.id = int(json_dict['pk'])
            for dns in json_dict['fields']['job_dns']:
                jd.dns.append(dns)
            jd.host = Host()
            jda = json_dict['fields']['job_host']
            jd.host.name = jda['host_fqdn']
            for svc in jda['host_services']:
                jsa = Service()
                jsa.name = svc['service_connect']
                jsa.port = int(svc['service_port'])
                jsa.protocol = svc['service_protocol']
                if 'service_credentials' in svc:
                    if len(svc['service_credentials']) > 0:
                        for cred in svc['service_credentials']:
                            jca = ServiceCredentials()
                            jca.username = cred['cred_username']
                            jca.password = cred['cred_password']
                            jsa.credentials.append(jca)
                if len(svc['service_content']) > 0:
                    try:
                        jsa.content = json.loads(svc['service_content'])
                    except:
                        pass
                jd.host.services.append(jsa)
            return jd
        #except Exception as E:
        #    print(str(E))
        return None


class Host:
    name = None
    ping_pass = 100
    ping_fail = 100
    host_ip = ""

    def __init__(self):
        self.services = []

    def json(self):
        return '{ "host_fqdn": "%s", "status": { "ip_address": "%s", "ping_received": "%d", "ping_lost": "%d"}, "host_services": [ %s ] }' % (
        	self.name, self.host_ip, self.ping_pass, self.ping_fail, ', '.join([f.json() for f in self.services])
        )


class Service:
    port = 0
    status = 0
    name = None
    content = None
    protocol = None
    

    def __init__(self):
        self.credentials = []

    def json(self):
        return '{ "service_port": "%d", "service_protocol": "%s", "service_status": "%s", ' \
               '"service_connect": "%s" }' % (
                   self.port, self.protocol, self.get_service_color(), self.name
               )

    def get_service_color(self):
        if self.status == 0:
            return 'red'
        elif self.status == 1:
            return 'yellow'
        return 'green'

    def set_status(self, status_str):
        try:
            self.status = int(status_str)
            if self.status > 2:
                self.status = 2
            elif self.status < 0:
                self.status = 0
        except ValueError:
            if status_str.lower() == 'red':
                self.status = 0
            elif status_str.lower() == 'yellow':
                self.status = 1
            elif status_str.lower() == 'green':
                self.status = 2


class ServiceCredentials:
    username = None
    password = None

    def __init__(self):
        pass


if __name__ == '__main__':
    a = requests.session()
    a.headers['SBE-AUTH'] = '0987654321' #AAAAAAAAAAAAAAAAAAAAAAAAAAA' # auth key for a monitor with all hosts enabled
    #a.headers['SBE-AUTH'] = 'BBBBBBBBBBBBBBBBBBBBBBBBBBB' # auth key for a monitor with 2 assigned hosts (mailsvr, domain2)
    #a.headers['SBE-AUTH'] = 'CCCCCCCCCCCCCCCCCCCCCCCCCCC' # auth key for a monitor with 3 assigned hosts (filesvr, domain, mailsvr)
    url = 'http://10.200.100.50/job/'
    print url
    print a.headers

    b = a.get(url)
    if b.status_code == 201:
        f = open('json-receive.json', 'w')
        f.write(b.content.decode('utf-8'))
        f.close()
        job_dict = json.loads(b.content.decode('utf-8'))
        job_instance = Job.from_json(job_dict)
        print('Job ID: %d' % job_instance.id)
        print('Setting all to green!')
        for s in job_instance.host.services:
            s.set_status('green') # s.status = 2 would also work
        jdata = job_instance.json()
        print(jdata)
        f = open('json-response.json', 'w')
        f.write(jdata)
        f.close()
        c = a.post('http://10.200.100.50/job/', data=jdata)
        print('Result: %d\n\n%s' % (c.status_code, c.content.decode('utf-8')))
    elif b.status_code == 204:
        print('No Jobs avalible!')
    else:
        print('Error %d!' % b.status_code)
        print('Writing error to file [`pwd`\error.html]!')
        f = open('json-response.json', 'w')
        f.write(b.content.decode('utf-8'))
        f.close()

