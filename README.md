# Transit Tracker MVP

## Overview

This project is a Minimum Viable Product (MVP) of a public transit
tracking system for Antigua and Barbuda. It provides real-time tracking
of buses across multiple routes and calculates estimated arrival times
(ETA) for users based on live vehicle data.

## Features

-   Real-time bus location tracking
-   Multiple route support
-   ETA calculation using Haversine distance
-   API-based backend with Flask
-   PostgreSQL database for persistent storage
-   Streamlit frontend for user interaction

## Tech Stack

-   **Backend:** Flask (Python)
-   **Database:** PostgreSQL
-   **Frontend:** Streamlit
-   **Other Tools:** SQLAlchemy, Requests

## How It Works

1.  Vehicles (buses) send GPS data to the `/location` endpoint.
2.  The backend stores and updates vehicle positions in PostgreSQL.
3.  Users select a route and stop via the Streamlit interface.
4.  The system calculates the closest bus and estimates arrival time
    using Haversine distance.

## Project Structure

    website/
      models.py
      views.py
      __init__.py

      scripts/
        Seed.py
        Register.py

      Coords/
        coords2.txt
        coords14.txt

      GPS Sims_14
      GPS Sims_17

      Routes/
        routes.csv

    README.md
    streamlit_app.py
    main.py
    requirements.txt

## Setup Instructions

### 1. Clone the repository

    git clone <your-repo-url>
    cd transit-tracker

### 2. Install dependencies

    pip install -r requirements.txt

### 3. Set environment variables

Create a `.env` file:

    DATABASE_URL=your_postgres_connection
    SECRET_KEY=your_secret_key

### 4. Run the backend

    python run.py

### 5. Run the frontend

    streamlit run app.py

## API Endpoints

### POST /location

Receives vehicle GPS data and updates row in Postgres database.

### POST /register

Recieves bus registration information. Id, Name, License Plate, Lat, Lon, Speed, API Key.

### GET /location/all

Returns the locations of all active buses.

### GET /vehicles/route

Returns a list of all active vehicles on selected route

### GET /vehicles

Returns a list of all active vehicles.

### GET /routes

Returns a list of all route ids and route names in Postgres database.

### GET /stops

Retutns a list of all stop ids, stop names and stop locations in Postgres database.

### GET /eta

Returns estimated arrival time for a selected route and stop.

### GET /health

Checks if the API and database are running.

## Future Improvements

-   Route visualization on a map
-   More accurate ETA using route geometry
-   Deployment to cloud infrastructure
-   React Frontend for a more interactive user experience

## Notes

This is an MVP and is designed to demonstrate core functionality of a
scalable transit tracking system.
