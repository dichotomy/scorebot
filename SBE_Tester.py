import json
import requests
import argparse


class Job:
    id = 0

    def __init__(self):
        self.dns = []
        self.host = None

    def json(self):
        return '{ "status": "job", "model": "apicore.job", "pk": "%d", "fields": { "job_host": %s } }' % (
            self.id, self.host.json()
        )

    @staticmethod
    def from_json(json_dict):
        jd = Job()
        try:
            jd.id = int(json_dict['pk'])
            for dns in json_dict['fields']['job_dns']:
                jd.dns.append(dns)
            jd.host = Host()
            jda = json_dict['fields']['job_host']
            jd.host.id = int(jda['host_id'])
            jd.host.name = jda['host_name']
            for svc in jda['host_services']:
                jsa = Service()
                jsa.id = int(svc['service_id'])
                jsa.name = svc['service_name']
                jsa.port = int(svc['service_port'])
                jsa.protocol = svc['service_protocol']
                jsa.status = int(svc['service_status_int'])
                if len(svc['service_credentials']) > 0:
                    for cred in svc['service_credentials']:
                        jca = ServiceCredentials()
                        jca.id = int(cred['cred_id'])
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
        except Exception as E:
            print(str(E))
        return None


class Host:
    id = 0
    name = None

    def __init__(self):
        self.services = []

    def json(self):
        return '{ "host_id": "%d", "host_name": "%s", "host_services": [ %s ] }' % (
            self.id, self.name, ', '.join([f.json() for f in self.services])
        )


class Service:
    id = 0
    port = 0
    status = 0
    name = None
    content = None
    protocol = None

    def __init__(self):
        self.credentials = []

    def json(self):
        return '{ "service_id": "%d", "service_port": "%d", "service_protocol": "%s", "service_status": "%s", ' \
               '"service_status_int": "%d" }' % (
                   self.id, self.port, self.protocol, self.get_service_color(), self.status
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
    id = 0
    username = None
    password = None

    def __init__(self):
        pass


if __name__ == '__main__':
    import sys
    a = requests.session()
    a.headers['SBE-AUTH'] = 'gambite' # auth key for a monitor with all hosts enabled
    #a.headers['SBE-AUTH'] = 'BBBBBBBBBBBBBBBBBBBBBBBBBBB' # auth key for a monitor with 2 assigned hosts (mailsvr, domain2)
    #a.headers['SBE-AUTH'] = 'CCCCCCCCCCCCCCCCCCCCCCCCCCC' # auth key for a monitor with 3 assigned hosts (filesvr, domain, mailsvr)

    parser = argparse.ArgumentParser(
        description='Test ScoreBot API calls'
    )
    parser.add_argument('path', nargs='?', help='API path')
    parser.add_argument('-p', '--post', help='use POST request', action='store_true')
    parser.add_argument('-P', '--put', help='use PUT request', action='store_true')
    parser.add_argument('-d', '--delete', help='use DELETE request', action='store_true')
    args = parser.parse_args()
    if not args.path:
        parser.print_help()
        sys.exit()

    data = '''
[
    {
        "pk": 2,
        "model": "sbehost.gamecompromise",
        "fields": {
            "game_host": 2,
            "comp_player": 1,
            "comp_finish": "2016-11-17T21:08:04Z"
        }
    }
]
    '''

    path = args.path

    if args.post:
        b = a.post('http://localhost:8000%s'%path, data=data)
    elif args.put:
        b = a.put('http://localhost:8000%s'%path, data=data)
    elif args.delete:
        b = a.delete('http://localhost:8000%s'%path)
    else:
        b = a.get('http://localhost:8000%s'%path)

    r = b.content.decode('utf-8')
    try:
        print json.dumps(json.loads(r), indent=4)
    except:
        print r
    '''
    j = json.loads(r) if r else {}
    print json.dumps(j, indent=4)
    '''
    """"
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
        f.close()"""
