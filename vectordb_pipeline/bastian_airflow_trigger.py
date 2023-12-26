import requests
from google.cloud import pubsub_v1
import json


def receive_message(message):
    """Receive a message from a Pub/Sub subscription and trigger a DAG run."""

    # Decode the message data from bytes to a string
    data_str = message.data.decode('utf-8')

    # Parse the string as JSON to get a dictionary
    data = json.loads(data_str)

    # The URL of your Airflow instance
    airflow_url = 'http://your-airflow-url.com'

    # The ID of your DAG
    dag_id = 'update_qdrant_db'

    # Trigger the DAG run and pass the message data to the DAG
    response = requests.post(
        f'{airflow_url}/api/experimental/dags/{dag_id}/dag_runs',
        json={'conf': data},
        headers={'Cache-Control': 'no-cache'}
    )

    if response.status_code == 200:
        print(f'Successfully triggered DAG {dag_id}')
    else:
        print(f'Failed to trigger DAG {dag_id}')

    # Acknowledge the message
    message.ack()


def listen_for_messages():
    """Subscribe to a Pub/Sub topic and listen for messages."""

    # The ID of your Pub/Sub subscription
    subscription_id = 'your_subscription_id'

    # Create a Pub/Sub client
    subscriber = pubsub_v1.SubscriberClient()

    # The `subscription_path` method creates a fully qualified identifier
    # in the form `projects/{project_id}/subscriptions/{subscription_id}`
    subscription_path = subscriber.subscription_path('your_project_id', subscription_id)

    # Subscribe to the topic and listen for messages
    subscriber.subscribe(subscription_path, callback=callback)

    # Keep the script running
    while True:
        pass


if __name__ == '__main__':
    listen_for_messages()
