#consumer.py

from kafka import KafkaConsumer
import json

# Create a Kafka consumer
consumer = KafkaConsumer('user-activity',
                        bootstrap_servers='localhost:9092',
                        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                        auto_offset_reset='earliest', # Start from the beginning
                        group_id='activity-looger') # Consumer group for message consumption

# Consume messages
print("Kafka Consumer started..")
for message in consumer:
    print("Received from Kafka..",message.value)
