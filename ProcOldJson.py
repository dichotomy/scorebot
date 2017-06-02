#!/usr/bin/env python2

import json


class ProcOldJson(object):

    def __init__(self, filename):
        self.filename = filename
        self.file = open(filename)
        self.json_obj = json.load(self.file)
        self.teams = []
        if "blueteams" in self.json_obj:
            for team in self.json_obj["blueteams"]:
                self.teams.append(team["name"])
        else:
            raise Exception("Invald JSON, no teams!")

    def get_teams(self):
        return self.teams

    def get_hosts(self, team):
        if team in self.teams:
            hosts = []
            for host in self.json_obj["blueteams"][self.teams.index(team)]["hosts"]:
                hosts.append(host["hostname"])
            return hosts
        else:
            raise Exception("Unknown team %s!" % team)

    def get_dns(self, team):
        if team in self.teams:
            return self.json_obj["blueteams"][self.teams.index(team)]["dns"]

    def get_services(self, team, host):
        if team in self.teams:
            hosts_json = self.json_obj["blueteams"][self.teams.index(team)]["hosts"]
            for this_host in hosts_json:
                if host == this_host["hostname"]:
                    services = []
                    for service in this_host["services"]:
                        port = service["port"]
                        protocol = service["protocol"]
                        services.append("%s/%s" % (port, protocol))
                    return services
            raise Exception("Unknown host %s!" % host)
        else:
            raise Exception("Unknown team %s!" % team)

if __name__ == "__main__":
    import sys
    filename = sys.argv[1]
    poj = ProcOldJson(filename)
    teams = poj.get_teams()
    for team in teams:
        print team
        print "\tDNS: %s" % poj.get_dns(team)
        hosts = poj.get_hosts(team)
        for host in hosts:
            print "\t%s" % host
            for service in poj.get_services(team, host):
                print "\t\t%s" % service
