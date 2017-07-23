import datetime
import csv
import random


now = datetime.datetime.now()
timef = '%Y-%m-%d %H:%M:%S'

teams = ['A', 'B', 'C', 'D']
services = ['A_21/tcp', 'A_80/tcp', 'B_80/tcp']
flags = ['1', '2', '3', '4']
stolen_flags = set()
beacons = ['1', '2', '3', '4']
active_beacons = {}

with open('data.csv', 'wb') as fp:
    cfp = csv.writer(fp)
    for _ in xrange(1000):
        for team in teams:
            for service in services:
                state = random.randint(0, 100)
                if state < 60:
                    sstate = 'UP'
                elif state < 90:
                    sstate = 'DOWN'
                else:
                    sstate = 'HALFUP'
                cfp.writerow([now.strftime(timef), team, 'SERVICE', service, sstate])
            for flag in flags:
                key = (team, flag)
                if key in stolen_flags:
                    continue
                if random.randint(0, 100) == 99:
                    sstate = 'STOLEN'
                    stolen_flags.add(key)
                else:
                    sstate = 'SAFE'
                cfp.writerow([now.strftime(timef), team, 'FLAG', flag, sstate])
            for beacon in beacons:
                key = (team, beacon)
                kv = active_beacons.get(key, None)
                if kv:
                    if kv > 1:
                        active_beacons[key] -= 1
                    else:
                        del active_beacons[key]
                    sstate = 'ALIVE'
                else:
                    l = random.randint(0, 200)
                    if l < 10:
                        active_beacons[key] = l
                        sstate = 'ALIVE'
                    else:
                        sstate = 'SILENT'
                cfp.writerow([now.strftime(timef), team, 'BEACON', beacon, sstate])
        now += datetime.timedelta(minutes=5)
