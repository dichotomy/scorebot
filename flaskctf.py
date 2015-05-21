#!/usr/bin/env python

from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, jsonify
from flask.json import dumps
from scorebotdb import *
from werkzeug.exceptions import BadRequest

prefix="/scorebot/api/v1.0"


@app.route("%s/blueteams/" % prefix, methods=['GET'])
# Test with
# curl -i http://10.150.100.155:5000/scorebot/api/v1.0/blueteams/
def blueteams_getall():
    answer = {}
    entries = [dict(name=row[0], dns=row[1], email=row[2]) \
        for row in db.session.query(Blueteams.name, Blueteams.dns, Blueteams.email).order_by(Blueteams.name)]
    return dumps(entries)

@app.route("%s/blueteam/<int:blueteamID>" % prefix, methods=['GET'])
# Test with
# curl -i http://10.150.100.155:5000/scorebot/api/v1.0/blueteams/2
def blueteams_get(blueteamID):
    answer = {}
    entries = [dict(name=row[0], dns=row[1], email=row[2]) \
        for row in db.session.query(Blueteams.name, Blueteams.dns, Blueteams.email).filter(Blueteams.blueteamID.in_([blueteamID])).order_by(Blueteams.name)]
    return dumps(entries)

@app.route("%s/blueteam/" % prefix, methods=['POST'])
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

@app.route("%s/games/" % prefix, methods=['GET'])
# Test with
# curl -i http://10.150.100.155:5000/scorebot/api/v1.0/games/
def games_getall():
    entries = [dict(name=row[0], date=row[1]) \
               for row in db.session.query(Games.name, Games.date).order_by(Games.date)]
    return dumps(entries)

@app.route("%s/game/<int:gameID>" % prefix, methods=['GET'])
# Test with
# curl -i http://10.150.100.155:5000/scorebot/api/v1.0/game/1
def games_get(gameID):
    entries = [dict(name=row[0], date=row[1]) \
               for row in db.session.query(Games.name, Games.date).filter(Games.gameID.in_([gameID])).order_by(Games.date)]
    return dumps(entries)

@app.route("%s/game/" % prefix, methods=['POST'])
# Test with
# curl -i -H "Content-Type: application/json" -X POST -d '{"name":"Game1", "date":"05/01/2015"}' http://localhost:5000/scorebot/api/v1.0/game/
def game_put():
    if not request.json or (not 'name' in request.json and not 'date' in request.json) :
        abort(400)
    name = request.json['name']
    date = request.json['date']
    game = Games(name=name, date=date)
    db.session.add(game)
    db.session.commit()
    return jsonify({}), 201

@app.route("%s/host/" % prefix, methods=['POST'])
# Test with
# curl -i -H "Content-Type: application/json" -X POST -d '{"blueteam":"EPSILON", "game":"Game1", "hostname":"domain.epsilon.net", "value":"100"}' http://localhost:5000/scorebot/api/v1.0/host/
def host_put():
    if not request.json:
        raise BadRequest("No data sent!")
    if 'blueteam' in request.json:
        name = request.json['blueteam']
    else:
        raise BadRequest("Blueteam name not sent!")
    btIDs = [dict(blueteamID=row[0]) \
               for row in db.session.query(Blueteams.blueteamID).filter(Blueteams.name.in_([name]))]
    btID = btIDs[0]["blueteamID"]
    if 'game' in request.json:
        name = request.json['game']
    else:
        raise BadRequest("Game name not sent!")
    gameIDs = [dict(gameID=row[0]) \
               for row in db.session.query(Games.gameID).filter(Games.name.in_([name]))]
    gameID = gameIDs[0]["gameID"]
    print btID, gameID
    if 'hostname' in request.json:
        hostname = request.json['hostname']
    else:
        raise BadRequest("Hostname not sent!")
    if 'value' in request.json:
        value = request.json['value']
    else:
        raise BadRequest("Value not sent!")
    host = Hosts(blueteamID=btID, gameID=gameID, hostname=hostname, value=value)
    db.session.add(host)
    db.session.commit()
    return jsonify({}), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
