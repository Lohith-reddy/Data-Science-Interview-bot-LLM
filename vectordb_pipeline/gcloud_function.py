from google.cloud import pubsub_v1
import json


def trigger_dag(event, context):
    """Publish a message to a Pub/Sub topic when a file in the 'pdfs' bucket changes."""

    # The ID of your Pub/Sub topic
    topic_id = 'data_updated_topic'

    # Create a Pub/Sub client
    publisher = pubsub_v1.PublisherClient()

    # The `topic_path` method creates a fully qualified identifier
    # in the form `projects/{project_id}/topics/{topic_id}`
    topic_path = publisher.topic_path('griller-490718', topic_id)

        # Create a dictionary with the event data
    data = {
        'name': event['name'],
        'eventType': context.event_type
    }

    # Convert the dictionary to a JSON string and encode it as a byte string
    payload = json.dumps(data).encode('utf-8')

    # Publish a message to the topic
    publisher.publish(topic_path, payload)