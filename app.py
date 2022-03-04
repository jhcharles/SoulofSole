import streamlit as st

import numpy as np
import pandas as pd
import bokeh
import streamlit_bokeh_events
from haversine import haversine, Unit

df = pd.read_csv('raw_artists.csv')

# Introductory section, context

from PIL import Image

image = Image.open('logo.JPG')
st.image(image)

st.markdown("""Use this app to explore which artists are local to you or the place you are interested to learn more about.

Happy scrolling and souling!""")

# Input of user lat and long data

st.markdown("""## Step 1: Input the location you're interested in""")

location_method = st.selectbox('Select a method', ('No selection','Share you location with wifi','Manual input'))

if location_method == "Manual input":
    st.markdown("For hardcoded inputs")

    user_latitude = st.number_input('Insert your latitude',value=51.5)
    user_longitude = st.number_input('Insert your longitude',value=-0.092)

if location_method == "Share you location with wifi":
    st.markdown("For users on laptop with wifi")
    import streamlit as st
    from bokeh.models.widgets import Button
    from bokeh.models import CustomJS
    from streamlit_bokeh_events import streamlit_bokeh_events
    import leafmap.foliumap as leafmap

    loc_button = Button(label="Get Device Location", max_width=150)
    loc_button.js_on_event(
        "button_click",
        CustomJS(code="""
        navigator.geolocation.getCurrentPosition(
            (loc) => {
                document.dispatchEvent(new CustomEvent("GET_LOCATION", {detail: {lat: loc.coords.latitude, lon: loc.coords.longitude}}))
            }
        )
        """),
    )
    result = streamlit_bokeh_events(
        loc_button,
        events="GET_LOCATION",
        key="get_location",
        refresh_on_update=False,
        override_height=75,
        debounce_time=0,
    )
    if result:
        if "GET_LOCATION" in result:
            loc = result.get("GET_LOCATION")
            user_latitude = loc.get("lat")
            user_longitude = loc.get("lon")
            st.write(f"Lat, Lon: {user_latitude}, {user_longitude}")
            m = leafmap.Map(center=(user_latitude, user_longitude), zoom=16)
            m.add_basemap("ROADMAP")
            popup = f"lat, lon: {user_latitude}, {user_longitude}"
            m.add_marker(location=(user_latitude, user_longitude), popup=popup)
            m.to_streamlit()

# Closest artist calculations

if location_method == "No selection":
    st.markdown('Submit a location')

if location_method == "Share you location with wifi" or "Manual input":

    try:
        user_latitude = user_latitude
    except NameError:
        st.markdown("")
    else:
        st.markdown("""## Step 2: Learn about a local artist""")
        df['lat,lon'] = df[[
            'artist_latitude',
            'artist_longitude']].apply(tuple, axis=1)

        user = (user_latitude,user_longitude)


        def localhaversine(X):
            y = haversine(X, user)
            return y

        df['localhaversine'] = df['lat,lon'].apply(localhaversine)

        artist = df[df['localhaversine'] == df['localhaversine'].min()]
        artist_dict = artist.to_dict('r')[0]

        # Closest artist details

        col1, col2 = st.columns(2)

        with col1:
            text1 = "**Artist:** " + artist_dict['artist_name']
            st.markdown(text1)
            text2 = "**Distance from input (km):** " + str(int(artist_dict['localhaversine']))
            st.markdown(text2)
            text3 = "**Website:** " + str(artist_dict['artist_website'])
            st.markdown(text3)
            st.markdown(artist_dict['artist_bio'])

        with col2:
            map_dictionary = {'artist_latitude': 'latitude','artist_longitude': 'longitude'}
            artistmap_df = artist[['artist_latitude','artist_longitude']]
            artistmap_df.rename(columns=map_dictionary, inplace=True)
            artistclean_map_df = artistmap_df[pd.to_numeric(artistmap_df['latitude'],errors='coerce').notnull()]
            st.map(artistclean_map_df)


# st.table(artist)

# Data and details

#map_df = df[['artist_latitude','artist_longitude']]

#map_df.rename(columns=map_dictionary, inplace=True)

#clean_map_df = map_df[pd.to_numeric(map_df['latitude'], errors='coerce').notnull()]

#st.map(clean_map_df)
