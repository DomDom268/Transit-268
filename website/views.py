from flask import Blueprint, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .models import db, Vehicle, Stops, Routes,Routes_Stops
from datetime import datetime, timezone
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app as app
from sqlalchemy import text
import logging

views = Blueprint('views', __name__)
limiter = Limiter(key_func=get_remote_address, app=app) # Apply rate limit to all routes in this blueprint

@views.route('/')
def home():
    return "Welcome to the Transit Tracker API! Please refer to the documentation for available endpoints."

@views.route('/register',methods = ['POST']) #Driver registers bus
@limiter.limit("5 per minute") # Limit to 5 requests per minute
def add_vehicles():
    try:
        logging.info(f"Received request to /register with data: {request.json}")
        api_key = request.headers.get('X-API-KEY')
        if not api_key:
            logging.warning("API key missing in request to /register")
            return jsonify({"error": "API key is required"}), 401

        data = request.json
        if data is None:
            logging.warning("No data received in request to /register")
            return jsonify({"error":"no data received"}), 400
        
        vehicle = Vehicle(
            vehicle_id = data.get('vehicle_id'),
            vehicle_plate = data.get('vehicle_plate'),
            vehicle_name = data.get('vehicle_name'),
            route_id = data.get('route_id'),
            latitude = data.get('latitude'),
            longitude = data.get('longitude'),
            speed = data.get('speed'),
            last_updated = datetime.now(timezone.utc)   
        )
        db.session.add(vehicle)
        safe_commit()   
        logging.info(f"Vehicle {vehicle.vehicle_id} registered successfully with API key {api_key}")
        return jsonify({'message':'vehicle added'})
    
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Database error occurred: {str(e)}")
        return jsonify({'database error': str(e)}), 500
    
    except Exception as e:
        db.session.rollback()
        logging.error(f"Unexpected error occurred: {str(e)}")
        return jsonify({'unexpected error': str(e)}), 500

@views.route('/location', methods = ['POST']) # Receive vehicle location via GPS
@limiter.limit("30 per minute") # Limit to 30 requests per minute
def update_location():
    try:
        logging.info(f"Received location update with data: {request.json}")
        api_key = request.headers.get('X-API-KEY')
        if not api_key:
            logging.warning("API key missing in request to /location")
            return jsonify({'error':'API key is required'}), 401
            
        data = request.json #Request vehicle information
        if data is None:
            logging.warning("No data received in request to /location")
            return jsonify({'error':'no data received'}), 400
        
        vehicle_id = data.get('vehicle_id')
        if not vehicle_id:
            logging.warning("vehicle_id is required in request to /location")
            return jsonify({'error':'vehicle_id is required'}), 400
        
        timestamp = data.get('last_updated')
        last_updated = datetime.fromtimestamp(timestamp) if timestamp else datetime.now(timezone.utc)

        vehicle = Vehicle.query.filter_by(vehicle_id = vehicle_id).first() #Authenticate using API key and find vehicle in database
        if vehicle:
            vehicle.route_id = data.get('route_id')
            vehicle.latitude = data.get('latitude')
            vehicle.longitude = data.get('longitude')
            vehicle.speed = data.get('speed')
            vehicle.last_updated = last_updated
            
        else:
            vehicle = Vehicle(
                vehicle_id = vehicle_id,
                vehicle_plate = data.get('vehicle_plate'),
                vehicle_name = data.get('vehicle_name'),
                route_id = data.get('route_id'),
                latitude = data.get('latitude'),
                longitude = data.get('longitude'),
                speed = data.get('speed'),
                last_updated = last_updated
                )
            db.session.add(vehicle)
        safe_commit() #Commit to database
        logging.info(f"Location for vehicle {vehicle_id} updated successfully with API key {api_key}")
        return jsonify({'status':'success'})
    
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Database error occurred: {str(e)}")
        return jsonify({'database error': str(e)}), 500
    
    except Exception as e:
        db.session.rollback()
        logging.error(f"Unexpected error occurred: {str(e)}")   
        return jsonify({'unexpected error': str(e)}), 500

@views.route('/location/vehicle', methods = ['GET']) #API Endpoint to send latest location to frontend
def get_vehicle_location():
    logging.info("Received request to /location/vehicle with args: " + str(request.args))

    vehicle_id = request.args.get('vehicle_id')
    if not vehicle_id:
        logging.error("vehicle_id is required in request to /location/vehicle")
        return jsonify({'error':'vehicle_id is required'}), 400

    location = Vehicle.query.filter_by(vehicle_id = vehicle_id).first()

    if not location:
        logging.warning(f"No location found for vehicle_id {vehicle_id} in request to /location/vehicle")
        return jsonify({'error':'no location'}), 404

    return jsonify({
        'vehicle_id': vehicle_id,
        'lat' : location.latitude,
        'lon' : location.longitude,
        'timestamp' : location.last_updated
         })

