#!/usr/bin/env python
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://scorebot:password@localhost/scorebot"
db = SQLAlchemy(app)


class Players(db.Model):
    __tablename__ = 'players'
    username = db.Column(db.String(50), unique=True)
    firstName = db.Column(db.String(50))
    playerID = db.Column(db.Integer, db.Sequence('playerID_seq'), primary_key=True)
    lastName = db.Column(db.String(50))
    score = db.Column(db.Integer, nullable=False)
    password = db.Column(db.String(50))

class Blueteams(db.Model):
    __tablename__ = 'blueteams'
    blueteamID = db.Column(db.Integer, db.Sequence('blueteamID_seq'), primary_key=True)
    name = db.Column(db.String(20), unique=True)
    dns = db.Column(db.String(16))
    email = db.Column(db.String(50))

class Games(db.Model):
    __tablename__ = 'games'
    start = db.Column(db.DateTime)
    gameID = db.Column(db.Integer, db.Sequence('gameID_seq'), primary_key=True)
    name = db.Column(db.String(30), unique=True)
    finish = db.Column(db.DateTime)

class Tickets(db.Model):
    __tablename__ = 'tickets'
    gameID = db.Column(db.Integer, db.ForeignKey("games.gameID"), nullable=False)
    name = db.Column(db.String(200))
    value = db.Column(db.Integer)
    blueteamID = db.Column(db.Integer, db.ForeignKey("blueteams.blueteamID"), nullable=False)
    duration = db.Column(db.Integer)
    message = db.Column(db.String(2000))
    TIcketID = db.Column(db.Integer, db.Sequence('TIcketID_seq'), primary_key=True)
    subject = db.Column(db.String(500))

class Flags(db.Model):
    __tablename__ = 'flags'
    flagID = db.Column(db.Integer, db.Sequence('flagID_seq'), primary_key=True)
    name = db.Column(db.String(200))
    value = db.Column(db.String(200))
    blueteamID = db.Column(db.Integer, db.ForeignKey("blueteams.blueteamID"), nullable=False)
    gameID = db.Column(db.Integer, db.ForeignKey("games.gameID"), nullable=False)
    answer = db.Column(db.String(2000))
    points = db.Column(db.Integer)

class Hosts(db.Model):
    __tablename__ = 'hosts'
    value = db.Column(db.Integer)
    blueteamID = db.Column(db.Integer, db.ForeignKey("blueteams.blueteamID"), nullable=False)
    hostID = db.Column(db.Integer, db.Sequence('hostID_seq'), primary_key=True)
    gameID = db.Column(db.Integer, db.ForeignKey("games.gameID"), nullable=False)
    hostname = db.Column(db.String(30))

class GamesTeams(db.Model):
    __tablename__ = 'gamesteams'
    blueteamID = db.Column(db.Integer, db.ForeignKey("blueteams.blueteamID"), nullable=False)
    gameID = db.Column(db.Integer, db.ForeignKey("games.gameID"), nullable=False)
    gameteamsID = db.Column(db.Integer, db.Sequence('gameteamsID_seq'), primary_key=True)

