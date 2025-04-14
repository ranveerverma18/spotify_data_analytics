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