@views.route('/location/all', methods = ['GET']) # API Endpoint to send latest location of all vehicles to frontend
@limiter.limit("5 per minute") # Limit to 5 requests per minute
def get_all_latest():
    logging.info("Received request to /location/all")
    result = []
    vehicles = Vehicle.query.all()

    if vehicles is None:
        logging.warning("No vehicles found in database for /location/all")
        return jsonify({'error':'no vehicles'}), 404
    else:

        for v in vehicles:
            location = Vehicle.query\
            .filter_by(vehicle_id=v.vehicle_id) \
            .order_by(Vehicle.last_updated.desc()) \
            .first()

            if location is None:
                continue
            else:
                result.append({
                    'vehicle_id':v.vehicle_id,
                    'latitude': v.latitude,
                    'longitude': v.longitude,
                    'last_updated': v.last_updated
                })
        logging.info(f"Returning location data for {len(result)} vehicles in response to /location/all")
        return jsonify(result)

@views.route('/vehicles', methods = ['GET'])#API Endpoint to send list of all vehicle_ids
def get_all():
    logging.info("Received request to /vehicles")

    vehicles = Vehicle.query.all()
    if not vehicles:
        logging.warning("No vehicles found in database for /vehicles")
        return jsonify({'error':'no vehicles'}), 404
    else:
        logging.info(f"Returning vehicle data for {len(vehicles)} vehicles in response to /vehicles")
        return jsonify([{
            'vehicle_id':v.vehicle_id,
            'vehicle_name' : v.vehicle_name,
            # 'vehicle_type' : v.vehicle_type,
            'route_id': v.route_id,
            'vehicle_plate':v.vehicle_plate,
            'latitude': v.latitude,
            'longitude': v.longitude
        } for v in vehicles])

@views.route('/vehicles/route',methods = ['GET']) #API Endpoint to send list of all vehicles per route
def vehicle_route():
    logging.info("Received request to /vehicles/routes")
    route_id = request.args.get('route_id',type=int)
    routes = [r.route_id for r in Routes.query.with_entities(Routes.route_id).all()]

    if route_id is None or route_id not in routes:
        logging.error("Invalid route_id or missing route_id in requests to /vehicles/route")
        return jsonify({'error':'invalid route_id or missing route_id'})

    try:
        vehicles = Vehicle.query.filter_by(route_id=route_id).all()
        if vehicles is None:
            return jsonify({"message":"Sorry there are no buses on this route at the moment"})
        else:
            return jsonify([{
                'vehicle_id':v.vehicle_id,
                'vehicle_name' : v.vehicle_name,
                # 'vehicle_type' : v.vehicle_type,
                'route_id': v.route_id,
                'vehicle_plate':v.vehicle_plate,
                'latitude': v.latitude,
                'longitude': v.longitude
            } for v in vehicles])
        
    except Exception as e:
        logging.error(f"Error occurred while fetching vehicles for route_id {route_id} in request to /vehicles/route: {str(e)}")
        return jsonify({'error': str(e)}), 500


@views.route('/routes', methods = ['GET']) #API Endpoint to send list of all routes
def get_routes():
    logging.info("Received request to /routes")

    routes = Routes.query.all()
    if routes is None:
        logging.warning("No routes found in database for /routes")
        return jsonify({'error':'no routes'}), 404
    else:
        logging.info(f"Returning route data for {len(routes)} routes in response to /routes")
        return jsonify([{
            "route_id": routes.route_id,
            "route_name": routes.route_name,
            "direction": routes.direction
        } for routes in routes])

@views.route('/stops', methods = ['GET']) #API Endpoint to send list of all stops per route
def get_stops():
    logging.info("Received request to /stops")
    route_id = request.args.get('route_id', type=int)
    route_ids = [r.route_id for r in Routes.query.all()]

    if route_id is None:
        logging.warning("route_id is required in request to /stops")
        return jsonify({'error':'route_id is required'}), 400
    elif route_id not in route_ids:
        logging.warning("Invalid route_id in request to /stops")
        return jsonify({'error':'invalid route_id'}), 400
    else:

        stops = Routes_Stops.query \
        .join(Stops, Routes_Stops.stop_id == Stops.stop_id) \
        .filter(Routes_Stops.route_id == route_id)\
        .order_by(Routes_Stops.stop_sequence) \
        .all()

        return jsonify([
            {
                "stop_id": s.stop_id,
                "stop_name": s.stop.stop_name,
                "latitude": s.stop.latitude,
                "longitude": s.stop.longitude
            } for s in stops]
        )

@views.route('/stop/location', methods = ['GET']) #API Endpoint to send location of a stop
def stop_location():
    logging.info("Received request to /stop/location with args: " + str(request.args))
    stop_id = request.args.get('stop_id', type=int)
    route_id = request.args.get('route_id', type=int)

    if stop_id is None or route_id is None:
        logging.warning("stop_id and route_id are required in request to /stop/location")
        return jsonify({'error':'stop_id and route_id are required'}), 400
    
    stop = Stops.query.filter_by(route_id = route_id, stop_id = stop_id).first()
    if not stop:
        logging.warning("Stop not found in request to /stop/location")
        return jsonify({'error':'stop not found'}), 404

    return jsonify({
        'stop_id': stop_id,
        'route_id': route_id,
        'lat' : stop.latitude,
        'lon' : stop.longitude
    })

