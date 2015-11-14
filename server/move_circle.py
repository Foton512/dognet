#!/usr/bin/env python

import urllib2
import time
import hashlib
import math
import sys

serverApiUrl = "http://188.166.64.150:8000/api/collar/add_point/?collar_id_hash={collarHash}&timestamp={time}&lat={lat}&lon={lon}"
localApiUrl = "http://127.0.0.1:8000/api/collar/add_point/?collar_id_hash={collarHash}&timestamp={time}&lat={lat}&lon={lon}"
apiUrl = localApiUrl if sys.argv[2] == "local" else serverApiUrl

angle = 0
angleStep = 5. * math.pi / 180
radius = 0.0005
center = (57.625329, 39.885215)
collarId = sys.argv[1]
#collarId = 1

while True:
    angle += angleStep
    print angle
    pos = (center[0] + radius * math.sin(angle), center[1] + radius * math.cos(angle))
    print pos
    url = apiUrl.format(
        time=int(time.time()),
        lat=pos[0],
        lon=pos[1],
        collarHash=hashlib.md5(str(collarId)).hexdigest(),
    )
    print url
    urllib2.urlopen(url)

    time.sleep(1)
