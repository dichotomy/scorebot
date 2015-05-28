#!/usr/bin/env python

from scorebotDB import *

class SBGame:
	def __init__(self):
		self.id = 0
		self.name = ''
		self.teams = []
		self.startdate = ''
		
	def add_gameTeam(self, NewTeam):
		self.teams.append(NewTeam)
	def remove_gameTeam(self, RemoveTeamID):
		for co in range(0, len(self.teams)):
			if self.teams[co].id == self.RemoveTeamID:
				self.teams.pop(co)
				break
	
	def toJSON_old(self):
		js = []
		js.append('{ "gameID": "%s"' % self.id)
		js.append(', "gameName": "%s"' % self.name)
		js.append(', "gameStart": "%s"' % self.startdate)
		if self.teams:
			js.append(', "gameTeams" : [ ')
			for et in range(0,len(self.teams)):
				if et > 0:
					js.append(', ')
				js.append(self.teams[et].toJSON())
			js.append(' ]')
		js.append(' }')
		return ''.join(js)
	def toJSON(self):
		js = []
		js.append('{ "gameID": "%s"' % self.id)
		js.append(', "gameName": "%s"' % self.name)
		js.append(', "gameStart": "%s"' % self.startdate)
		js.append(' }')
		return ''.join(js)
class SBPlayer:
	def __init__(self):
		self.id = 0
		self.pid = 0
		self.name = ''
		self.score = 0
		self.gameID = 0
		self.teamID = 0
		self.type = 'blue'
	
	def toJSON(self):
		js = []
		js.append('{ "playerID": "%s"' % self.id)
		js.append(', "playerPID": "%s"' % self.pid)
		js.append(', "playerType": "%s"' % self.type)
		js.append(', "playerName": "%s"' % self.name)
		js.append(', "playerScore": "%s"' % self.score)
		js.append(', "playerGameID": "%s"' % self.gameID)
		js.append(', "playerTeamID": "%s"' % self.teamID)
		js.append(' }')
		return ''.join(js)
class SBTeam:
	def __init__(self):
		self.id = 0
		self.dns = ''
		self.name = ''
		self.email = ''
		self.players = []
		self.type = 'blue'
		self.captain = None
	
	def add_teamPlayer(self, NewPlayer):
		self.players.append(NewPlayer)
	def remove_teamPlayer(self, RemovePlayerID):
		for co in range(0, len(self.players)):
			if self.players[co].id == RemovePlayerID:
				self.players.pop(co)
				break
	
	def toJSON_old(self):
		js = []
		js.append('{ "teamID": "%s"' % self.id)
		js.append(', "teamDNS": "%s"' % self.dns)
		js.append(', "teamType": "%s"' % self.type)
		js.append(', "teamName": "%s"' % self.name)
		js.append(', "teamEmail": "%s"' % self.email)
		if self.captain:
			js.append(', "teamCaptain": %s ' % self.captain.toJSON())
		if self.players:
			js.append(', "teamPlayers": [ ')
			for ep in range(0,len(self.players)):
				if ep > 0:
					js.append(', ')
				js.append(self.players[ep].toJSON())
			js.append(' ]')
		js.append(' }')
		return ''.join(js)
	def toJSON(self):
		js = []
		js.append('{ "teamID": "%s"' % self.id)
		js.append(', "teamDNS": "%s"' % self.dns)
		js.append(', "teamType": "%s"' % self.type)
		js.append(', "teamName": "%s"' % self.name)
		js.append(', "teamEmail": "%s"' % self.email)
		js.append(' }')
		return ''.join(js)