@views.route('/eta', methods = ['GET']) #API ENdpoint to calculate and send the eta of a vehicle
@limiter.limit("30 per minute") # Limit to 30 requests per minute
def eta():
    logging.info("Received request to /eta with args: " + str(request.args))
   #Receive route number and stop id from user
    stop_id = request.args.get('stop_id',type=int)
    route_id = request.args.get('route_id',type=int)

    stop_ids = [s.stop_id for s in Stops.query.all()]
    route_ids = [r.route_id for r in Routes.query.all()]

    if stop_id is None or route_id is None:
        logging.warning("stop_id and route_id are required in request to /eta")
        return jsonify({'error':'stop_id and route_id are required'}), 400
    
    elif stop_id not in stop_ids:
        logging.warning("Invalid stop_id in request to /eta")
        return jsonify({'error':'invalid stop_id'}), 400
    
    elif route_id not in route_ids: 
        logging.warning("Invalid route_id in request to /eta")
        return jsonify({'error':'invalid route_id'}), 400

    #Pull all stops on the route
    stops = (
        Routes_Stops.query
        .join(Stops, Routes_Stops.stop_id == Stops.stop_id)
        .filter(Routes_Stops.route_id == route_id)
        .order_by(Routes_Stops.stop_sequence)   
        .all()
    )

    try:
        #Transform into list for python use
        stops_list = [
            {
            "id":rs.stop_id,
            "lat":rs.stop.latitude,
            "lon":rs.stop.longitude,
            "seq":rs.stop_sequence
            } 
            for rs in stops
        ]
    except:
        logging.warning(f"No stops found for route_id {route_id} in request to /eta")
        return jsonify({'error':'no stops found for route'}), 404
    

    target_stop = next(s for s in stops_list if s['id']==stop_id)
    target_seq = target_stop['seq']

    #Get all vehicles on route
    vehicles = Vehicle.query.filter_by(route_id=route_id).order_by(Vehicle.last_updated.desc()).all()
    eta_list = []
    vehicle_list = []
    # min_eta = float('inf')
    best_vehicle = None
    best_vehicle_location = None
    best_distance = None
    
    if not vehicles:
        logging.warning(f"No vehicles found for route_id {route_id} in request to /eta")
        return jsonify({'message':'No buses found at the moment'}), 200
    
    # distance = 0
    #Investigate all vehicles on route
    for v in vehicles:
        closest_stop = min(stops_list, key=lambda s: haversine(v.latitude, v.longitude, s['lat'], s['lon']))

        direction = 1 if route_id == 17 or route_id == 14 else -1

        if (closest_stop['seq'] -  target_seq) * direction > 0:
            logging.info(f"Vehicle {v.vehicle_id} is past the target stop in request to /eta, skipping")
            continue
        
        #Calculate distance from bus to closest stop
        distance = 0
        distance = haversine(v.latitude,v.longitude,closest_stop['lat'],closest_stop['lon'])

        # Calculate distance from closest stop to target stop
        for i in range(len(stops_list) - 1):
            s1 = stops_list[i]
            s2 = stops_list[i+1]

            # if s1['seq'] >= closest_stop['seq'] and s2['seq'] <= target_seq:
            if (s1['seq'] - closest_stop['seq']) * direction >= 0 and (target_seq - s1['seq']) * direction >= 0:
                logging.info(f"Calculating distance from stop {s1['id']} to stop {s2['id']} for vehicle {v.vehicle_id} in request to /eta")
                distance += haversine(s1['lat'],s1['lon'],s2['lat'],s2['lon'])

        #Calculate ETA
        speed = v.speed if v.speed > 5 else 25
        eta = (distance / speed) * 60 #Convert to minutes
        vehicle_list.append(v.vehicle_id)
        eta_list.append(eta)

    eta_data = zip(vehicle_list, eta_list)
    eta_data_sorted = sorted(eta_data, key=lambda x: x[1])
    eta_output = [{'vehicle_id': v_id, 'eta_minutes': round(eta, 2)} for v_id, eta in eta_data_sorted]

    return jsonify(eta_output)

@views.route('/health', methods = ['GET']) #Health check endpoint
def health():
    try:
        db.session.execute(text('SELECT 1')) # Simple query to check database connectivity
        logging.info("Health check successful: Database connection is healthy")
        return jsonify({'status':'ok', 'database':'healthy'})
    
    except Exception as e:
        logging.error("Health check failed: Database connection is not healthy")
        return jsonify({'status':'error', 'database':'unhealthy'}), 500

def haversine(latV,lonV,latU,lonU):
    import math
    R = 6371.01 #Earth's radius in kilometers

    phiU = math.radians(latU)
    phiV = math.radians(latV)
    lambdaU = math.radians(lonU)
    lambdaV = math.radians(lonV)

    dphi = phiV-phiU
    dlambda = lambdaV-lambdaU

    a = math.sin(dphi/2)**2 + \
    math.cos(phiV) * math.cos(phiU) * math.sin(dlambda/2)**2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    d = R * c

    return d

def safe_commit():
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e


