#!/usr/bin/env python
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine("postgresql://scorebot:password@localhost/scorebot", echo=True)

Base = declarative_base()

class Blueteams(Base):
    __tablename__ = 'blueteams'
    blueteamID = Column(Integer, Sequence('blueteamID_seq'), primary_key=True)
    name = Column(String(20))
    dns = Column(String(16))
    email = Column(String(50))

class Games(Base):
    __tablename__ = 'games'
    date = Column(DateTime)
    gameID = Column(Integer, Sequence('gameID_seq'), primary_key=True)
    name = Column(String(30))

class BluePlayers(Base):
    __tablename__ = 'blueplayers'
    gameID = Column(Integer, ForeignKey("games.gameID"), nullable=False)
    blueplayersID = Column(Integer, Sequence('blueplayersID_seq'), primary_key=True)
    playerID = Column(Integer, nullable=False)
    blueteamID = Column(Integer, ForeignKey("blueteams.blueteamID"), nullable=False)
    score = Column(Integer, nullable=False)
    captain = Column(Boolean, nullable=False)

class Tickets(Base):
    __tablename__ = 'tickets'
    gameID = Column(Integer, ForeignKey("games.gameID"), nullable=False)
    name = Column(String(200))
    value = Column(Integer)
    blueteamID = Column(Integer, ForeignKey("blueteams.blueteamID"), nullable=False)
    duration = Column(Integer)
    message = Column(String(2000))
    TIcketID = Column(Integer, Sequence('TIcketID_seq'), primary_key=True)
    subject = Column(String(500))

class Flags(Base):
    __tablename__ = 'flags'
    flagID = Column(Integer, Sequence('flagID_seq'), primary_key=True)
    name = Column(String(200))
    value = Column(String(200))
    blueteamID = Column(Integer, ForeignKey("blueteams.blueteamID"), nullable=False)
    gameID = Column(Integer, ForeignKey("games.gameID"), nullable=False)
    answer = Column(String(2000))
    points = Column(Integer)

class Hosts(Base):
    __tablename__ = 'hosts'
    value = Column(Integer)
    blueteamID = Column(Integer, ForeignKey("blueteams.blueteamID"), nullable=False)
    hostID = Column(Integer, Sequence('hostID_seq'), primary_key=True)
    gameID = Column(Integer, ForeignKey("games.gameID"), nullable=False)
    hostname = Column(String(30))

class Scores(Base):
    __tablename__ = 'scores'
    date = Column(DateTime, nullable=False)
    blueteamID = Column(Integer, ForeignKey("games.gameID"), nullable=False)
    gameID = Column(Integer, ForeignKey("blueteams.blueteamID"), nullable=False)
    score = Column(Integer, nullable=False)
    scoresID = Column(Integer, Sequence('scoresID_seq'), primary_key=True)

class RedTeam(Base):
    __tablename__ = 'redteam'
    playerID = Column(Integer, Sequence('playerID_seq'), primary_key=True)
    RedTeamID = Column(Integer, Sequence('RedTeamID_seq'), primary_key=True)
    gameID = Column(Integer, ForeignKey("games.gameID"), nullable=False)

class HostStatus(Base):
    __tablename__ = 'hoststatus'
    status = Column(String(50))
    hostStatusID = Column(Integer, Sequence('hostStatusID_seq'), primary_key=True)
    hostID = Column(Integer, ForeignKey("hosts.hostID"), nullable=False)
    datetime = Column(DateTime)

class TicketActivity(Base):
    __tablename__ = 'ticketactivity'
    ticketActivityID = Column(Integer, Sequence('ticketActivityID_seq'), primary_key=True)
    datetime = Column(DateTime)
    injectID = Column(Integer, ForeignKey("tickets.TIcketID"), nullable=False)
    activity = Column(String(50))

class Players(Base):
    __tablename__ = 'players'
    username = Column(String(50))
    firstName = Column(String(50))
    playerID = Column(Integer, Sequence('playerID_seq'), primary_key=True)
    lastName = Column(String(50))
    score = Column(Integer, nullable=False)
    password = Column(String(50))

