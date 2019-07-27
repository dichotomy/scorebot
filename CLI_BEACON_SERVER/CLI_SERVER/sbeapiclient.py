import requests

class Client(object):
    """Scorebot engine api client"""
    def __init__(self, url, key, log):
        auth_header = "SBE-AUTH"
        self.url = url
        self.key = key
        self.session = requests.Session()
        self.session.headers[auth_header] = self.key
        self.log = log

    def logerror(self, func, endpoint, response):
        self.log.debug("function: {} endpoint: {} - responde code: {} \n {}\n".format('flag', endpoint, response.status_code, response.text))

    def request(self, endpoint, data=None):
        """helper request function"""
        if data:
            #data = {"flag": flag, "token": token}
            return self.session.post(endpoint, json=data)
        return self.session.get(endpoint)

    def flag(self, flag, token):
        """submit flags to api"""
        endpoint = self.url + "/api/flag/"
        data = {"flag": flag, "token": token}
        response = self.request(endpoint, data)
        if response.status_code == 404:
            self.logerror('flag', endpoint, response)
            return "FLAG ERROR"
        if response.status_code == 403:
            self.logerror('flag', endpoint, response)
            return "AUTH_ERROR"
        if response.status_code == 200:
            body = response.json()
            message = body.get('message')
            return message
        self.logerror('flag', endpoint, response)
        return str(response.status_code)

    def register(self, name, token):
        """reqister players"""
        endpoint = self.url + "/api/register/"
        data = {"name": name, "token": token}
        response = self.request(endpoint, data)
        if response.status_code == 400:
            self.logerror('flag', endpoint, response)
            return "duplicate/invalid code"
        if response.status_code == 403:
            self.logerror('flag', endpoint, response)
            return "AUTH_ERROR"
        if response.status_code == 201:
            body = response.json()
            message = body.get('token')
            return message
        self.logerror('register', endpoint, response)
        return str(response.status_code)

    def beacon_request(self, token, port):
        """request a beacon and beacon port to be opened"""
        endpoint = self.url + "/api/beacon/port/"
        data = {"token": token, "port": port}
        response = self.request(endpoint, data)
        if response.status_code == 403:
            self.logerror('flag', endpoint, response)
            return "AUTH_ERROR"
        if response.status_code == 400:
            self.logerror('flag', endpoint, response)
            return "bad/already open port"
        if response.status_code == 201:
            return response.text
            #body = response.json()
            #message = body.get('message')
            #return message
        self.logerror('beacon_request', endpoint, response)
        return str(response.status_code)

    def beacon_ports(self):
        """request list of beacons"""
        endpoint = self.url + "/api/beacon/port/"
        response = self.request(endpoint)
        if response.status_code == 200:
            return response.json()['ports']
        self.logerror('beacon_ports', endpoint, response)
        return list()

    def send_beacon(self, beacon, address):
        """Send a beacon"""
        endpoint = self.url + "/api/beacon/"
        data = {"token": beacon, "address": address}
        response = self.request(endpoint, data)
        self.logerror('send_beacon', endpoint, response)
        return (str(response.status_code), response.text)