class SBHost:
	def __init__(self):
		self.id = 0
		self.name = ''
		self.value = 0
		self.servs = []
		self.teamID = 0
		self.gameID = 0
		self.status = None
		self.compromised = None
	
	def toJSON(self):
		js = []
		js.append('{ "hostID": "%s"' % self.id)
		js.append(', "hostName": "%s"' % self.name)
		js.append(', "hostValue": "%s"' % self.value)
		js.append(', "hostTeamID": "%s"' % self.teamID)
		js.append(', "hostGameID": "%s"' % self.gameID)
		js.append(' }')
		return ''.join(js)
	def toJSON_old(self):
		js = []
		js.append('{ "hostID": "%s"' % self.id)
		js.append(', "hostName": "%s"' % self.name)
		js.append(', "hostValue": "%s"' % self.value)
		js.append(', "hostTeamID": "%s"' % self.teamID)
		js.append(', "hostGameID": "%s"' % self.gameID)
		if self.status:
			js.append(', "hostStatus": %s' % self.status.toJSON())
		if self.servs:
			js.append(', "hostServices": [ ')
			for e in range(0,len(self.servs)):
				if e > 0:
					js.append(', ')
				js.append(self.servs[e].toJSON())
			js.append(' ]')
		if self.compromised:
			js.append(', "hostCompromised": %s' % self.compromised.toJSON())
		js.append(' }')
		return ''.join(js)
class SBHostCompromised:
	def __init__(self):
		self.id = 0
		self.pid = 0
		self.end = ''
		self.score = 0
		self.start = ''
		self.hostID = 0
	
	def toJSON(self):
		js = []
		js.append('{ "compromisedID": "%s"' % self.id)
		js.append(', "compromisedStart": "%s"' % self.start)
		js.append(', "compromisedEnd": "%s"' % self.end)
		js.append(', "compromisedPlayerID": "%s"' % self.pid)
		js.append(', "compromisedScore": "%s"' % self.score)
		js.append(', "compromisedHostID": "%s"' % self.hostID)
		js.append(' }')
		return ''.join(js)
class SBService:
	def __init__(self):
		self.id = 0	
		self.port = 0
		self.name =''
		self.value = 0
		self.hostID = 0
		self.creds = None
		self.protocol = ''
		self.status = None
		self.content = None
		
	def toJSON(self):
		js = []
		js.append('{ "serviceID": "%s"' % self.id)
		js.append(', "serviceName": "%s"' % self.name)
		js.append(', "serviceValue": "%s"' % self.value)
		js.append(', "serviceHostID": "%s"' % self.hostID)
		js.append(', "servicePort": "%s"' % self.port)
		js.append(', "serviceProtocol": "%s"' % self.protocol)
		js.append(' }')
		return ''.join(js)
	def toJSON_old(self):
		js = []
		js.append('{ "serviceID": "%s"' % self.id)
		js.append(', "serviceName": "%s"' % self.name)
		js.append(', "serviceValue": "%s"' % self.value)
		js.append(', "serviceHostID": "%s"' % self.hostID)
		js.append(', "servicePort": "%s"' % self.port)
		js.append(', "serviceProtocol": "%s"' % self.protocol)
		if self.status:
			js.append(', "serviceStatus": %s' % self.status.toJSON())
		if self.content:
			js.append(', "serviceContent": %s' % self.content.toJSON())
		if self.creds:
			js.append(', "serviceCredentials": %s' % self.creds.toJSON())
		js.append(' }')
		return ''.join(js)
class SBStatus:
	def __init__(self):
		self.id = 0
		self.date = ''
		self.status = ''
		self.instanceID = 0
		
	def toJSON(self):
		js = []
		js.append('{ "statusID": "%s"' % self.id)
		js.append(', "statusDate": "%s"' % self.date)
		js.append(', "statusValue": "%s"' % self.status)
		js.append(', "statusInstanceID": "%s"' % self.instanceID)
		js.append(' }')
		return ''.join(js)
class SBCreds:
	def __init__(self):
		self.id = 0
		self.created = ''
		self.valid = False
		self.instanceID = 0
		self.username = ''
		self.password = ''
		self.status = None

	def toJSON(self):
		js = []
		js.append('{ "credentialID": "%s"' % self.id)
		js.append(', "credentialDate": "%s"' % self.created)
		js.append(', "credentialValid": "%s"' % self.valid)
		js.append(', "credentialInstanceID": "%s"' % self.instanceID)
		js.append(', "credentialUsername": "%s"' % self.username)
		js.append(', "credentialPassword": "%s"' % self.password)
		js.append(' }')
		return ''.join(js)
	def toJSON_old(self):
		js = []
		js.append('{ "credentialID": "%s"' % self.id)
		js.append(', "credentialDate": "%s"' % self.created)
		js.append(', "credentialValid": "%s"' % self.valid)
		js.append(', "credentialInstanceID": "%s"' % self.instanceID)
		js.append(', "credentialUsername": "%s"' % self.username)
		js.append(', "credentialPassword": "%s"' % self.password)
		if self.status:
			js.append(', "credentialStatus": %s' % self.status.toJSON())
		js.append(' }')
		return ''.join(js)
