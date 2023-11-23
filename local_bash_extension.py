import os

from dotenv import load_dotenv
from jess_extension import jess_extension
from google.cloud import pubsub_v1
from concurrent.futures import TimeoutError

load_dotenv()

GCP_PROJECT_FOR_PUBSUB = os.getenv('GCP_PROJECT_FOR_PUBSUB')
GCP_PUBSUB_SUBSCRIPTION_FROM_HOST = os.getenv('GCP_PUBSUB_SUBSCRIPTION_FROM_HOST')
GCP_PUBSUB_TOPIC_TO_HOST = os.getenv('GCP_PUBSUB_TOPIC_TO_HOST')


def publish_command(project_id, topic_id, command):
    """Publishes a command to the specified Pub/Sub topic"""
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)
    future = publisher.publish(topic_path, command.encode("utf-8"))
    print(f"Published command to {topic_path}: {command}")
    return future.result()

def subscribe_to_result(project_id, subscription_id, timeout=None):
    """Subscribes to the specified Pub/Sub subscription for results"""
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    def callback(message):
        print(f"Received result: {message.data.decode('utf-8')}")
        callback.txt = message.data.decode('utf-8')
        message.ack()
        # Close the subscriber client to stop its background thread
        # try:
        #     subscriber.close()
        # except Exception as e:
        #     print(f"An error occurred: {e}")

    subscription_future = subscriber.subscribe(subscription_path, callback=callback)
    print(f"Listening for results on {subscription_path}...")

    try:
        # Wait for the subscriber to complete, or for a timeout
        subscription_future.result(timeout=timeout)
    except TimeoutError:
        # Handle the timeout case as needed
        print("No response received within the timeout period.")
        subscription_future.cancel()
    return callback.txt

@jess_extension(
    description="Send bash command on execution on a user's host",
    param_descriptions={
        "command": "Bash command to execute on the user's host"
    }
)
def send_bash_command_to_local_host(command: str):
    # Publish the command
    publish_command(GCP_PROJECT_FOR_PUBSUB, GCP_PUBSUB_TOPIC_TO_HOST, command)

    # Subscribe to the result and wait for the response
    subscribe_to_result(GCP_PROJECT_FOR_PUBSUB, GCP_PUBSUB_SUBSCRIPTION_FROM_HOST, timeout=20) 