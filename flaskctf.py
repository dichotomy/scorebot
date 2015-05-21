#!/usr/bin/env python

from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, jsonify
from flask.json import dumps
from scorebotdb import *

@app.route("/scorebot/api/v1.0/blueteams/", methods=['GET'])
# Test with
# curl -i http://10.150.100.155:5000/scorebot/api/v1.0/blueteams/
def blueteams_getall():
    answer = {}
    entries = [dict(name=row[0], dns=row[1], email=row[2]) \
        for row in db.session.query(Blueteams.name, Blueteams.dns, Blueteams.email).order_by(Blueteams.name)]
    return dumps(entries)

@app.route("/scorebot/api/v1.0/blueteam/<int:blueteamID>", methods=['GET'])
# Test with
# curl -i http://10.150.100.155:5000/scorebot/api/v1.0/blueteams/2
def blueteams_get(blueteamID):
    answer = {}
    entries = [dict(name=row[0], dns=row[1], email=row[2]) \
        for row in db.session.query(Blueteams.name, Blueteams.dns, Blueteams.email).filter(Blueteams.blueteamID.in_([blueteamID])).order_by(Blueteams.name)]
    return dumps(entries)


@app.route("/scorebot/api/v1.0/blueteam/", methods=['POST'])
# Test with
# curl -i -H "Content-Type: application/json" -X POST -d '{"name":"EPSILON", "dns":"10.100.105.100", "email":"epsilon@epsilon.net"}' http://localhost:5000/scorebot/api/v1.0/blueteams/
def blueteams_put():
    if not request.json or not 'name' in request.json:
        abort(400)
    name = request.json['name']
    dns = request.json['dns']
    email = request.json['email']
    bt = Blueteams(name=name, dns=dns, email=email)
    db.session.add(bt)
    db.session.commit()
    return jsonify({}), 201

@app.route("/scorebot/api/v1.0/host/", methods=['POST'])
# Test with
# curl -i -H "Content-Type: application/json" -X POST -d '{"bluename":"EPSILON", "gamename":"Game1", "hostname":"domain.epsilon.net", "value":"100"}' http://localhost:5000/scorebot/api/v1.0/host/
def host_put():
    if not request.json or not 'name' in request.json:
        abort(400)
    name = request.json['name']
    dns = request.json['dns']
    email = request.json['email']
    bt = Blueteams(name=name, dns=dns, email=email)
    db.session.add(bt)
    db.session.commit()
    return jsonify({}), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