class SBCredsStatus:
	def __init__(self):
		self.id = 0
		self.pid = 0
		self.date = ''
		self.score = 0
		self.status = ''
		self.instanceID = 0
	
	def toJSON(self):
		js = []
		js.append('{ "statusID": "%s"' % self.id)
		js.append(', "statusDate": "%s"' % self.date)
		js.append(', "statusPlayerID": "%s"' % self.pid)
		js.append(', "statusInstanceID": "%s"' % self.instanceID)
		js.append(', "statusScore": "%s"' % self.score)
		js.append(', "statusValue": "%s"' % self.status)
		js.append(' }')
		return ''.join(js)
class SBServiceContent:
	def __init__(self):
		self.id = 0
		self.uri = ''
		self.name = ''
		self.value = 0
		self.content = ''
		self.creds = None
		self.status = None
		self.serviceID = 0
	
	def toJSON(self):
		js = []
		js.append('{ "contentID": "%s"' % self.id)
		js.append(', "contentURI": "%s"' % self.uri)
		js.append(', "contentValue": "%s"' % self.value)
		js.append(', "contentContent": "%s"' % self.content)
		js.append(', "contentServiceID": "%s"' % self.serviceID)
		js.append(' }')
		return ''.join(js)	
	def toJSON_old(self):
		js = []
		js.append('{ "contentID": "%s"' % self.id)
		js.append(', "contentURI": "%s"' % self.uri)
		js.append(', "contentValue": "%s"' % self.value)
		js.append(', "contentContent": "%s"' % self.content)
		js.append(', "contentServiceID": "%s"' % self.serviceID)
		if self.creds:
			js.append(', "contentCredentials": %s' % self.creds.toJSON())
		if self.status:
			js.append(', "contentStatus": %s' % self.status.toJSON())
		js.append(' }')
		return ''.join(js)

class SBFlag:
	def __init__(self):
		self.id = 0
		self.name = ''
		self.value = ''
		self.teamID = 0
		self.gameID = 0
		self.points = 0
		self.answer = ''
		self.found = None
		self.stolen = None

	def toJSON_old(self):
		js = []
		js.append('{ "flagID": "%s"' % self.id)
		js.append(', "flagName": "%s"' % self.name)
		js.append(', "flagValue": "%s"' % self.value)
		js.append(', "flagTeamID": "%s"' % self.teamID)
		js.append(', "flagGameID": "%s"' % self.gameID)
		js.append(', "flagPoints": "%s"' % self.points)
		js.append(', "flagAnswer": "%s"' % self.answer)
		if self.found:
			js.append(', "flagFound": %s' % self.found.toJSON())
		if self.stolen:
			js.append(', "flagStolen": %s' % self.stolen.toJSON())
		js.append(' }')
		return ''.join(js)
	def toJSON(self):
		js = []
		js.append('{ "flagID": "%s"' % self.id)
		js.append(', "flagName": "%s"' % self.name)
		js.append(', "flagValue": "%s"' % self.value)
		js.append(', "flagTeamID": "%s"' % self.teamID)
		js.append(', "flagGameID": "%s"' % self.gameID)
		js.append(', "flagPoints": "%s"' % self.points)
		js.append(', "flagAnswer": "%s"' % self.answer)
		js.append(' }')
		return ''.join(js)
class SBFlagAct:
	def __init__(self):
		self.id = 0
		self.flagID = 0
		self.playerID = 0
		self.datetime = ''
		self.activity = ''
		
	def toJSON(self):
		js = []
		js.append('{ "flagActivityID": "%s"' % self.id)
		js.append(', "flagFlagID": "%s"' % self.flagID)
		js.append(', "flagPlayerID": "%s"' % self.playerID)
		js.append(', "flagActivity": "%s"' % self.activity)
		js.append(', "flagDatetime": "%s"' % self.datetime)
		js.append(' }')
		return ''.join(js)

