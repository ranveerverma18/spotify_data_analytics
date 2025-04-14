from flask import Flask, render_template, request
from pymongo import MongoClient
from bson.json_util import dumps

app = Flask(__name__)

# MongoDB Atlas connection
mongo_client = MongoClient("mongodb+srv://ranveerverma18:ranveer18@mongo-db-cluster.7xghnej.mongodb.net/spotify_data?retryWrites=true&w=majority")
db = mongo_client["spotify_data"]

@app.route("/dashboard/<user_id>")
def dashboard(user_id):
    # Fetch data for the user from MongoDB collections
    profile = db.spotify_user_profile.find_one({"id": user_id})
    liked_songs = list(db.spotify_liked_songs.find({"user_id": user_id}))
    top_tracks = list(db.spotify_top_tracks.find({"user_id": user_id}))
    top_artists = list(db.spotify_top_artists.find({"user_id": user_id}))
    playlists = list(db.spotify_user_playlists.find({"user_id": user_id}))
    recent = list(db.spotify_recently_played.find({"user_id": user_id}).sort("played_at", -1).limit(5))

    # Derived stats
    total_liked = len(liked_songs)
    playlist_count = len(playlists)
    
    # Safe access to 'name' field
    top_artist_names = [artist.get('name', 'Unknown Artist') for artist in top_artists[:10]]
    top_track_names = [track.get('name', 'Unknown Track') for track in top_tracks[:10]]

    return render_template("dashboard.html",
                           user=profile,
                           total_liked=total_liked,
                           playlist_count=playlist_count,
                           top_artists=top_artist_names,
                           top_tracks=top_track_names,
                           recent=recent)

if __name__ == "__main__":
    app.run(debug=True)
