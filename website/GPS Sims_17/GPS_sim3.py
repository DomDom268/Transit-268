import requests
import time
import ast
import os
from dotenv import load_dotenv

load_dotenv() #Load environment variables from .env file    
URL = 'http://127.0.0.1:5000/location'

your_api_key = os.getenv('VEHICLE_3_KEY') #API key for authentication, generated when vehicle is added to database. Can be found in the vehicles table in the database
with open('website/GPS Sims_17/coords2.txt', 'r') as f:
    list_of_coords = f.read()

route17 = ast.literal_eval(list_of_coords)
route18 = route17[::-1]

i = 0 
direction = 1 #1 = Forward, -1=Reverse
while True:
    lat,lon = route18[i]
    route_id = 18 if direction == 1 else 17

    payload = {
        "vehicle_id":3,
        "vehicle_plate":"TEST125",
        "vehicle_name":"Bebe",
        "route_id":route_id,
        "latitude": lat,
        "longitude": lon,
        "speed": 30,
        "last_updated":time.time()
        }
    
    requests.post(URL,json=payload,headers={'X-API-KEY': your_api_key}) #Send request to html to add payload to db

    if i == len(route18) - 1:
        direction = -1
    elif i == 0:
        direction = 1
    
    i+= direction
    time.sleep(5)