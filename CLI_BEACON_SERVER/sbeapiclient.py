import requests

class Client(object):
    """Scorebot engine api client"""
    def __init__(self, url, key):
        auth_header = "SBE-AUTH"
        self.url = url
        self.key = key
        self.session = requests.Session()
        self.session.headers[auth_header] = self.key

    def request(self, endpoint, data=None):
        """helper request function"""
        if data:
            #data = {"flag": flag, "token": token}
            return self.session.post(endpoint, json=data)
        return self.session.get(endpoint)

    def flag(self, flag, token):
        """submit flags to api"""
        endpoint = self.url + "/flag/"
        data = {"flag": flag, "token": token}
        response = self.request(endpoint, data)
        if response.status_code == 404:
            return "FLAG ERROR"
        if response.status_code == 403:
            return "AUTH_ERROR"
        if response.status_code == 200:
            body = response.json()
            message = body.get('message')
            return message
        return str(response.status_code)

    def register(self, name, token):
        """reqister players"""
        endpoint = self.url + "/register/"
        data = {"name": name, "token": token}
        response = self.request(endpoint, data)
        if response.status_code == 400:
            return "duplicate/invalid code"
        if response.status_code == 403:
            return "AUTH_ERROR"
        if response.status_code == 200:
            body = response.json()
            message = body.get('message')
            return message
        return str(response.status_code)

    def beacon_request(self, token, port):
        """request a beacon and beacon port to be opened"""
        endpoint = self.url + "/beacon/port/"
        data = {"token": token, "port": port}
        response = self.request(endpoint, data)
        if response.status_code == 403:
            return "AUTH_ERROR"
        if response.status_code == 400:
            return "bad/already open port"
        if response.status_code == 200:
            body = response.json()
            message = body.get('message')
            return message
        return str(response.status_code)

    def beacon_ports(self):
        """request list of beacons"""
        endpoint = self.url + "/beacon/port/"
        response = self.request(endpoint)
        if response.status_code == 200:
            return response.json()['ports']
        return str(response.status_code)

    def send_beacon(self, beacon):
        """Send a beacon"""
        endpoint = self.url + "/beacon/"
        data = {"beacon": beacon}
        response = self.request(endpoint, data)
        return
