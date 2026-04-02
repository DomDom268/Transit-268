import streamlit as st
import requests

st.set_page_config(layout="centered") #Center the content on the page

st.title('Transit Tracker 268') 
st.write('Welcome to the Transit Tracker 268! This application allows you to track public transit vehicles in real-time and calculate their estimated time of arrival (ETA) at your location. No more guessing ever!')


st.sidebar.header('Select Your Route and Stop')
routes = requests.get('http://localhost:5000/routes').json() #Fetch routes from the backend API
route_options = {f"{r['route_name']} ({r['direction']})": r['route_id'] for r in routes} #Create a dictionary mapping route names to route IDs for the dropdown menu

selected_route_name = st.sidebar.selectbox("Select Route", list(route_options.keys())) #Create a dropdown menu in the sidebar for selecting a route, using the route names as options
selected_route_id = route_options[selected_route_name] #Get the route ID corresponding to the selected route name from the route_options dictionary, which will be used to fetch the stops for that route

# Fetch stops for this route
stops = requests.get(f"http://localhost:5000/stops?route_id={selected_route_id}").json() #Fetch stops for the selected route from the backend API, using the selected route ID as a query parameter
stop_options = {s['stop_name']:s["stop_id"] for s in stops}
# stop_names = [stop['stop_name'] for stop in stops]
selected_stop_name = st.sidebar.selectbox('Select a stop', list(stop_options.keys())) #Create a dropdown menu in the sidebar for selecting a stop, using the stop names as options. The stop names are extracted from the stops data fetched from the backend API and stored in the stop_options dictionary, which maps stop names to stop IDs for later use when calculating ETA.
selected_stop_id = stop_options[selected_stop_name] # Get the stop ID corresponding to the selected stop name from the stop_options dictionary, which will be used to calculate the ETA for the selected route and stop.

stop = next(stop for stop in stops if stop['stop_name'] == selected_stop_name) #Find the stop object in the stops list that matches the selected stop name. This is done using a generator expression that iterates through the stops and returns the first stop whose 'stop_name' matches the selected stop name. The resulting stop object contains information about the selected stop, including its stop ID, which will be used to calculate the ETA for the selected route and stop.

st.write(f"You selected route {selected_route_id} and {selected_stop_name}.Calculating ETA...")

eta_call = requests.get(f"http://localhost:5000/eta?route_id={selected_route_id}&stop_id={stop['stop_id']}") #Make a GET request to the backend API to calculate the ETA for the selected route and stop. The request includes the selected route ID and stop ID as query parameters. The response from the API is expected to contain the ETA information, which will be displayed to the user. The status code of the response is checked to ensure that the request was successful before processing the ETA data.s
if eta_call.status_code == 200:
    eta = eta_call.json()
    for i in range(len(eta['eta_minutes'])):
        eta_info = eta['eta_minutes'][i]
        vehicle_id = eta['vehicle_id'][i]
        if eta_info >= 1:
            st.write(f"Bus {vehicle_id} {eta_info} minutes.")
        elif eta_info < 1:
            st.write(f"Bus {vehicle_id} now.")
    # if 'eta_minutes' not in eta.keys():
    #     st.write(f"Sorry, we couldn't calculate the ETA for route {selected_route_id} at {selected_stop_name} at this time.")
    # elif eta['eta_minutes'] >= 1:
    #     st.write(f"Bus {eta['vehicle_id']}  on route {selected_route_id} is expected to arrive at {selected_stop_name} in {eta['eta_minutes']} minutes.")
    #     # st.write(f"{eta}")
    # elif eta['eta_minutes'] < 1:
    #     st.write(f"Bus {eta['vehicle_id']} on route {selected_route_id}  is expected to arrive at {selected_stop_name} now.")
        
    