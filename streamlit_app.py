import streamlit as st
import requests
import os
import pandas as pd
import pydeck as pdk
from datetime import datetime


st.set_page_config(page_title="Transit 268",layout="wide") #Center the page title and set the layout to wide for better use of screen space

st.title('Transit Tracker 268') 
st.caption("Real time bus arrivals")

col1,col2 = st.columns(2)

routes = requests.get('http://localhost:5000/routes').json() #Fetch routes from the backend API
route_options = {f"{r['route_name']} ({r['direction']})": r['route_id'] for r in routes} #Create a dictionary mapping route names to route IDs for the dropdown menu

with col1:
    st.subheader("Select Route") #Display a subheader in the first column to indicate that the user should select a route and stop from the dropdown menus below
    selected_route_name = st.selectbox(label="Select Route", placeholder="Select Route", options=list(route_options.keys())) #Create a dropdown menu in the sidebar for selecting a route, using the route names as options

selected_route_id = route_options[selected_route_name] #Get the route ID corresponding to the selected route name from the route_options dictionary, which will be used to fetch the stops for that route

# Fetch stops for this route
stops = requests.get(f"http://localhost:5000/stops?route_id={selected_route_id}").json() #Fetch stops for the selected route from the backend API, using the selected route ID as a query parameter
stop_options = {s['stop_name']:s["stop_id"] for s in stops}
# stop_names = [stop['stop_name'] for stop in stops]

with col2:
    st.subheader("Select a Stop") #Display a subheader in the second column to indicate that the next arrivals for the selected route and stop will be displayed below
    selected_stop_name = st.selectbox(label="Select a Stop", placeholder="Select a stop", options=list(stop_options.keys())) #Create a dropdown menu in the sidebar for selecting a stop, using the stop names as options. The stop names are extracted from the stops data fetched from the backend API and stored in the stop_options dictionary, which maps stop names to stop IDs for later use when calculating ETA.
selected_stop_id = stop_options[selected_stop_name] # Get the stop ID corresponding to the selected stop name from the stop_options dictionary, which will be used to calculate the ETA for the selected route and stop.

stop = next(stop for stop in stops if stop['stop_name'] == selected_stop_name) #Find the stop object in the stops list that matches the selected stop name. This is done using a generator expression that iterates through the stops and returns the first stop whose 'stop_name' matches the selected stop name. The resulting stop object contains information about the selected stop, including its stop ID, which will be used to calculate the ETA for the selected route and stop.

st.markdown(f"### Calculating Next Arrivals...⌚") #Display a message indicating that the application is calculating the next arrivals for the selected route and stop. This message is shown while the application makes a request to the backend API to calculate the ETA for the selected route and stop.
eta_call = requests.get(f"http://localhost:5000/eta?route_id={selected_route_id}&stop_id={stop['stop_id']}") #Make a GET request to the backend API to calculate the ETA for the selected route and stop. The request includes the selected route ID and stop ID as query parameters. The response from the API is expected to contain the ETA information, which will be displayed to the user. The status code of the response is checked to ensure that the request was successful before processing the ETA data.s
if eta_call.status_code == 200:
    eta = eta_call.json()

    if not eta['eta_minutes']:
        st.warning(f"Sorry, we couldn't calculate the ETA for route {selected_route_id} at {selected_stop_name} at this time.")
    
    else:

        next_bus = eta['eta_minutes'][0]

        st.metric("Next Bus Arrival", value=f"{round(next_bus,0)} minutes" if next_bus >= 1 else "Now") #Display the ETA for the next bus arrival using a metric component. The label is set to "Next Bus Arrival" and the value is formatted to show the ETA in minutes if it is greater than or equal to 1 minute, or "Now" if the ETA is less than 1 minute.
        
        for i in range(1,(len(eta['eta_minutes']))):
            eta_info = round(eta['eta_minutes'][i],0)
            vehicle_id = eta['vehicle_id'][i]
            if eta_info >= 1:
                st.write(f"{eta_info} minutes.")
            elif eta_info < 1:
                st.write(f"Bus {vehicle_id} now.")

        # if 'eta_minutes' not in eta.keys():
        #     st.write(f"Sorry, we couldn't calculate the ETA for route {selected_route_id} at {selected_stop_name} at this time.")
        # elif eta['eta_minutes'] >= 1:
        #     st.write(f"Bus {eta['vehicle_id']}  on route {selected_route_id} is expected to arrive at {selected_stop_name} in {eta['eta_minutes']} minutes.")
        #     # st.write(f"{eta}")
        # elif eta['eta_minutes'] < 1:
        #     st.write(f"Bus {eta['vehicle_id']} on route {selected_route_id}  is expected to arrive at {selected_stop_name} now.")

        #Collect locations for stops and next buses
        stop_loc = requests.get(f"http://localhost:5000/stop/location?stop_id={stop['stop_id']}&route_id={selected_route_id}").json() #Make a GET request to the backend API to fetch the location of the vehicle corresponding to the next bus arrival. The request includes the vehicle ID as a query parameter, which is extracted from the ETA data received from the previous API call. The response from the API is expected to contain the location information for the specified vehicle, which can be used to display the current location of the next bus on a map or provide additional information to the user.
        vehicle_locs = []
        for id in eta['vehicle_id']:
            loc = requests.get(f"http://localhost:5000/location/vehicle?vehicle_id={id}").json()
            vehicle_locs.append(loc)


        data = {
            "name":[stop['stop_id']] + eta['vehicle_id'],
            "lon":[stop_loc['lon']] + [loc['lon'] for loc in vehicle_locs],
            "lat":[stop_loc['lat']] + [loc['lat'] for loc in vehicle_locs]
        }

        map_data = pd.DataFrame(data)
        st.write(map_data)

        st.map(map_data, zoom=12) 


        layer =pdk.Layer(
            'ScatterplotLayer',
            data=map_data,
            get_position='[lon, lat]',
            get_color='[200, 30, 0, 160]',
            get_radius=100,
        )

        view_state = pdk.ViewState(
            longitude=map_data['lon'].mean(),
            latitude=map_data['lat'].mean(),
            zoom=12,
            pitch=0,
        )

        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
        )

        st.pydeck_chart(deck)
else:
    st.warning("No active buses on this route.")
