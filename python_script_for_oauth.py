from spotipy.oauth2 import SpotifyOAuth
import spotipy
import pymongo

# MongoDB setup
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["spotify_user_data"]

# Spotify Auth Function
def authenticate_spotify():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id='e406584407bc4d6abfbc0ed5052983e0',
        client_secret='3052c144d4d1423e9b9bcdf02d587cc5',
        redirect_uri='http://localhost:8888/callback',
        scope="user-read-private user-read-email user-top-read user-library-read user-read-recently-played playlist-read-private playlist-read-collaborative"
    ))
    print("✅ Spotify OAuth authentication successful!")
    return sp

# Functions to fetch and save data
def save_user_profile(sp):
    try:
        user_data = sp.current_user()
        db.profile.insert_one(user_data)
        print("✅ User profile saved!")
    except Exception as e:
        print("❌ Error saving user profile:", e)

def save_top_tracks(sp):
    try:
        top_tracks = sp.current_user_top_tracks(limit=10)
        db.top_tracks.insert_one(top_tracks)
        print("🎶 Top tracks saved!")
    except Exception as e:
        print("❌ Error saving top tracks:", e)

def save_top_artists(sp):
    try:
        top_artists = sp.current_user_top_artists(limit=10)
        db.top_artists.insert_one(top_artists)
        print("🧑‍🎤 Top artists saved!")
    except Exception as e:
        print("❌ Error saving top artists:", e)

def save_liked_songs(sp):
    try:
        liked_songs = sp.current_user_saved_tracks(limit=10)
        db.liked_songs.insert_one(liked_songs)
        print("❤️ Liked songs saved!")
    except Exception as e:
        print("❌ Error saving liked songs:", e)

def save_recently_played(sp):
    try:
        recently_played = sp.current_user_recently_played(limit=10)
        db.recently_played.insert_one(recently_played)
        print("🕒 Recently played tracks saved!")
    except Exception as e:
        print("❌ Error saving recently played:", e)

def save_playlists(sp):
    try:
        playlists = sp.current_user_playlists(limit=10)
        db.playlists.insert_one(playlists)
        print("📂 Playlists saved!")
    except Exception as e:
        print("❌ Error saving playlists:", e)

# Main Function
def main():
    sp = authenticate_spotify()
    save_user_profile(sp)
    save_top_tracks(sp)
    save_top_artists(sp)
    save_liked_songs(sp)
    save_recently_played(sp)
    save_playlists(sp)

if __name__ == "__main__":
    main()
