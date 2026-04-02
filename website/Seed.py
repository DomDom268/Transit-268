import requests
import csv
from website import db, create_app
from .models import Routes, Stops, Routes_Stops
from sqlalchemy.exc import SQLAlchemyError

def safe_commit():
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e

def get_coords(filename):
    """Reads from coords2.txt to get the list of coordinates along the route between
      the start and end points. Uses OSRM API to get the route geometry between the two
        points and returns a list of (lat,lon) tuples representing the coordinates along the route."""
    
    coords = []
    # route = []
    with open(filename, 'r') as f:
        list_of_coords = f.read()
    
    coords = eval(list_of_coords)
    # route = coords[::-1]
    return coords

def load_route():
    with open('routes.csv','r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            existing = Routes.query.filter_by(route_id=row['route_id']).first()
            if not existing:
                route = Routes(
                    route_id=row['route_id'],
                    route_name=row['route_name'],
                    direction=row['direction']
                )
                db.session.add(route)
    db.session.commit()

def generate_stops(coords,spacing=300):
    """Takes the list of coords along a route and generate stops every 300 meters"""

    from geopy.distance import geodesic
    stops =[]
    last_point = coords[0]
    stops.append(last_point)

    for point in coords[1:]:
        if geodesic(last_point,point).meters >= spacing:
            stops.append(point)
            last_point = point
    return stops
    
def load_stops(route_id,stops):
    try:
        route = Routes.query.filter_by(route_id=route_id).first()
        if not route:
            raise ValueError(f"Route with id {route_id} does not exist")
        
        db_len = Stops.query.count()
        for i,(lat,lon) in enumerate(stops):
            stop = Stops(stop_id=db_len+i,stop_name=f' Stop {i+1}', latitude=lat,longitude=lon, route_id=route_id)
            db.session.merge(stop)
        
            rs = Routes_Stops(id=db_len+i,route_id=route_id, stop_id=stop.stop_id, stop_sequence=i+1)
            db.session.add(rs)
        safe_commit()

    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error loading stops: {e}")
    
    except Exception as e:
        print(f"Error: {e}")

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        # load_route()

        coords = get_coords('coords14.txt')
        stops = generate_stops(coords, spacing=300)
        load_stops(route_id=13, stops=stops)