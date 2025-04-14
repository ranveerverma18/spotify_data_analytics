import streamlit as st
import pandas as pd
import plotly.express as px
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")

# MongoDB connection
client = MongoClient(mongo_uri)
db = client['spotify_data']
print("✅ Connected to MongoDB Atlas")

# Streamlit UI Setup
st.set_page_config(page_title="Spotify Real-Time Dashboard", layout="wide")
st.title("🎧 Spotify Real-Time Dashboard")
st.sidebar.header("🎚️ Filters")

# Collection Selector
collections = ['spotify_liked_songs', 'spotify_user_playlists', 'spotify_top_tracks',
               'spotify_top_artists', 'spotify_recently_played']
selected_collection = st.sidebar.selectbox("📂 Select Collection", collections)

# Manual Refresh Button
if st.sidebar.button("🔄 Refresh Now"):
    st.rerun()

# Fetch data with caching
@st.cache_data(ttl=30)
def fetch_data(collection_name):
    data = list(db[collection_name].find())
    return pd.DataFrame(data)

# Main Display Logic
def display_data():
    df = fetch_data(selected_collection)
    st.subheader(f"📊 Data from `{selected_collection}`")

    if df.empty:
        st.warning("No data available yet.")
        return

    # Drop ID and Convert date
    if '_id' in df.columns:
        df.drop(columns=['_id'], inplace=True)
    if 'played_at' in df.columns:
        df['played_at'] = pd.to_datetime(df['played_at'], errors='coerce')

    # User filter if applicable
    if 'user_id' in df.columns:
        user_ids = df['user_id'].dropna().unique().tolist()
        selected_user = st.sidebar.selectbox("👤 Filter by User", user_ids)
        df = df[df['user_id'] == selected_user]

    # Optional date filter for recently played
    if selected_collection == 'spotify_recently_played' and 'played_at' in df.columns:
        min_date = df['played_at'].min()
        max_date = df['played_at'].max()
        date_range = st.sidebar.date_input("📅 Date Range", [min_date, max_date])
        if len(date_range) == 2:
            start, end = date_range
            df = df[(df['played_at'].dt.date >= start) & (df['played_at'].dt.date <= end)]

    # Dataframe preview
    st.dataframe(df.head(20), use_container_width=True)

    # Show Metrics
    st.markdown("### 📌 Quick Stats")
    col1, col2, col3 = st.columns(3)
    col1.metric("📁 Records", len(df))
    if 'duration_ms' in df.columns:
        avg_duration = round(df['duration_ms'].mean() / 60000, 2)
        col2.metric("⏱ Avg Duration (min)", avg_duration)
    if 'popularity' in df.columns:
        avg_popularity = round(df['popularity'].mean(), 2)
        col3.metric("🔥 Avg Popularity", avg_popularity)

    # Visualizations
    st.markdown("### 📊 Insights")

    if selected_collection == 'spotify_top_tracks' and {'track_name', 'popularity'}.issubset(df.columns):
        fig1 = px.bar(df.sort_values(by='popularity', ascending=False).head(10),
                      x='track_name', y='popularity', color='popularity',
                      title="🔥 Top Tracks by Popularity")
        st.plotly_chart(fig1, use_container_width=True)

    elif selected_collection == 'spotify_top_artists' and 'artist_name' in df.columns:
        fig2 = px.pie(df, names='artist_name', title="🎤 Your Favorite Artists", hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)

    elif selected_collection == 'spotify_liked_songs' and 'duration_ms' in df.columns:
        fig3 = px.histogram(df, x='duration_ms', nbins=50, title="🎶 Liked Songs Duration")
        st.plotly_chart(fig3, use_container_width=True)

    elif selected_collection == 'spotify_user_playlists' and 'track_count' in df.columns:
        fig4 = px.bar(df, x='playlist_name', y='track_count', title="📁 Tracks per Playlist")
        st.plotly_chart(fig4, use_container_width=True)

    elif selected_collection == 'spotify_recently_played' and 'played_at' in df.columns:
        col_a, col_b = st.columns(2)

        with col_a:
            df['hour'] = df['played_at'].dt.hour
            fig5 = px.histogram(df, x='hour', nbins=24, title="⏱️ Listening by Hour")
            st.plotly_chart(fig5, use_container_width=True)

        with col_b:
            df['day'] = df['played_at'].dt.date
            fig6 = px.histogram(df, x='day', title="📆 Listening Trend Over Days")
            st.plotly_chart(fig6, use_container_width=True)

# Execute
display_data()




