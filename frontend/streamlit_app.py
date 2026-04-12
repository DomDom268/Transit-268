import logging
import streamlit as st
import requests
import os
import pandas as pd
import pydeck as pdk
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

API = os.getenv('PUBLIC_API_URL')
MAP_API =os.getenv('MAP_API')
st.set_page_config(page_title="Transit 268",layout="wide") #Center the page title and set the layout to wide for better use of screen space

#AUTO REFRESH EVERY 30 SECONDS
st_autorefresh(interval=30000,key="refresh") 

#WEBSITE HEADER
st.title('Transit Tracker 268') 
st.caption("Real time bus arrivals")

#CACHED FUNCTIONS
@st.cache_data()
def get_routes():
    return requests.get(f'https://{API}/routes').json() 

@st.cache_data()
def get_stops(route_id):
    return requests.get(f"https://{API}/stops?route_id={route_id}").json()

@st.cache_data()
def get_stop_location(stop_id, route_id):
    return requests.get(f"https://{API}/stop/location?stop_id={stop_id}&route_id={route_id}").json()

@st.cache_data()
def stop_to_df(stops):
    data = {
        "stop_id":[s['stop_id'] for s in stops],
        "stop_name":[s['stop_name'] for s in stops],
        "lon":[s['lon'] for s in stops],
        "lat":[s['lat'] for s in stops]
    }

    return pd.DataFrame(data)

def get_vehicle_location(route_id,vehicle_ids:list):
    locs = []
    vehicles = requests.get(f"https://{API}/vehicles/route?route_id={route_id}").json()

    for v in vehicles:
        if v['vehicle_id'] in vehicle_ids:
            locs.append(v)
    
    return locs


#USER INPUTS
col1,col2 = st.columns(2)

routes = get_routes()
route_options = {f"{r['route_name']} ({r['direction']})": r['route_id'] for r in routes} 

with col1:
    st.subheader("Select Route") 
    selected_route_name = st.selectbox(label="Select Route", placeholder="Select Route", options=list(route_options.keys()),key="route") 

selected_route_id = route_options[selected_route_name] 

# Fetch stops for this route
stops = get_stops(selected_route_id)
stop_options = {s['stop_name']:s["stop_id"] for s in stops}

with col2:
    st.subheader("Select a Stop") 
    selected_stop_name = st.selectbox(label="Select a Stop", placeholder="Select a stop", options=list(stop_options.keys()),key="stop") 

selected_stop_id = stop_options[selected_stop_name] 

stop = next(stop for stop in stops if stop['stop_name'] == selected_stop_name)

#ETA + MAP SECTION
live_section = st.empty() #Create an empty container in the Streamlit app to hold the live section of the application

with live_section.container():
    if selected_route_id and selected_stop_id:

        st.markdown(f"### Calculating Next Arrivals...⌚") #Display a message indicating that the application is calculating the next arrivals for the selected route and stop. This message is shown while the application makes a request to the backend API to calculate the ETA for the selected route and stop.
        
        eta_call = requests.get(f"https://{API}/eta?route_id={selected_route_id}&stop_id={stop['stop_id']}") #Make a GET request to the backend API to calculate the ETA for the selected route and stop. The request includes the selected route ID and stop ID as query parameters. The response from the API is expected to contain the ETA information, which will be displayed to the user. The status code of the response is checked to ensure that the request was successful before processing the ETA data.s
        if eta_call.status_code == 200:
            eta = eta_call.json()

            if not eta:
                st.warning(f"There are no upcoming buses for route {selected_route_id} at {selected_stop_name} at this time.")
    
            else:
                # st.write(eta)
                next_bus = eta[0]['eta_minutes']

                st.metric("Next Bus Arrival", value=f"{round(next_bus,0)} minutes" if next_bus >= 1 else "Now") #Display the ETA for the next bus arrival using a metric component. The label is set to "Next Bus Arrival" and the value is formatted to show the ETA in minutes if it is greater than or equal to 1 minute, or "Now" if the ETA is less than 1 minute.
        
                for i in range(1,len(eta)):
                    eta_info = eta[i]['eta_minutes']
                    if eta_info >= 1:
                        st.write(f"{round(eta_info,0)} minutes.")
                    elif eta_info < 1:
                        st.write("Now")

    
            #Collect locations for stops and next buses
            stop_loc = get_stop_location(selected_stop_id, selected_route_id)
            ids = [v['vehicle_id'] for v in eta]
            vehicle_locs = get_vehicle_location(selected_route_id, ids)
            # vehicle_locs = []
            # for id in eta['vehicle_id']:
            #     loc = requests.get(f"http://localhost:5000/location/vehicle?vehicle_id={id}").json()
            #     vehicle_locs.append(loc)


            data = {
                "name":[stop['stop_id']] + ids,
                "lon":[stop_loc['lon']] + [loc['longitude'] for loc in vehicle_locs],
                "lat":[stop_loc['lat']] + [loc['latitude'] for loc in vehicle_locs]
            }

            map_data = pd.DataFrame(data)

            #ICON SETUP
            if selected_route_id == 17 or selected_route_id == 18:
                bus_icon_url = "https://upload.wikimedia.org/wikipedia/commons/a/aa/Bus_icon_d_green.jpg"
            else:
                bus_icon_url = "https://upload.wikimedia.org/wikipedia/commons/1/11/Bus_icon_red.jpg"
                
            bus_icon = {
                "url": bus_icon_url,
                "width": 128,
                "height": 128,
                "anchorY": 128
            }

            user_icon = {
                "url":"https://upload.wikimedia.org/wikipedia/commons/7/74/Location_icon_from_Noun_Project.png",
                "width": 128,
                "height": 128,
                "anchorY": 128
            }

            map_data['icon_data'] = None
            map_data['icon_data'] = [user_icon] + [bus_icon] * (len(map_data)-1)

            df = stop_to_df(stops)

            pathLayer = pdk.Layer(
                type='PathLayer',
                data=df,
                pickable=True,
                width_scale=20,
                width_min_pixels=2,
                get_path="path",
                get_width=5,
            )

            iconLayer = pdk.Layer(
                type='IconLayer',
                data=map_data,
                get_icon='icon_data',
                get_size=4,
                size_scale=15,
                get_position='[lon, lat]',
            )

            view_state = pdk.ViewState(
                longitude=map_data['lon'].mean(),
                latitude=map_data['lat'].mean(),
                zoom=12,
                pitch=0,
            )

            deck = pdk.Deck(
                layers=[iconLayer,pathLayer],
                map_provider="mapbox",
                map_style='mapbox://styles/mapbox/streets-v11',
                api_keys={'mapbox': MAP_API},
                initial_view_state=view_state,
            )

            st.markdown("### 📍 Live Map")
            st.pydeck_chart(deck)
            st.caption("Last updated at: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            # st.write(map_data)

        else:
            logging.warning(f"Failed to fetch ETA data: {eta_call.status_code}")
            st.error("Sorry, we couldn't fetch the ETA data at this time. Please try again later.")
    else:
        st.warning("No active buses on this route.")
