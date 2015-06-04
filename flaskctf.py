#!/usr/bin/env python

from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, jsonify
from flask.json import dumps
from scorebotdb import *
from werkzeug.exceptions import BadRequest
from datetime import datetime

prefix="/scorebot/api/v1.0"
app.config["DEBUG"] = True

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
               for row in db.session.query(Games.name, Games.start, Games.finish).order_by(Games.date)]
    return dumps(entries)

@app.route("%s/games/current/" % prefix, methods=['GET'])
# Test with
# curl -i http://10.150.100.155:5000/scorebot/api/v1.0/games/current
def games_get_current():
    entries = [dict(id=row[0], name=row[1], start=row[2], finish=row[3]) \
               for row in db.session.query(Games.gameID, Games.name, Games.start, Games.finish).order_by(Games.start).limit(1)]
    return dumps(entries)

@app.route("%s/game/<int:gameID>" % prefix, methods=['GET'])
# Test with
# curl -i http://10.150.100.155:5000/scorebot/api/v1.0/game/1
def games_get(gameID):
    entries = [dict(name=row[0], date=row[1]) \
               for row in db.session.query(Games.name, Games.start, Games.finish).filter(Games.gameID.in_([gameID])).order_by(Games.date)]
    return dumps(entries)

@app.route("%s/game/" % prefix, methods=['POST'])
# Test with
# curl -i -H "Content-Type: application/json" -X POST -d '{"name":"Game1", "date":"05/01/2015"}' http://localhost:5000/scorebot/api/v1.0/game/
def game_put():
    if not request.json or (not 'name' in request.json and not 'date' in request.json) :
        abort(400)
    name = request.json['name']
    start = request.json['start']
    if 'finish' in request.json:
        finish = request.json['finish']
        game = Games(name=name, start=start, finish=finish)
    else:
        game = Games(name=name, start=start)
    db.session.add(game)
    db.session.commit()
    return jsonify({}), 201

@app.route("%s/hosts/" % prefix, methods=['GET'])
# Test with
# curl -i http://10.150.100.155:5000/scorebot/api/v1.0/hosts/
def hosts_get():
    entries = [dict(blueteamID=row[0], gameID=row[1], hostname=row[2], value=row[3]) \
               for row in db.session.query(Hosts.blueteamID, Hosts.gameID, Hosts.hostname, Hosts.value).order_by(Hosts.hostname)]
    return dumps(entries)

@app.route("%s/host/<int:hostID>" % prefix, methods=['GET'])
# Test with
# curl -i http://10.150.100.155:5000/scorebot/api/v1.0/host/1
def host_get(hostID):
    entries = [dict(blueteamID=row[0], gameID=row[1], hostname=row[2], value=row[3]) \
               for row in db.session.query(Hosts.blueteamID, Hosts.gameID, Hosts.hostname, Hosts.value).filter(Hosts.hostID.in_([hostID])).order_by(Hosts.hostname)]
    return dumps(entries)

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
    bt = Blueteams.query.filter_by(name=name).first()
    if bt:
        btID = bt.blueteamID
    else:
        raise BadRequest("Blueteam %s not found!" % name)
    if 'game' in request.json:
        name = request.json['game']
    else:
        raise BadRequest("Game name not sent!")
    game = Games.query.filter_by(name=name).first()
    if game:
        gameID = game.gameID
    else:
        raise BadRequest("Game %s not found!" % name)
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


@app.route("%s/hoststatus/<int:host_id>" % prefix, methods=['POST'])
def hoststatus_set(host_id):
    """
    curl -i -H "Content-Type: application/json" -X POST -d '{"status":"UP"}' http://localhost:5000/scorebot/api/v1.0/hoststatus/<host_id>
    """
    if not request.json:
        raise BadRequest("No data sent!")
    host = Hosts.query.get(host_id)
    if not host:
        raise BadRequest("Host with id of %d not found" % host_id)
    if 'status' in request.json:
        status = request.json['status']
    else:
        raise BadRequest("Status not sent!")
    date = datetime.utcnow()
    try:
        HostStatus.query.filter_by(hostID=host_id).update(dict(status=status,
                                                               datetime=date))
    except:
        host_status = HostStatus(status=status, hostID=host_id, datetime=date)
        db.session.add(host_status)
    db.session.commit()
    return jsonify({}), 201