def toJSON(Object):
	return "[%s]" % Object.toJSON()

def getGame(GameID):
	a = [dict(name=row[0], date=row[1]) \
        for row in db.session.query(Games.name, Games.date).filter(Games.gameID.in_([GameID])).order_by(Games.date)]
	if not a:
		return None
	if len(a) != 1:
		return None
	b = SBGame()
	b.id = GameID
	b.name = (a[0]["name"])
	b.startdate = (a[0]["date"])
	c = [dict(id=row[0]) \
		for row in db.session.query(GamesTeams.blueteamsID).filter(GamesTeams.gameID.in_([GameID])).order_by(GamesTeams.blueteamsID)]
	if c and len(c) > 0:
		for d in range(0, len(c)):
			e = getTeam(c[d]["id"], GameID)
			b.teams.append(e)
	return b
def getTeam(TeamID, GameID):
	a = SBTeam()
	a.id = TeamID
	b = [dict(name=row[0],dns=row[1],email=row[2]) \
		 for row in db.session.query(Blueteams.name, Blueteams.dns, Blueteams.email).filter(Blueteams.blueteamID.in_([TeamID]))]
	if not b:
		return None
	if b and len(b) > 0:
		a.dns = b[0]["dns"]
		a.email = b[0]["email"]
		a.name = b[0]["name"]
	c = [dict(id=row[0], pid=row[1], isc=row[2], score=row[3]) \
		 for row in db.session.query(BluePlayers.blueplayersID, BluePlayers.playerID, BluePlayers.captain, BluePlayers.score).filter(BluePlayers.blueteamID.in_([TeamID])).order_by(BluePlayers.blueplayersID)]
	if c and len(c) > 0:
		for d in range(0, len(c)):
			e = SBPlayer()
			e.id = c[d]["id"]
			e.pid = c[d]["pid"]
			e.gameID = GameID
			e.teamID = TeamID
			e.score = c[d]["score"]
			if c[d]["isc"]:
				a.captain = e
			f = [dict(name=row[0]) \
				 for row in db.session.query(Players.username).filter(Players.playerID.in_([e.pid]))]
			if f and len(f) > 0:
				e.name = f[0]["name"]
			a.players.append(e)
	return a
def getPlayer(PlayerID):
	a = SBPlayer()
	b = [dict(id=row[0], tid=row[1], score=row[2]) \
		for row in db.session.query(BluePlayers.playerID, BluePlayers.blueteamID, BluePlayers.score).filter(BluePlayers.blueplayersID.in_([PlayerID]))]
	if not b:
		return None
	a.pid = PlayerID
	a.id = b[0]["id"]
	a.score = b[0]["score"]
	a.teamID = b[0]["tid"]
	b = [dict(name=row[0]) \
		for row in db.session.query(Players.username).filter(Players.playerID.in_([a.id]))]
	if b and len(b) > 0:
		a.name = b[0]["name"]
	c = [dict(id=row[0]) \
		for row in db.session.query(GamesTeams.gameID).filter(GamesTeams.blueteamsID.in_([a.teamID]))]
	if c and len(c) > 0:
		a.gameID = c[0]["id"]
	return a

def getHost(HostID):
	a = SBHost()
	b = [dict(val=row[0], btid=row[1], gid=row[2], name=row[3]) \
		for row in db.session.query(Hosts.value, Hosts.blueteamID, Hosts.gameID, Hosts.hostname).filter(Hosts.hostID.in_([HostID]))]
	if not b:
		return None
	a.id = 	HostID
	a.gameID = b[0]["gid"]
	a.teamID = b[0]["btid"]
	a.name = b[0]["name"]
	a.value = b[0]["val"]
	a.compromised = getHostCompromised(HostID)
	a.status = getHostStatus(HostID)
	c = [dict(id=row[0]) \
		for row in db.session.query(Services.serviceID).filter(Services.hostID.in_([HostID]))]
	if c and len(c) > 0:
		for d in range(0, len(c)):
			e = getService(c[d]["id"])
			a.servs.append(e)
	return a
