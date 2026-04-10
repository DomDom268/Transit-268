from .import db
import secrets
from datetime import datetime, timezone

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    
    vehicle_id = db.Column(db.Integer, primary_key =True, unique = True, nullable = False)
    vehicle_plate = db.Column(db.String(30),unique = True, nullable = False)
    vehicle_name = db.Column(db.String(50))
    route_id = db.Column(db.Integer, db.ForeignKey('routes.route_id'))
    latitude = db.Column(db.Integer)
    longitude = db.Column(db.Integer)
    speed = db.Column(db.Float)
    last_updated = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    api_key = db.Column(db.String,unique = True, nullable = False, default = lambda: secrets.token_hex(16))

    def __repr__(self):
        return f"<Vehicle {self.vehicle_id} ({self.latitude},{self.longitude})>"

class Stops(db.Model):
    __tablename__ = 'stops'
    

    stop_id = db.Column(db.Integer,primary_key = True)
    stop_name = db.Column(db.String(50), nullable = False)
    latitude = db.Column(db.Float,nullable = False)
    longitude = db.Column(db.Float, nullable = False)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.route_id'), nullable = False)

    def __repr__(self):
        return f"< {self.stop_name} ({self.latitude}, {self.longitude})>"
    
class Routes(db.Model):
    __tablename__ = 'routes'

    route_id = db.Column(db.Integer,primary_key = True)
    route_name = db.Column(db.String(50), nullable = False)
    direction = db.Column(db.String(30), nullable = False)
    

def __repr__(self):
    return f"<{self.route_number}: {self.route_name}>"

class Routes_Stops(db.Model):
    __tablename__ = 'routes_stops'

    id = db.Column(db.Integer,primary_key = True)
    route_id = db.Column(db.Integer,db.ForeignKey('routes.route_id'),nullable = False)
    stop_id = db.Column(db.Integer, db.ForeignKey('stops.stop_id'),nullable = False)
    stop_sequence = db.Column(db.Integer, nullable = False)

    stop = db.relationship('Stops')
   