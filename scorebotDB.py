#!/usr/bin/env python

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://scorebot:password@localhost/scorebot"
db = SQLAlchemy(app)


class Blueteams(db.Model):
    __tablename__ = 'blueteams'
    blueteamID = Column(db.Integer, Sequence('blueteamID_seq'), primary_key=True)
    name = Column(db.String(20), unique=True)
    dns = Column(db.String(16))
    email = Column(db.String(50))

class Games(db.Model):
    __tablename__ = 'games'
    date = Column(db.DateTime)
    gameID = Column(db.Integer, Sequence('gameID_seq'), primary_key=True)
    name = Column(db.String(30))

class BluePlayers(db.Model):
    __tablename__ = 'blueplayers'
    gameID = Column(db.Integer, ForeignKey("games.gameID"), nullable=False)
    blueplayersID = Column(db.Integer, Sequence('blueplayersID_seq'), primary_key=True)
    playerID = Column(db.Integer, nullable=False)
    blueteamID = Column(db.Integer, ForeignKey("blueteams.blueteamID"), nullable=False)
    score = Column(db.Integer, nullable=False)
    captain = Column(db.Boolean, nullable=False)

class Tickets(db.Model):
    __tablename__ = 'tickets'
    gameID = Column(db.Integer, ForeignKey("games.gameID"), nullable=False)
    name = Column(db.String(200))
    value = Column(db.Integer)
    blueteamID = Column(db.Integer, ForeignKey("blueteams.blueteamID"), nullable=False)
    duration = Column(db.Integer)
    message = Column(db.String(2000))
    TIcketID = Column(db.Integer, Sequence('TIcketID_seq'), primary_key=True)
    subject = Column(db.String(500))

class Flags(db.Model):
    __tablename__ = 'flags'
    flagID = Column(db.Integer, Sequence('flagID_seq'), primary_key=True)
    name = Column(db.String(200))
    value = Column(db.String(200))
    blueteamID = Column(db.Integer, ForeignKey("blueteams.blueteamID"), nullable=False)
    gameID = Column(db.Integer, ForeignKey("games.gameID"), nullable=False)
    answer = Column(db.String(2000))
    points = Column(db.Integer)

class Hosts(db.Model):
    __tablename__ = 'hosts'
    value = Column(db.Integer)
    blueteamID = Column(db.Integer, ForeignKey("blueteams.blueteamID"), nullable=False)
    hostID = Column(db.Integer, Sequence('hostID_seq'), primary_key=True)
    gameID = Column(db.Integer, ForeignKey("games.gameID"), nullable=False)
    hostname = Column(db.String(30))

class Scores(db.Model):
    __tablename__ = 'scores'
    date = Column(db.DateTime, nullable=False)
    blueteamID = Column(db.Integer, ForeignKey("games.gameID"), nullable=False)
    gameID = Column(db.Integer, ForeignKey("blueteams.blueteamID"), nullable=False)
    score = Column(db.Integer, nullable=False)
    scoresID = Column(db.Integer, Sequence('scoresID_seq'), primary_key=True)

class RedTeam(db.Model):
    __tablename__ = 'redteam'
    playerID = Column(db.Integer, Sequence('playerID_seq'), primary_key=True)
    RedTeamID = Column(db.Integer, Sequence('RedTeamID_seq'), primary_key=True)
    gameID = Column(db.Integer, ForeignKey("games.gameID"), nullable=False)

class HostStatus(db.Model):
    __tablename__ = 'hoststatus'
    status = Column(db.String(50))
    hostStatusID = Column(db.Integer, Sequence('hostStatusID_seq'), primary_key=True)
    hostID = Column(db.Integer, ForeignKey("hosts.hostID"), nullable=False)
    datetime = Column(db.DateTime)

class TicketActivity(db.Model):
    __tablename__ = 'ticketactivity'
    ticketActivityID = Column(db.Integer, Sequence('ticketActivityID_seq'), primary_key=True)
    datetime = Column(db.DateTime)
    injectID = Column(db.Integer, ForeignKey("tickets.TIcketID"), nullable=False)
    activity = Column(db.String(50))

class Players(db.Model):
    __tablename__ = 'players'
    username = Column(db.String(50))
    firstName = Column(db.String(50))
    playerID = Column(db.Integer, Sequence('playerID_seq'), primary_key=True)
    lastName = Column(db.String(50))
    score = Column(db.Integer, nullable=False)
    password = Column(db.String(50))