class Scores(db.Model):
    __tablename__ = 'scores'
    date = db.Column(db.DateTime, nullable=False)
    blueteamID = db.Column(db.Integer, db.ForeignKey("games.gameID"), nullable=False)
    gameID = db.Column(db.Integer, db.ForeignKey("blueteams.blueteamID"), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    scoresID = db.Column(db.Integer, db.Sequence('scoresID_seq'), primary_key=True)

class RedTeam(db.Model):
    __tablename__ = 'redteam'
    playerID = db.Column(db.Integer, db.ForeignKey("players.playerID"), nullable=False)
    RedTeamID = db.Column(db.Integer, db.Sequence('RedTeamID_seq'), primary_key=True)
    gameID = db.Column(db.Integer, db.ForeignKey("games.gameID"), nullable=False)

class HostCompromises(db.Model):
    __tablename__ = 'hostcompromises'
    hostID = db.Column(db.Integer, db.ForeignKey("hosts.hostID"), nullable=False)
    playerID = db.Column(db.Integer, db.ForeignKey("players.playerID"), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    starttime = db.Column(db.DateTime)
    endtime = db.Column(db.DateTime)
    hostCompromisesID = db.Column(db.Integer, db.Sequence('hostCompromisesID_seq'), primary_key=True)

class HostStatus(db.Model):
    __tablename__ = 'hoststatus'
    status = db.Column(db.String(50), nullable=False)
    checkStarted = db.Column(db.DateTime, nullable=False)
    hostID = db.Column(db.Integer, db.ForeignKey("hosts.hostID"), nullable=False)
    checkFInished = db.Column(db.DateTime)
    hostStatusID = db.Column(db.Integer, db.Sequence('hostStatusID_seq'), primary_key=True)

class BluePlayers(db.Model):
    __tablename__ = 'blueplayers'
    blueplayerID = db.Column(db.Integer, db.Sequence('blueplayerID_seq'), primary_key=True)
    playerID = db.Column(db.Integer, db.ForeignKey("players.playerID"), nullable=False)
    blueteamID = db.Column(db.Integer, db.ForeignKey("gamesteams.blueteamID"), nullable=False)
    score = db.Column(db.Integer, nullable=False)

class TicketActivity(db.Model):
    __tablename__ = 'ticketactivity'
    ticketActivityID = db.Column(db.Integer, db.Sequence('ticketActivityID_seq'), primary_key=True)
    datetime = db.Column(db.DateTime)
    injectID = db.Column(db.Integer, db.ForeignKey("tickets.TIcketID"), nullable=False)
    activity = db.Column(db.String(50))

class FlagsActivity(db.Model):
    __tablename__ = 'flagsactivity'
    playerID = db.Column(db.Integer, db.ForeignKey("players.playerID"), nullable=False)
    flagFoundID = db.Column(db.Integer, db.Sequence('flagFoundID_seq'), primary_key=True)
    flagID = db.Column(db.Integer, db.ForeignKey("flags.flagID"), nullable=False)
    activity = db.Column(db.String(50))
    datetime = db.Column(db.DateTime)

class Services(db.Model):
    __tablename__ = 'services'
    hostID = db.Column(db.Integer, db.ForeignKey("hosts.hostID"), nullable=False)
    protocol = db.Column(db.String(20))
    name = db.Column(db.String(20))
    value = db.Column(db.Integer)
    serviceID = db.Column(db.Integer, db.Sequence('serviceID_seq'), primary_key=True)
    port = db.Column(db.Integer)

class ServiceStatus(db.Model):
    __tablename__ = 'servicestatus'
    status = db.Column(db.String(50), nullable=False)
    checkStarted = db.Column(db.DateTime, nullable=False)
    checkFinished = db.Column(db.DateTime)
    serviceID = db.Column(db.Integer, db.ForeignKey("services.serviceID"), nullable=False)
    serviceStatusID = db.Column(db.Integer, db.Sequence('serviceStatusID_seq'), primary_key=True)

class ServiceCredentials(db.Model):
    __tablename__ = 'servicecredentials'
    username = db.Column(db.String(50))
    created = db.Column(db.DateTime)
    credentialID = db.Column(db.Integer, db.Sequence('credentialID_seq'), primary_key=True)
    serviceID = db.Column(db.Integer, db.ForeignKey("services.serviceID"), nullable=False)
    password = db.Column(db.String(50))
    valid = db.Column(db.Boolean)

class Content(db.Model):
    __tablename__ = 'content'
    name = db.Column(db.String(50))
    contentID = db.Column(db.Integer, db.Sequence('contentID_seq'), primary_key=True)
    uri = db.Column(db.String(2000))
    value = db.Column(db.String(1000))
    content = db.Column(db.String(2000))
    serviceID = db.Column(db.Integer, db.ForeignKey("services.serviceID"), nullable=False)

class ContentCredentials(db.Model):
    __tablename__ = 'contentcredentials'
    username = db.Column(db.String(50))
    created = db.Column(db.DateTime)
    contentID = db.Column(db.Integer, db.ForeignKey("content.contentID"), nullable=False)
    credentialID = db.Column(db.Integer, db.Sequence('credentialID_seq'), primary_key=True)
    valid = db.Column(db.Boolean)
    password = db.Column(db.String(50))

class ContentCredentialStatus(db.Model):
    __tablename__ = 'contentcredentialstatus'
    status = db.Column(db.String(50))
    contentCredentialStatusID = db.Column(db.Integer, db.Sequence('contentCredentialStatusID_seq'), primary_key=True)
    playerID = db.Column(db.Integer, db.ForeignKey("players.playerID"), nullable=False)
    datetime = db.Column(db.DateTime)
    credentialID = db.Column(db.Integer, db.ForeignKey("contentcredentials.credentialID"), nullable=False)
    score = db.Column(db.Integer, nullable=False)

class ServiceCredentialStatus(db.Model):
    __tablename__ = 'servicecredentialstatus'
    status = db.Column(db.String(50))
    servicesCredentialStatusID = db.Column(db.Integer, db.Sequence('servicesCredentialStatusID_seq'), primary_key=True)
    playerID = db.Column(db.Integer, db.ForeignKey("players.playerID"), nullable=False)
    datetime = db.Column(db.DateTime)
    credentialID = db.Column(db.Integer, db.ForeignKey("servicecredentials.credentialID"), nullable=False)
    score = db.Column(db.Integer, nullable=False)

class ContentStatus(db.Model):
    __tablename__ = 'contentstatus'
    status = db.Column(db.String(50))
    contentID = db.Column(db.Integer, db.ForeignKey("content.contentID"), nullable=False)
    checkFinished = db.Column(db.DateTime)
    checkStarted = db.Column(db.DateTime, nullable=False)
    contentStatusID = db.Column(db.Integer, db.Sequence('contentStatusID_seq'), primary_key=True)

if __name__== "__main__":
    db.drop_all()
    db.create_all()
    bt1 = Blueteams(name="ALPHA", dns="10.100.101.100", email="alpha@alpha.net")
    bt2 = Blueteams(name="BETA", dns="10.100.102.100", email="beta@beta.net")
    bt3 = Blueteams(name="GAMMA", dns="10.100.102.100", email="gamma@gamma.net")
    #bt4 = Blueteams(name="ALPHA", dns="10.100.101.100", email="alpha@alpha.net")
    db.session.add(bt1)
    db.session.add(bt2)
    db.session.add(bt3)
    #db.session.add(bt4)
    db.session.commit()