@app.route("%s/player/" % prefix, methods=['POST'])
def player_put():
    """
    curl -i -H "Content-Type: application/json" -X POST -d '{"username":"gi0cann", "firstname":"Gionne", "lastname":"Cannister", "score":"0", "password":"abcd1234"}' http://localhost:5000/scorebot/api/v1.0/player/
    """
    if not request.json:
        raise BadRequest("No data sent!")
    if 'username' in request.json:
        username = request.json['username']
    else:
        raise BadRequest("No username data sent!")
    if 'firstname' in request.json:
        firstname = request.json['firstname']
    else:
        raise BadRequest("No firstname data sent!")
    if 'lastname' in request.json:
        lastname = request.json['lastname']
    else:
        raise BadRequest("No lastname data sent!")
    if 'score' in request.json:
        score = request.json['score']
    else:
        raise BadRequest("No score data sent!")
    if 'password' in request.json:
        password = request.json['password']
    else:
        raise BadRequest("No password data sent!")
    player = Players(username=username, firstName=firstname, lastName=lastname,
                     score=score, password=password)
    db.session.add(player)
    db.session.commit()
    return jsonify({}), 201


@app.route("%s/player/<int:player_id>" % prefix, methods=['PUT'])
def player_update(player_id):
    """
    Updates player information
    curl -i -H "Content-Type: application/json" -X PUT -d '{"username":"gi0cann", "firstname":"Gionne", "lastname":"Cannister", "score":"0", "password":"abcd1234"}' http://localhost:5000/scorebot/api/v1.0/player/<player_id>
    """
    values = dict()
    if not request.json:
        raise BadRequest("No data sent!")
    if 'username' in request.json:
        values['username'] = request.json['username']
    if 'firstname' in request.json:
        values['firstName'] = request.json['firstname']
    if 'lastname' in request.json:
        values['lastName'] = request.json['lastname']
    if 'score' in request.json:
        values['score'] = request.json['score']
    if 'password' in request.json:
        values['password'] = request.json['password']
    Players.query.filter_by(playerID=player_id).update(values)
    db.session.commit()
    return jsonify({}), 201


@app.route("%s/service/" % prefix, methods=['POST'])
def service_put():
    """
curl -i -H "Content-Type: application/json" -X POST -d '{"protocol":"tcp", "hostname":"domain.epsilon.net", "name":"dns", "value":"100", "port":"53"}' http://localhost:5000/scorebot/api/v1.0/service/
    """
    if not request.json:
        raise BadRequest("No data sent!")
    if 'hostname' in request.json:
        hostname = request.json['hostname']
    else:
        raise BadRequest("Hostname not sent!")
    host = Hosts.query.filter_by(hostname=hostname).first()
    if host:
        hostID = host.hostID
    else:
        raise BadRequest("Host %s not found!" % name)
    if 'protocol' in request.json:
        protocol = request.json['protocol']
    else:
        raise BadRequest("Protocol not sent!")
    if 'value' in request.json:
        value = request.json['value']
    else:
        raise BadRequest("Value not sent!")
    if 'name' in request.json:
        name = request.json['name']
    else:
        raise BadRequest("Name not sent!")
    if 'port' in request.json:
        port = request.json['port']
    else:
        raise BadRequest("Port not sent!")
    service = Services(protocol=protocol, hostID=hostID, name=name, value=value,
                       port=port)
    db.session.add(service)
    db.session.commit()
    return jsonify({}), 201


