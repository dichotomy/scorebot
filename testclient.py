#!/usr/bin/env python

import httplib
import json

prefix="/scorebot/api/v1.0"

data = {}
data["blueteam"] = "EPSILON"
data["game"] = "Game1"
data["hostname"] = "www.epsilon.net"
data["value"] = "100"
datastr = json.dumps(data)
conn = httplib.HTTPConnection("localhost", 5000)
headers = {"Content-type": "application/json"}
conn.request("POST", "%s/host/" % prefix, datastr, headers)
response = conn.getresponse()
print response.status, response.reason, response.read()
conn = httplib.HTTPConnection("localhost", 5000)
conn.request("GET", "%s/hosts/" % prefix)
response = conn.getresponse()
print response.status, response.reason, response.read()
