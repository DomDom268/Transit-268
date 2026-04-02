import requests
import time
import ast


URL = "http://127.0.0.1:5000/location" #Backend url


with open('coords2.txt', 'r') as f:
    list_of_coords = f.read()

route = ast.literal_eval(list_of_coords)


i=0

direction = 1 #1 = Forward, -1=Reverse
while True:
    
    lat,lon = route[i]
    
    payload = {
        'vehicle_id' : 2,
        'vehicle_plate' : 'TEST124',
        'vehicle_name' : 'Stecy',
        'route_id': 17,
        'latitude' : lat,
        'longitude' : lon,
        'speed': 20,
        'last_updated' : time.time()
    }
    requests.post(URL,json=payload) #Send request to html to add payload to db
    
    #Start route again from end
    if i == len(route) - 1:
        direction = -1
    elif i ==0:
        direction = 1
    
    i+= direction
    time.sleep(5)