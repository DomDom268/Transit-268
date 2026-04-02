import requests
import time
import ast


URL = "http://127.0.0.1:5000/location" #Backend url

your_api_key = '596ee5e5114cd0d5410fc3bf06d4f269' #API key for authentication, generated when vehicle is added to database. Can be found in the vehicles table in the database
with open('coords14.txt', 'r') as f:
    list_of_coords = f.read()

route = ast.literal_eval(list_of_coords)
route18 = route[::-1]

i=0
direction = 1 #1 = Forward, -1=Reverse
while True:
    
    lat,lon = route18[i]
    
    payload = {
        'vehicle_id' : 5,
        'vehicle_plate' : 'TEST127',
        'vehicle_name' : 'Garfield',
        # 'vehicle_type' : 'Bus',
        'route_id': 18,
        'latitude' : lat,
        'longitude' : lon,
        'speed': 25,
        'last_updated' : time.time()
    }
    requests.post(URL,json=payload,headers={'X-API-KEY': your_api_key}) #Send request to html to add payload to db
    
    #Start route again from end
    if i == len(route) - 1:
        direction = -1
    elif i ==0:
        direction = 1
    
    i+= direction
    time.sleep(5)