def getHostCompromised(HostID):
	a = SBHostCompromised()
	b = [dict(id=row[0], score=row[1], pid=row[2], start=row[3], end=row[4]) \
		for row in db.session.query(HostCompromises.hostCompromisesID, HostCompromises.score, HostCompromises.playerID, HostCompromises.starttime, HostCompromises.endtime).filter(HostCompromises.hostID.in_([HostID]))]
	if not b:
		return None
	a.hostID = HostID
	a.id = b[0]["id"]
	a.pid = b[0]["pid"]
	a.score = b[0]["score"]
	a.start = b[0]["start"]
	a.end = b[0]["end"]
	return a
def getHostStatus(HostID):
	a = SBStatus()
	b = [dict(id=row[0], date=row[1], stat=row[2]) \
		for row in db.session.query(HostStatus.hostStatusID, HostStatus.datetime, HostStatus.status).filter(HostStatus.hostID.in_([HostID])).order_by(HostStatus.datetime)]
	if not b:
		return None
	a.id = b[0]["id"]
	a.date = b[0]["date"]
	a.instanceID = HostID
	a.status = b[0]["stat"]
	return a
def getService(ServiceID):
	a = SBService()
	b = [dict(id=row[0], hid=row[1], prot=row[2], name=row[3], val=row[4], port=row[5]) \
		for row in db.session.query(Services.serviceID, Services.hostID, Services.protocol, Services.name, Services.value, Services.port).filter(Services.serviceID.in_([ServiceID]))]
	if not b:
		return None
	a.id = b[0]["id"]
	a.hostID = b[0]["hid"]
	a.name = b[0]["name"]
	a.protocol = b[0]["prot"]
	a.port = b[0]["port"]
	a.value = b[0]["val"]
	c = [dict(id=row[0]) \
		for row in db.session.query(Content.contentID).filter(Content.serviceID.in_([ServiceID]))]
	if c:
		a.content = getContent(c[0]["id"])
	a.status = getServiceStatus(ServiceID)
	a.creds = getServiceCreds(ServiceID)
	return a
def getContent(ContentID):
	a = SBServiceContent()
	b = [dict(id=row[0], name=row[1], iid=row[2], content=row[3], val=row[4], ur=row[5]) \
		for row in db.session.query(Content.contentID, Content.name, Content.serviceID, Content.content, Content.value, Content.uri).filter(Content.contentID.in_([ContentID]))]
	if not b:
		return None
	a.id = b[0]["id"]
	a.name = b[0]["name"]
	a.serviceID = b[0]["iid"]
	a.content = b[0]["content"]
	a.value = b[0]["val"]
	a.uri = b[0]["ur"]
	a.creds = getContentCreds(ContentID)
	a.status = getContentStatus(ContentID)
	return a
def getServiceStatus(ServiceID):
	a = SBStatus()
	b = [dict(id=row[0], date=row[1], stat=row[2]) \
		for row in db.session.query(ServiceStatus.serviceStatusID, ServiceStatus.datetime, ServiceStatus.status).filter(ServiceStatus.serviceID.in_([ServiceID])).order_by(ServiceStatus.datetime)]
	if not b:
		return None
	a.id = b[0]["id"]
	a.date = b[0]["date"]
	a.instanceID = ServiceID
	a.status = b[0]["stat"]
	return a
def getContentStatus(ContentID):
	a = SBStatus()
	b = [dict(id=row[0], date=row[1], stat=row[2]) \
		for row in db.session.query(ContentStatus.contentStatusID, ContentStatus.datetime, ContentStatus.status).filter(ContentStatus.contentID.in_([ContentID])).order_by(ContentStatus.datetime)]
	if not b:
		return None
	a.id = b[0]["id"]
	a.date = b[0]["date"]
	a.instanceID = ContentID
	a.status = b[0]["stat"]
	return a
