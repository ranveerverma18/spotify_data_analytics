import time
import random
import uuid
from datetime import datetime
from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import StringSerializer
import spotipy
from spotipy.oauth2 import SpotifyOAuth

kafka_config = {
    'bootstrap.servers': 'pkc-l7pr2.ap-south-1.aws.confluent.cloud:9092', 
    'sasl.mechanisms': 'PLAIN',
    'security.protocol': 'SASL_SSL',
    'sasl.username': 'YBZYWVVR4ZHOM7LJ',
    'sasl.password': '8AZFKxD8XSgYhYpcg25Z4yQEIVUKVLPa0+SAkW9LjNwWVVK9RJZguxluzadIbFcr'
}


schema_registry_client = SchemaRegistryClient({
  'url': 'https://psrc-epk8y.australia-southeast1.gcp.confluent.cloud',
  'basic.auth.user.info': '{}:{}'.format('EFMB2DEU7PLZKQMG', 'dcvZBcYboTVYrBRlhSxM2uSLhFSSxzZhGO87WV5NHxyAZRzUByYm7yYtwWwyQwaS')
})

key_serializer = StringSerializer('utf_8')  #serialized the keys as UTF-8 strings

def get_latest_schema(subject):
    schema = schema_registry_client.get_latest_version(subject).schema.schema_str
    return AvroSerializer(schema_registry_client, schema)

# Producers
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

#fetching data and sending to kafka
def send_data_to_kafka(sp):
    user_profile = sp.current_user()
    top_tracks = sp.current_user_top_tracks(limit=10)
    top_artists = sp.current_user_top_artists(limit=10)
    liked_songs = sp.current_user_saved_tracks(limit=10)
    recently_played = sp.current_user_recently_played(limit=10)
    playlists = sp.current_user_playlists(limit=10)

    # Produce user profile data
    user_profile_producer.produce(
        topic='spotify_user_profile',
        key=user_profile['id'],
        value=user_profile,
        on_delivery=delivery_report
    )

    # Produce top tracks data
    top_tracks_producer.produce(
        topic='spotify_top_tracks',
        key=str(uuid.uuid4()),  # Generate unique key for each top track
        value=top_tracks,
        on_delivery=delivery_report
    )

    # Produce top artists data
    top_artists_producer.produce(
        topic='spotify_top_artists',
        key=str(uuid.uuid4()),  # Generate unique key for each artist list
        value=top_artists,
        on_delivery=delivery_report
    )

    # Produce liked songs data
    liked_songs_producer.produce(
        topic='spotify_liked_songs',
        key=str(uuid.uuid4()),  # Generate unique key for each liked song list
        value=liked_songs,
        on_delivery=delivery_report
    )

    # Produce recently played tracks data
    recently_played_producer.produce(
        topic='spotify_recently_played',
        key=str(uuid.uuid4()),  # Generate unique key for each recently played list
        value=recently_played,
        on_delivery=delivery_report
    )

    # Produce playlists data
    playlists_producer.produce(
        topic='spotify_user_playlists',
        key=str(uuid.uuid4()),  # Generate unique key for each playlist list
        value=playlists,
        on_delivery=delivery_report
    )

    #flushing the producers to ensure the messages are being sent
    user_profile_producer.flush()
    top_tracks_producer.flush()
    top_artists_producer.flush()
    liked_songs_producer.flush()
    recently_played_producer.flush()
    playlists_producer.flush()

# Delivery report callback function
def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed for {msg.key()}: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

# Main function to continuously fetch and send data
def main():
    sp = authenticate_spotify()

    while True:
        send_data_to_kafka(sp)
        time.sleep(10)  # Delay for 60 seconds before fetching new data

if __name__ == "__main__":
    main()