class Services(Base):
    __tablename__ = 'services'
    hostID = Column(Integer, ForeignKey("hosts.hostID"), nullable=False)
    protocol = Column(String(20))
    name = Column(String(20))
    value = Column(Integer)
    serviceID = Column(Integer, Sequence('serviceID_seq'), primary_key=True)
    port = Column(Integer)

class HostCompromises(Base):
    __tablename__ = 'hostcompromises'
    hostID = Column(Integer, ForeignKey("hosts.hostID"), nullable=False)
    playerID = Column(Integer, ForeignKey("players.playerID"), nullable=False)
    score = Column(Integer, nullable=False)
    starttime = Column(DateTime)
    endtime = Column(DateTime)
    hostCompromisesID = Column(Integer, Sequence('hostCompromisesID_seq'), primary_key=True)

class ServiceStatus(Base):
    __tablename__ = 'servicestatus'
    status = Column(String(50))
    serviceID = Column(Integer, ForeignKey("services.serviceID"), nullable=False)
    serviceStatusID = Column(Integer, Sequence('serviceStatusID_seq'), primary_key=True)
    datetime = Column(DateTime)

class FlagsStolen(Base):
    __tablename__ = 'flagsstolen'
    playerID = Column(Integer, ForeignKey("players.playerID"), nullable=False)
    flagID = Column(Integer, ForeignKey("flags.flagID"), nullable=False)
    flagStolenID = Column(Integer, Sequence('flagStolenID_seq'), primary_key=True)
    activity = Column(String(50))
    datetime = Column(DateTime)

class ServiceCredentials(Base):
    __tablename__ = 'servicecredentials'
    username = Column(String(50))
    created = Column(DateTime)
    credentialID = Column(Integer, Sequence('credentialID_seq'), primary_key=True)
    serviceID = Column(Integer, ForeignKey("services.serviceID"), nullable=False)
    password = Column(String(50))
    valid = Column(Boolean)

class FlagsFound(Base):
    __tablename__ = 'flagsfound'
    playerID = Column(Integer, ForeignKey("players.playerID"), nullable=False)
    flagFoundID = Column(Integer, Sequence('flagFoundID_seq'), primary_key=True)
    flagID = Column(Integer, ForeignKey("flags.flagID"), nullable=False)
    activity = Column(String(50))
    datetime = Column(DateTime)

class Content(Base):
    __tablename__ = 'content'
    name = Column(String(50))
    contentID = Column(Integer, Sequence('contentID_seq'), primary_key=True)
    uri = Column(String(2000))
    value = Column(String(1000))
    content = Column(String(2000))
    serviceID = Column(Integer, ForeignKey("services.serviceID"), nullable=False)

class ContentCredentials(Base):
    __tablename__ = 'contentcredentials'
    username = Column(String(50))
    created = Column(DateTime)
    contentID = Column(Integer, ForeignKey("content.contentID"), nullable=False)
    credentialID = Column(Integer, Sequence('credentialID_seq'), primary_key=True)
    valid = Column(Boolean)
    password = Column(String(50))

class ContentCredentialStatus(Base):
    __tablename__ = 'contentcredentialstatus'
    status = Column(String(50))
    contentCredentialStatusID = Column(Integer, Sequence('contentCredentialStatusID_seq'), primary_key=True)
    playerID = Column(Integer, ForeignKey("players.playerID"), nullable=False)
    datetime = Column(DateTime)
    credentialID = Column(Integer, ForeignKey("contentcredentials.credentialID"), nullable=False)
    score = Column(Integer, nullable=False)

class ServiceCredentialStatus(Base):
    __tablename__ = 'servicecredentialstatus'
    status = Column(String(50))
    servicesCredentialStatusID = Column(Integer, Sequence('servicesCredentialStatusID_seq'), primary_key=True)
    playerID = Column(Integer, ForeignKey("players.playerID"), nullable=False)
    datetime = Column(DateTime)
    credentialID = Column(Integer, ForeignKey("servicecredentials.credentialID"), nullable=False)
    score = Column(Integer, nullable=False)

class ContentStatus(Base):
    __tablename__ = 'contentstatus'
    status = Column(String(50))
    contentID = Column(Integer, ForeignKey("content.contentID"), nullable=False)
    contentStatusID = Column(Integer, Sequence('contentStatusID_seq'), primary_key=True)
    datetime = Column(DateTime)

