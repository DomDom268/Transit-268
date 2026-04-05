import requests
import time
import ast
import os
from dotenv import load_dotenv  

load_dotenv() #Load environment variables from .env file
URL = "http://127.0.0.1:5000/location" #Backend url

your_api_key = os.getenv('VEHICLE_7_KEY') #API key for authentication, generated when vehicle is added to database. Can be found in the vehicles table in the database
with open('website/GPS Sims_14/coords14.txt', 'r') as f:
    list_of_coords = f.read()

route = ast.literal_eval(list_of_coords)
route13 = route[::-1]

i=0
direction = 1 #1 = Forward, -1=Reverse
while True:
    
    lat,lon = route13[i]
    route_id = 13 if direction ==1 else 14
    
    payload = {
        'vehicle_id' : 7,
        'vehicle_plate' : 'TEST129',
        'vehicle_name' : 'Pumpy Dan',
        # 'vehicle_type' : 'Bus',
        'route_id': route_id,
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