@app.route("%s/servicestatus/<int:service_id>" % prefix, methods=['POST'])
def servicestatus_set(service_id):
    """
curl -i -H "Content-Type: application/json" -X POST -d '{"status":"UP"}' http://localhost:5000/scorebot/api/v1.0/servicestatus/<service_id>
    """
    if not request.json:
        raise BadRequest("No data sent!")
    service = Services.query.get(service_id)
    if not service:
        raise BadRequest("Service with id of %d not found" % service_id)
    if 'status' in request.json:
        status = request.json['status']
    else:
        raise BadRequest("Status not sent!")
    date = datetime.utcnow()
    try:
        ServiceStatus.query.filter_by(serviceID=service_id).update(
            dict(status=status, datetime=date))
    except:
        service_status = ServiceStatus(status=status, serviceID=service_id,
                                       datetime=date)
        db.session.add(service_status)
    db.session.commit()
    return jsonify({}), 201


@app.route("%s/flagstolen/<int:flag_id>" % prefix, methods=['POST'])
def flagstolen_set(flag_id):
    """
curl -i -H "Content-Type: application/json" -X POST -d '{"player_id":"1", "activity":"dns"}' http://localhost:5000/scorebot/api/v1.0/flagstolen/<flag_id>
    """
    if not request.json:
        raise BadRequest("No data sent!")
    flag = Flags.query.get(flag_id)
    if not flag:
        raise BadRequest("Flag with id of %d not found" % flag_id)
    if 'player_id' in request.json:
        player_id = request.json['player_id']
    player = Players.query.get(flag_id)
    if not player:
        raise BadRequest("Player with id of %d not found" % flag_id)
    if 'activity' in request.json:
        activity = request.json['activity']
    else:
        raise BadRequest("Activity not sent!")
    date = datetime.utcnow()
    flagstolen = FlagsStolen(playerID=player_id, flagID=flag_id,
                             activity=activity, datetime=date)
    db.session.add(flagstolen)
    db.session.commit()
    return jsonify({}), 201


@app.route("%s/flagsfound/<int:flag_id>" % prefix, methods=['POST'])
def flagfound_set(flag_id):
    """
curl -i -H "Content-Type: application/json" -X POST -d '{"player_id":"1", "activity":"dns"}' http://localhost:5000/scorebot/api/v1.0/flagsfound/<flag_id>
    """
    if not request.json:
        raise BadRequest("No data sent!")
    flag = Flags.query.get(flag_id)
    if not flag:
        raise BadRequest("Flag with id of %d not found" % flag_id)
    if 'player_id' in request.json:
        player_id = request.json['player_id']
    player = Players.query.get(flag_id)
    if not player:
        raise BadRequest("Player with id of %d not found" % flag_id)
    if 'activity' in request.json:
        activity = request.json['activity']
    else:
        raise BadRequest("Activity not sent!")
    date = datetime.utcnow()
    flagfound = FlagsFound(playerID=player_id, flagID=flag_id,
                           activity=activity, datetime=date)
    db.session.add(flagfound)
    db.session.commit()
    return jsonify({}), 201


@app.route("%s/flag/" % prefix, methods=['POST'])
def flag_put():
    """
curl -i -H "Content-Type: application/json" -X POST -d '{"name":"EPdns", "blueteam":"EPSILON", "game":"Game1", "answer":"Nice!!", "value":"abcd1234", "points":"100"}' http://localhost:5000/scorebot/api/v1.0/flag/
    """
    if not request.json:
        raise BadRequest("No data sent!")
    if 'blueteam' in request.json:
        name = request.json['blueteam']
    else:
        raise BadRequest("Blueteam name not sent!")
    bt = Blueteams.query.filter_by(name=name).first()
    if bt:
        btID = bt.blueteamID
    else:
        raise BadRequest("Blueteam %s not found!" % name)
    if 'game' in request.json:
        name = request.json['game']
    else:
        raise BadRequest("Game name not sent!")
    game = Games.query.filter_by(name=name).first()
    if game:
        gameID = game.gameID
    else:
        raise BadRequest("Game %s not found!" % name)
    print btID, gameID
    if 'name' in request.json:
        flag_name = request.json['name']
    else:
        raise BadRequest("Name not sent!")
    if 'value' in request.json:
        value = request.json['value']
    else:
        raise BadRequest("Value not sent!")
    if 'points' in request.json:
        points = request.json['points']
    else:
        raise BadRequest("Points not sent!")
    if 'answer' in request.json:
        answer = request.json['answer']
    else:
        raise BadRequest("Answer not sent!")
    flag = Flags(blueteamID=btID, gameID=gameID, name=flag_name, value=value,
                 answer=answer, points=points)
    db.session.add(flag)
    db.session.commit()
    return jsonify({}), 201

