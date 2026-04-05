import requests
import time
import ast
import os
from dotenv import load_dotenv

load_dotenv() #Load environment variables from .env file

URL = "http://127.0.0.1:5000/location" #Backend url

your_api_key = os.getenv('VEHICLE_9_KEY') #API key for authentication, generated when vehicle is added to database. Can be found in the vehicles table in the database
with open('website/GPS Sims_17/coords2.txt', 'r') as f:
    list_of_coords = f.read()

route = ast.literal_eval(list_of_coords)

i=0
direction = 1 #1 = Forward, -1=Reverse
while True:
    
    lat,lon = route[i]
    
    payload = {
        'vehicle_id' : 9,
        'vehicle_plate' : 'TEST131',
        'vehicle_name' : 'Rags',
        # 'vehicle_type' : 'Bus',
        'route_id': 17,
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