class Services(db.Model):
    __tablename__ = 'services'
    hostID = Column(db.Integer, ForeignKey("hosts.hostID"), nullable=False)
    protocol = Column(db.String(20))
    name = Column(db.String(20))
    value = Column(db.Integer)
    serviceID = Column(db.Integer, Sequence('serviceID_seq'), primary_key=True)
    port = Column(db.Integer)

class HostCompromises(db.Model):
    __tablename__ = 'hostcompromises'
    hostID = Column(db.Integer, ForeignKey("hosts.hostID"), nullable=False)
    playerID = Column(db.Integer, ForeignKey("players.playerID"), nullable=False)
    score = Column(db.Integer, nullable=False)
    starttime = Column(db.DateTime)
    endtime = Column(db.DateTime)
    hostCompromisesID = Column(db.Integer, Sequence('hostCompromisesID_seq'), primary_key=True)

class ServiceStatus(db.Model):
    __tablename__ = 'servicestatus'
    status = Column(db.String(50))
    serviceID = Column(db.Integer, ForeignKey("services.serviceID"), nullable=False)
    serviceStatusID = Column(db.Integer, Sequence('serviceStatusID_seq'), primary_key=True)
    datetime = Column(db.DateTime)

class FlagsStolen(db.Model):
    __tablename__ = 'flagsstolen'
    playerID = Column(db.Integer, ForeignKey("players.playerID"), nullable=False)
    flagID = Column(db.Integer, ForeignKey("flags.flagID"), nullable=False)
    flagStolenID = Column(db.Integer, Sequence('flagStolenID_seq'), primary_key=True)
    activity = Column(db.String(50))
    datetime = Column(db.DateTime)

class ServiceCredentials(db.Model):
    __tablename__ = 'servicecredentials'
    username = Column(db.String(50))
    created = Column(db.DateTime)
    credentialID = Column(db.Integer, Sequence('credentialID_seq'), primary_key=True)
    serviceID = Column(db.Integer, ForeignKey("services.serviceID"), nullable=False)
    password = Column(db.String(50))
    valid = Column(db.Boolean)

class FlagsFound(db.Model):
    __tablename__ = 'flagsfound'
    playerID = Column(db.Integer, ForeignKey("players.playerID"), nullable=False)
    flagFoundID = Column(db.Integer, Sequence('flagFoundID_seq'), primary_key=True)
    flagID = Column(db.Integer, ForeignKey("flags.flagID"), nullable=False)
    activity = Column(db.String(50))
    datetime = Column(db.DateTime)

class Content(db.Model):
    __tablename__ = 'content'
    name = Column(db.String(50))
    contentID = Column(db.Integer, Sequence('contentID_seq'), primary_key=True)
    uri = Column(db.String(2000))
    value = Column(db.String(1000))
    content = Column(db.String(2000))
    serviceID = Column(db.Integer, ForeignKey("services.serviceID"), nullable=False)

class ContentCredentials(db.Model):
    __tablename__ = 'contentcredentials'
    username = Column(db.String(50))
    created = Column(db.DateTime)
    contentID = Column(db.Integer, ForeignKey("content.contentID"), nullable=False)
    credentialID = Column(db.Integer, Sequence('credentialID_seq'), primary_key=True)
    valid = Column(db.Boolean)
    password = Column(db.String(50))

class ContentCredentialStatus(db.Model):
    __tablename__ = 'contentcredentialstatus'
    status = Column(db.String(50))
    contentCredentialStatusID = Column(db.Integer, Sequence('contentCredentialStatusID_seq'), primary_key=True)
    playerID = Column(db.Integer, ForeignKey("players.playerID"), nullable=False)
    datetime = Column(db.DateTime)
    credentialID = Column(db.Integer, ForeignKey("contentcredentials.credentialID"), nullable=False)
    score = Column(db.Integer, nullable=False)

class ServiceCredentialStatus(db.Model):
    __tablename__ = 'servicecredentialstatus'
    status = Column(db.String(50))
    servicesCredentialStatusID = Column(db.Integer, Sequence('servicesCredentialStatusID_seq'), primary_key=True)
    playerID = Column(db.Integer, ForeignKey("players.playerID"), nullable=False)
    datetime = Column(db.DateTime)
    credentialID = Column(db.Integer, ForeignKey("servicecredentials.credentialID"), nullable=False)
    score = Column(db.Integer, nullable=False)

class ContentStatus(db.Model):
    __tablename__ = 'contentstatus'
    status = Column(db.String(50))
    contentID = Column(db.Integer, ForeignKey("content.contentID"), nullable=False)
    contentStatusID = Column(db.Integer, Sequence('contentStatusID_seq'), primary_key=True)
    datetime = Column(db.DateTime)


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

