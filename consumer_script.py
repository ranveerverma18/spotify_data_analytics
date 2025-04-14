# This script consumes messages from multiple Kafka topics and stores them in MongoDB.
# It uses the Confluent Kafka library for Kafka interactions and PyMongo for MongoDB operations.

import threading
from confluent_kafka import DeserializingConsumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import StringDeserializer
from pymongo import MongoClient

# Kafka Configuration
kafka_config = {
    'bootstrap.servers': 'pkc-l7pr2.ap-south-1.aws.confluent.cloud:9092',
    'sasl.mechanisms': 'PLAIN',
    'security.protocol': 'SASL_SSL',
    'sasl.username': 'YBZYWVVR4ZHOM7LJ',
    'sasl.password': '8AZFKxD8XSgYhYpcg25Z4yQEIVUKVLPa0+SAkW9LjNwWVVK9RJZguxluzadIbFcr',
    'group.id': 'spotify-consumer-group',
    'auto.offset.reset': 'earliest'
}

# Schema Registry Configuration
schema_registry_client = SchemaRegistryClient({
    'url': 'https://psrc-epk8y.australia-southeast1.gcp.confluent.cloud',
    'basic.auth.user.info': '{}:{}'.format('EFMB2DEU7PLZKQMG', 'dcvZBcYboTVYrBRlhSxM2uSLhFSSxzZhGO87WV5NHxyAZRzUByYm7yYtwWwyQwaS')
})

# MongoDB Setup
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["spotify_data"]

# Define topics and their schema subjects
topics = {
    'spotify_user_profile': 'spotify_user_profile-value',
    'spotify_top_tracks': 'spotify_top_tracks-value',
    'spotify_top_artists': 'spotify_top_artists-value',
    'spotify_liked_songs': 'spotify_liked_songs-value',
    'spotify_recently_played': 'spotify_recently_played-value',
    'spotify_user_playlists': 'spotify_user_playlists-value'
}

def consume_topic(topic, subject):
    key_deserializer = StringDeserializer('utf_8')
    value_schema_str = schema_registry_client.get_latest_version(subject).schema.schema_str
    value_deserializer = AvroDeserializer(schema_registry_client, value_schema_str)

    consumer = DeserializingConsumer({
        'bootstrap.servers': kafka_config['bootstrap.servers'],
        'security.protocol': kafka_config['security.protocol'],
        'sasl.mechanisms': kafka_config['sasl.mechanisms'],
        'sasl.username': kafka_config['sasl.username'],
        'sasl.password': kafka_config['sasl.password'],
        'key.deserializer': key_deserializer,
        'value.deserializer': value_deserializer,
        'group.id': kafka_config['group.id'],
        'auto.offset.reset': kafka_config['auto.offset.reset']
    })

    consumer.subscribe([topic])
    collection = db[topic]

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"Consumer error on topic {topic}: {msg.error()}")
                continue

            print(f"Consumed from {topic}: key={msg.key()}, value={msg.value()}")
            collection.insert_one(msg.value())
    except KeyboardInterrupt:
        print(f"Stopped consuming from {topic}")
    finally:
        consumer.close()

if __name__ == "__main__":
    threads = []
    for topic, subject in topics.items():
        t = threading.Thread(target=consume_topic, args=(topic, subject))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()