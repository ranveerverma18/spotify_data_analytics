import time
import uuid
from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import StringSerializer
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Kafka Configuration
kafka_config = {
    'bootstrap.servers': 'pkc-l7pr2.ap-south-1.aws.confluent.cloud:9092', 
    'sasl.mechanisms': 'PLAIN',
    'security.protocol': 'SASL_SSL',
    'sasl.username': 'YBZYWVVR4ZHOM7LJ',
    'sasl.password': '8AZFKxD8XSgYhYpcg25Z4yQEIVUKVLPa0+SAkW9LjNwWVVK9RJZguxluzadIbFcr'
}

# Schema Registry Configuration
schema_registry_client = SchemaRegistryClient({
  'url': 'https://psrc-epk8y.australia-southeast1.gcp.confluent.cloud',
  'basic.auth.user.info': '{}:{}'.format('EFMB2DEU7PLZKQMG', 'dcvZBcYboTVYrBRlhSxM2uSLhFSSxzZhGO87WV5NHxyAZRzUByYm7yYtwWwyQwaS')
})

key_serializer = StringSerializer('utf_8')

def get_latest_schema(subject):
    schema = schema_registry_client.get_latest_version(subject).schema.schema_str
    return AvroSerializer(schema_registry_client, schema)

# Kafka Producers for each topic
user_profile_producer = SerializingProducer({**kafka_config,
                                             'key.serializer': key_serializer,
                                             'value.serializer': get_latest_schema('spotify_user_profile-value')})

top_tracks_producer = SerializingProducer({**kafka_config,
                                           'key.serializer': key_serializer,
                                           'value.serializer': get_latest_schema('spotify_top_tracks-value')})

top_artists_producer = SerializingProducer({**kafka_config,
                                            'key.serializer': key_serializer,
                                            'value.serializer': get_latest_schema('spotify_top_artists-value')})

liked_songs_producer = SerializingProducer({**kafka_config,
                                            'key.serializer': key_serializer,
                                            'value.serializer': get_latest_schema('spotify_liked_songs-value')})

recently_played_producer = SerializingProducer({**kafka_config,
                                                'key.serializer': key_serializer,
                                                'value.serializer': get_latest_schema('spotify_recently_played-value')})

playlists_producer = SerializingProducer({**kafka_config,
                                           'key.serializer': key_serializer,
                                           'value.serializer': get_latest_schema('spotify_user_playlists-value')})

# Spotify Authentication
def authenticate_spotify():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id='e406584407bc4d6abfbc0ed5052983e0',
        client_secret='3052c144d4d1423e9b9bcdf02d587cc5',
        redirect_uri='http://localhost:8888/callback',
        scope="user-read-private user-read-email user-top-read user-library-read user-read-recently-played playlist-read-private playlist-read-collaborative"
    ))
    return sp

# Kafka Delivery Report
def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed for {msg.key()}: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

# Send data to Kafka topics
def send_data_to_kafka(sp):
    user_profile_raw = sp.current_user()
    user_id = user_profile_raw["id"]

    user_profile = {
        "user_id": user_id,
        "display_name": user_profile_raw.get("display_name", ""),
        "email": user_profile_raw.get("email", ""),
        "country": user_profile_raw.get("country", ""),
        "followers_count": user_profile_raw.get("followers", {}).get("total", 0),
        "product_type": user_profile_raw.get("product", ""),
        "external_urls": {
            "spotify": user_profile_raw.get("external_urls", {}).get("spotify", "")
        },
        "images": [
            {
                "url": img.get("url", ""),
                "height": img.get("height", 0),
                "width": img.get("width", 0)
            } for img in user_profile_raw.get("images", [])
        ]
    }

    user_profile_producer.produce(
        topic='spotify_user_profile',
        key=user_profile["user_id"],
        value=user_profile,
        on_delivery=delivery_report
    )

    top_tracks_raw = sp.current_user_top_tracks(limit=10)
    for item in top_tracks_raw["items"]:
        top_track = {
            "user_id": user_id,
            "track_name": item["name"],
            "artist_name": item["artists"][0]["name"] if item["artists"] else "Unknown",
            "album_name": item["album"]["name"],
            "track_url": item["external_urls"]["spotify"],
            "track_id": item["id"],
            "popularity": item["popularity"]
        }
        top_tracks_producer.produce(
            topic='spotify_top_tracks',
            key=str(uuid.uuid4()),
            value=top_track,
            on_delivery=delivery_report
        )

    top_artists_raw = sp.current_user_top_artists(limit=10)
    for item in top_artists_raw["items"]:
        top_artist = {
            "user_id": user_id,
            "artist_name": item["name"],
            "artist_id": item["id"],
            "popularity": item.get("popularity", 0),
            "artist_url": item.get("external_urls", {}).get("spotify", "")
        }
        top_artists_producer.produce(
            topic='spotify_top_artists',
            key=str(uuid.uuid4()),
            value=top_artist,
            on_delivery=delivery_report
        )

    liked_songs_raw = sp.current_user_saved_tracks(limit=10)
    for item in liked_songs_raw["items"]:
        track = item["track"]
        liked_song = {
            "user_id": user_id,
            "track_name": track["name"],
            "artist_name": track["artists"][0]["name"] if track["artists"] else "Unknown",
            "album_name": track["album"]["name"],
            "track_url": track["external_urls"]["spotify"],
            "track_id": track["id"],
            "added_at": item.get("added_at", "")  
        }
        liked_songs_producer.produce(
            topic='spotify_liked_songs',
            key=str(uuid.uuid4()),
            value=liked_song,
            on_delivery=delivery_report
        )


    recently_played_raw = sp.current_user_recently_played(limit=10)
    for item in recently_played_raw["items"]:
        track = item["track"]
        recently_played = {
            "user_id": user_id,
            "track_name": track["name"],
            "artist_name": track["artists"][0]["name"] if track.get("artists") else "Unknown",
            "album_name": track["album"]["name"] if track.get("album") else "Unknown",
            "track_url": track["external_urls"]["spotify"] if track.get("external_urls") else "Unknown",  
            "played_at": item["played_at"],
            "track_id": track["id"]
        }

        recently_played_producer.produce(
            topic='spotify_recently_played',
            key=str(uuid.uuid4()),
            value=recently_played,
            on_delivery=delivery_report
        )


    user_playlists_raw = sp.current_user_playlists(limit=10)
    for playlist in user_playlists_raw["items"]:
        playlist_data = {
            "user_id": user_id,
            "playlist_name": playlist.get("name", ""),
            "playlist_id": playlist.get("id", ""),
            "playlist_url": playlist.get("external_urls", {}).get("spotify", ""),
            "description": playlist.get("description", "") or "No description",
            "track_count": playlist.get("tracks", {}).get("total", 0),
            "is_public": playlist.get("public", False),
            "images": [
                {
                    "url": img.get("url", ""),
                    "height": int(img.get("height") or 0),
                    "width": int(img.get("width") or 0)
                } for img in (playlist.get("images") or [])
            ]
        }

        playlists_producer.produce(
            topic='spotify_user_playlists',
            key=playlist_data["playlist_id"],
            value=playlist_data,
            on_delivery=delivery_report
        )

    # Flush all producers
    user_profile_producer.flush()
    top_tracks_producer.flush()
    top_artists_producer.flush()
    liked_songs_producer.flush()
    recently_played_producer.flush()
    playlists_producer.flush()

# Main runner
def main():
    sp = authenticate_spotify()
    while True:
        send_data_to_kafka(sp)
        time.sleep(10)

if __name__ == "__main__":
    main()