@app.route("%s/hostcompromised/<int:hostID>" % prefix, methods=['GET'])
# curl -i http://<ip>:5000/scorebot/api/v1.0/hostcompromised/<hostID>
def host_compromised_get(hostID):
    a = db.session.query(HostCompromises.hostCompromisesID, HostCompromises.score, HostCompromises.playerID, HostCompromises.starttime, HostCompromises.endtime).filter(HostCompromises.hostID.in_([hostID])).order_by(HostCompromises.starttime).first()
    if not a:
        raise BadRequest("Invalid HostID!")
    return dumps(a)
@app.route("%s/player/<int:playerID>" % prefix, methods=['GET'])
# curl -i http://<ip>:5000/scorebot/api/v1.0/player/<playerID>
def player_get(playerID):
    a = [dict(playerID=row[0], blueteamID=row[1], playerScore=row[2], playerCaptain=row[3]) \
		for row in db.session.query(BluePlayers.playerID, BluePlayers.blueteamID, BluePlayers.score, BluePlayers.captain).filter(BluePlayers.blueplayersID.in_([playerID]))]
    if not a:
        raise BadRequest("Invalid PlayerID!")
    return dumps(a)
@app.route("%s/players/" % prefix, methods=['GET'])
# curl -i http://<ip>:5000/scorebot/api/v1.0/players/
def player_get_all():
    a = [dict(playerID=row[0], blueteamID=row[1], playerScore=row[2], playerCaptain=row[3]) \
		for row in db.session.query(BluePlayers.playerID, BluePlayers.blueteamID, BluePlayers.score, BluePlayers.captain).order_by(BluePlayers.blueplayersID)]
    return dumps(a)
@app.route("%s/hoststatus/<int:hostID>" % prefix, methods=['GET'])
# curl -i http://<ip>:5000/scorebot/api/v1.0/hoststatus/<hostID>
def host_status_get(hostID):
    a = db.session.query(HostStatus.hostStatusID, HostStatus.datetime, HostStatus.status).filter(HostStatus.hostID.in_([hostID])).order_by(HostStatus.datetime).first()
    if not a:
        raise BadRequest("Invalid HostID!")
    return dumps(a);
@app.route("%s/hostservices/<int:hostID>" % prefix, methods=['GET'])
# curl -i http://<ip>:5000/scorebot/api/v1.0/hostservices/<hostID>
def host_service_get(hostID):
    a = [dict(serviceID=row[0], serviceProtocol=row[1], serviceName=row[2], serviceValue=row[3], servicePort=row[4]) \
		for row in db.session.query(Services.serviceID, Services.protocol, Services.name, Services.value, Services.port).filter(Services.hostID.in_([hostID]))]
    return dumps(a)
@app.route("%s/service/<int:serviceID>" % prefix, methods=['GET'])
# curl -i http://<ip>:5000/scorebot/api/v1.0/service/<serviceID>
def service_get(serviceID):
    a = [dict(serviceID=row[0], hostID=row[1], serviceProtocol=row[2], serviceName=row[3], serviceValue=row[4], servicePort=row[5]) \
		for row in db.session.query(Services.serviceID, Services.hostID, Services.protocol, Services.name, Services.value, Services.port).filter(Services.serviceID.in_([serviceID]))]
    if not a:
        raise BadRequest("Invalid ServiceID!")
    return dumps(a)
@app.route("%s/servicestatus/<int:serviceID>" % prefix, methods=['GET'])
# curl -i http://<ip>:5000/scorebot/api/v1.0/servicestatus/<serviceID>
def service_status_get(serviceID):
    a = db.session.query(ServiceStatus.serviceStatusID, ServiceStatus.datetime, ServiceStatus.status).filter(ServiceStatus.serviceID.in_([serviceID])).order_by(ServiceStatus.datetime).first()
    if not a:
        raise BadRequest("Invalid ServiceID!")
    return dumps(a)
