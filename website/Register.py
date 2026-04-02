import requests
import secrets

URL ="http://127.0.0.1:5000/register"

def register_vehicle(vehicle_id: int, vehicle_plate: str, vehicle_name: str, route_id: int, latitude: float, longitude: float, speed: float, api_key=secrets.token_hex(16)):
    data = {
        'vehicle_id': vehicle_id,
        'vehicle_plate': vehicle_plate,
        'vehicle_name': vehicle_name,
        'route_id': route_id,
        'latitude': latitude,
        'longitude': longitude,
        'speed': speed,
        'api_key': api_key
    }
    response = requests.post(URL, json=data, headers={'X-API-KEY': api_key})
    return response.status_code

if register_vehicle(9,'TEST131','Rags',17,0.0,0.0,35.0) == 200:
    print('Vehicle registered successfully!')
else:    
    print('Failed to register vehicle.')
