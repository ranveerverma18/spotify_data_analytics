from pymongo import MongoClient
from bson.json_util import dumps

# Connect to the MongoDB Atlas cluster
client = MongoClient("mongodb+srv://ranveerverma18:ranveer18@mongo-db-cluster.7xghnej.mongodb.net/spotify_data?retryWrites=true&w=majority")

# Access the database and collections
db = client.spotify_data

# List of collections to monitor for changes 
collections_to_watch = ['spotify_liked_songs', 'spotify_recently_played', 'spotify_user_playlists','spotify_top_tracks']

# Create change streams for each collection
change_streams = [db[collection].watch(full_document='updateLookup') for collection in collections_to_watch]

# Function to handle changes and print them
def handle_change(change):
    print(f"Change detected: {dumps(change)}")

# Listen for changes in all specified collections
try:
    while True:
        for stream in change_streams:
            # Get the next change from the stream
            change = stream.next()
            # Call the handle_change function for each change detected
            handle_change(change)
except KeyboardInterrupt:
    print("Stopped listening for changes.")