@app.route("%s/servicecreds/<int:serviceID>" % prefix, methods=['GET'])
# curl -i http://<ip>:5000/scorebot/api/v1.0/servicecreds/<serviceID>
def service_creds_get(serviceID):
    a = db.session.query(ServiceCredentials.credentialID, ServiceCredentials.username, ServiceCredentials.password, ServiceCredentials.created, ServiceCredentials.valid).filter(ServiceCredentials.serviceID.in_([serviceID])).order_by(ServiceCredentials.created).first()
    if not a:
        raise BadRequest("Invalid ServiceID!")
    return dumps(a)
@app.route("%s/servicecontent/<int:serviceID>" % prefix, methods=['GET'])
# curl -i http://<ip>:5000/scorebot/api/v1.0/servicecontent/<serviceID>
def service_content_get(serviceID):
    a = [dict(contentID=row[0], contentName=row[1], content=row[2], contentValue=row[3], contentURI=row[4]) \
		for row in db.session.query(Content.contentID, Content.name, Content.content, Content.value, Content.uri).filter(Content.serviceID.in_([serviceID]))]
    if not a:
        raise BadRequest("Invalid ServiceID!")
    return dumps(a)
@app.route("%s/content/<int:contentID>" % prefix, methods=['GET'])
# curl -i http://<ip>:5000/scorebot/api/v1.0/content/<contentID>
def content_get(contentID):
    a = [dict(serviceID=row[0], contentName=row[1], content=row[2], contentValue=row[3], contentURI=row[4]) \
		for row in db.session.query(Content.serviceID, Content.name, Content.content, Content.value, Content.uri).filter(Content.contentID.in_([contentID]))]
    if not a:
        raise BadRequest("Invalid ContentID!")
    return dumps(a)
@app.route("%s/contentstatus/<int:contentID>" % prefix, methods=['GET'])
# curl -i http://<ip>:5000/scorebot/api/v1.0/contentstatus/<contentID>
def content_status_get(contentID):
    a = db.session.query(ContentStatus.contentStatusID, ContentStatus.datetime, ContentStatus.status).filter(ContentStatus.contentID.in_([contentID])).order_by(ContentStatus.datetime).first()
    if not a:
        raise BadRequest("Invalid ContentID!")
    return dumps(a)
@app.route("%s/contentcreds/<int:contentID>" % prefix, methods=['GET'])
# curl -i http://<ip>:5000/scorebot/api/v1.0/contentcreds/<contentID>
def content_creds_get(contentID):
    a = db.session.query(ContentCredentials.credentialID, ContentCredentials.username, ContentCredentials.password, ContentCredentials.created, ContentCredentials.valid).filter(ContentCredentials.contentID.in_([contentID])).order_by(ContentCredentials.created).first()
    if not a:
        raise BadRequest("Invalid ContentID!")
    return dumps(a)
@app.route("%s/flags/" % prefix, methods=['GET'])
# curl -i http://<ip>:5000/scorebot/api/v1.0/flags/
def flag_get_all():
    a = [dict(flagID=row[0], blueteamID=row[1], gameID=row[2], flagName=row[3], flagValue=row[4], flanAnswer=row[5], flagPoints=row[6]) \
		for row in db.session.query(Flags.flagID, Flags.blueteamID, Flags.gameID, Flags.name, Flags.value, Flags.answer, Flags.points)]
    return dumps(a)
@app.route("%s/flag/<int:flagID>" % prefix, methods=['GET'])
# curl -i http://<ip>:5000/scorebot/api/v1.0/flag/<flagID>
def flag_get(flagID):
    a = [dict(blueteamID=row[0], gameID=row[1], flagName=row[2], flagValue=row[3], flanAnswer=row[4], flagPoints=row[5]) \
		for row in db.session.query(Flags.blueteamID, Flags.gameID, Flags.name, Flags.value, Flags.answer, Flags.points).filter(Flags.flagID.in_([flagID]))]
    if not a:
        raise BadRequest("Invalid FlagID!")
    return dumps(a)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
