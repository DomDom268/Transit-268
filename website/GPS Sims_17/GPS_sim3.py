import requests
import time

URL = 'http://127.0.0.1:5000/location'
with open('coords2.txt', 'r') as f:
    list_of_coords = f.read()

route17 = eval(list_of_coords)
route18 = route17[::-1]

i = 0 
direction = 1 #1 = Forward, -1=Reverse
while True:
    lat,lon = route18[i]

    payload = {
        "vehicle_id":3,
        "vehicle_plate":"TEST125",
        "vehicle_name":"Bebe",
        "route_id":18,
        "latitude": lat,
        "longitude": lon,
        "speed": 30,
        "last_updated":time.time()
        }
    
    requests.post(URL,json=payload)

    if i == len(route18) - 1:
        direction = -1
    elif i == 0:
        direction = 1
    
    i+= direction
    time.sleep(5)