import streamlit as st
import pandas as pd
import plotly.express as px
from pymongo import MongoClient
import threading
import os
from bson.json_util import dumps

# MongoDB connection (use environment variable for security)
mongo_uri = os.getenv("MONGO_URI", "mongodb+srv://ranveerverma18:ranveer18@mongo-db-cluster.7xghnej.mongodb.net/spotify_data?retryWrites=true&w=majority")
client = MongoClient(mongo_uri)  # MongoDB URI from environment variable
db = client['spotify_data']  # Your database name

# Print to confirm connection
print("Connected to MongoDB")

# List of relevant collections
collections = ['spotify_liked_songs', 'spotify_user_playlists', 'spotify_top_tracks', 
               'spotify_top_artists', 'spotify_recently_played']

# Streamlit layout
st.title("Spotify Real-Time Dashboard")
st.sidebar.header("Filters")

# Dropdown to select collection
selected_collection = st.sidebar.selectbox("Select Collection", collections)

# Function to fetch data from MongoDB
def fetch_data(collection_name):
    collection = db[collection_name]
    data = collection.find()
    df = pd.DataFrame(list(data))  # Convert MongoDB data to DataFrame
    return df

# Show real-time data
def display_data():
    df = fetch_data(selected_collection)
    if df.empty:
        st.write("No data available.")
    else:
        # Debugging: Force print the DataFrame
        st.write(df.head())  # This will show the first few rows of data
        st.write(f"Current Data from Collection: {selected_collection}")
        st.dataframe(df)
        
        # Example visualizations based on collection
        if selected_collection == 'spotify_liked_songs':
            if 'duration_ms' in df.columns and not df['duration_ms'].empty:
                fig = px.histogram(df, x='duration_ms', title="Song Duration Distribution")
                st.plotly_chart(fig)

        elif selected_collection == 'spotify_top_tracks':
            if 'track_name' in df.columns and 'popularity' in df.columns and not df[['track_name', 'popularity']].empty:
                fig = px.bar(df, x='track_name', y='popularity', title="Top Tracks by Popularity")
                st.plotly_chart(fig)

        elif selected_collection == 'spotify_user_playlists':
            if 'track_count' in df.columns and not df['track_count'].empty:
                fig = px.histogram(df, x='track_count', title="Playlist Track Count Distribution")
                st.plotly_chart(fig)

        elif selected_collection == 'spotify_top_artists':
            if 'artist_name' in df.columns and not df['artist_name'].empty:
                fig = px.bar(df, x='artist_name', title="Top Artists")
                st.plotly_chart(fig)

        elif selected_collection == 'spotify_recently_played':
            if 'played_at' in df.columns and not df['played_at'].empty:
                fig = px.histogram(df, x='played_at', title="Recently Played Tracks")
                st.plotly_chart(fig)

# Function to handle MongoDB change stream and trigger Streamlit refresh
def handle_change(change):
    print(f"Change detected: {dumps(change)}")
    st.experimental_rerun()  # Trigger Streamlit app refresh on change detection

# MongoDB Change Stream Logic for Real-Time Updates
def watch_changes():
    collections_to_watch = ['spotify_liked_songs', 'spotify_recently_played', 
                            'spotify_user_playlists', 'spotify_top_tracks']
    
    change_streams = [db[collection].watch(full_document='updateLookup') for collection in collections_to_watch]

    for stream in change_streams:
        while True:
            change = stream.next()
            handle_change(change)

# Start the change stream listener in a separate thread
def start_change_stream():
    thread = threading.Thread(target=watch_changes, daemon=True)
    thread.start()

# Start listening for MongoDB changes when the app loads
start_change_stream()

# Display the data
display_data()

