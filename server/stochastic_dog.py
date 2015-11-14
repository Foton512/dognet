#!/usr/bin/env python

import urllib2
import time
import hashlib

apiUrl = "http://188.166.64.150:8000/api/collar/add_point/?collar_id_hash={collarHash}&timestamp={time}&lat={lat}&lon={lon}"
#apiUrl = "http://127.0.0.1:8000/api/collar/add_point/?collar_id_hash={collarHash}&timestamp={time}&lat={lat}&lon={lon}"

step = 0.00005

dogs = {
    5: {
        "collar": 15,
        "pos": (57.625329, 39.885215),
    }
}


def advance(pos):
    print pos
    pos = (pos[0] + step, pos[1])
    return pos


def send(pos, collarId):
    url = apiUrl.format(
        time=int(time.time()),
        lat=pos[0],
        lon=pos[1],
        collarHash=hashlib.md5(str(collarId)).hexdigest(),
    )
    print url
    urllib2.urlopen(url)


while True:
    for dogId, dogData in dogs.items():
        pos = dogData["pos"]
        pos = advance(pos)
        send(pos, dogData["collar"])
        dogData["pos"] = pos

        time.sleep(1)