def getServiceCreds(ServiceID):
	a = SBCreds()
	b = [dict(id=row[0], uname=row[1], paswd=row[2], create=row[3], val=row[4]) \
		for row in db.session.query(ServiceCredentials.credentialID, ServiceCredentials.username, ServiceCredentials.password, ServiceCredentials.created, ServiceCredentials.valid).filter(ServiceCredentials.serviceID.in_([ServiceID]))]
	if not b:
		return None
	a.id = b[0]["id"]
	a.username = b[0]["uname"]
	a.password = b[0]["paswd"]
	a.created = b[0]["create"]
	a.instanceID = ServiceID
	a.valid = b[0]["val"]
	c = [dict(id=row[0], stat=row[1], date=row[2], score=row[3], pid=row[4]) \
		for row in db.session.query(ServiceCredentialStatus.servicesCredentialStatusID, ServiceCredentialStatus.status, ServiceCredentialStatus.datetime, ServiceCredentialStatus.score, ServiceCredentialStatus.playerID).filter(ServiceCredentialStatus.credentialID.in_([a.id])).order_by(ServiceCredentialStatus.datetime)]
	if c:
		d = SBCredsStatus()
		d.id = c[0]["id"]
		d.date = c[0]["date"]
		d.status = c[0]["stat"]
		d.pid = c[0]["pid"]
		d.score = c[0]["score"]
		d.instanceID = a.id
		a.status = d
	return a
def getContentCreds(ContentID):
	a = SBCreds()
	b = [dict(id=row[0], uname=row[1], paswd=row[2], create=row[3], val=row[4]) \
		for row in db.session.query(ContentCredentials.credentialID, ContentCredentials.username, ContentCredentials.password, ContentCredentials.created, ContentCredentials.valid).filter(ContentCredentials.contentID.in_([ContentID]))]
	if not b:
		return None
	a.id = b[0]["id"]
	a.username = b[0]["uname"]
	a.password = b[0]["paswd"]
	a.created = b[0]["create"]
	a.instanceID = ContentID
	a.valid = b[0]["val"]
	c = [dict(id=row[0], stat=row[1], date=row[2], score=row[3], pid=row[4]) \
		for row in db.session.query(ContentCredentialStatus.contentCredentialStatusID, ContentCredentialStatus.status, ContentCredentialStatus.datetime, ContentCredentialStatus.score, ContentCredentialStatus.playerID).filter(ContentCredentialStatus.credentialID.in_([a.id])).order_by(ContentCredentialStatus.datetime)]
	if c:
		d = SBCredsStatus()
		d.id = c[0]["id"]
		d.date = c[0]["date"]
		d.status = c[0]["stat"]
		d.pid = c[0]["pid"]
		d.score = c[0]["score"]
		d.instanceID = a.id
		a.status = d
	return a

def getFlag(FlagID):
	a = SBFlag()
	b = [dict(tid=row[0], gid=row[1], name=row[2], val=row[3], ans=row[4], pt=row[5]) \
		for row in db.session.query(Flags.blueteamID, Flags.gameID, Flags.name, Flags.value, Flags.answer, Flags.points).filter(Flags.flagID.in_([FlagID]))]
	if not b:
		return None
	a.id = FlagID
	a.gameID = b[0]["gid"]
	a.teamID = b[0]["tid"]
	a.name = b[0]["name"]
	a.value = b[0]["val"]
	a.answer = b[0]["ans"]
	a.points = b[0]["pt"]
	a.found = getFlagFound(FlagID)
	a.stolen = getFlagStolen(FlagID)
	return a
def getFlagStolen(FlagID):
	a = SBFlagAct()
	b = [dict(id=row[0], pid=row[1], date=row[2], act=row[3]) \
		for row in db.session.query(FlagsStolen.flagStolenID, FlagsStolen.playerID, FlagsStolen.datetime, FlagsStolen.activity).filter(FlagsStolen.flagID.in_([FlagID]))]
	if not b:
		return None
	a.flagID = FlagID
	a.id = b[0]["id"]
	a.activity = b[0]["act"]
	a.datetime = b[0]["date"]
	a.playerID = b[0]["pid"]
	return a
def getFlagFound(FlagID):
	a = SBFlagAct()
	b = [dict(id=row[0], pid=row[1], date=row[2], act=row[3]) \
		for row in db.session.query(FlagsFound.flagFoundID, FlagsFound.playerID, FlagsFound.datetime, FlagsFound.activity).filter(FlagsFound.flagID.in_([FlagID]))]
	if not b:
		return None
	a.flagID = FlagID
	a.id = b[0]["id"]
	a.activity = b[0]["act"]
	a.datetime = b[0]["date"]
	a.playerID = b[0]["pid"]
	return a
