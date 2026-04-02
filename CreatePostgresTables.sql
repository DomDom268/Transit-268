
CREATE TABLE vehicles (
vehicle_id SERIAL PRIMARY KEY,
vehicle_name TEXT,
vehicle_plate TEXT,
route_id INTEGER REFERENCES routes(route_id),
latitude REAL,
longitude REAL,
speed REAL,
last_updated TIMESTAMP
);

