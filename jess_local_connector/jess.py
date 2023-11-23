import subprocess
import argparse

from google.cloud import pubsub_v1

# Set up the argument parser
parser = argparse.ArgumentParser(description="Google Pub/Sub Subscriber")
parser.add_argument('project_id', help="Google Cloud project ID")
parser.add_argument('subscription_id', help="Pub/Sub subscription ID")
parser.add_argument('publisher_topic_id', help="Pub/Sub publisher topic ID")

# Parse arguments
args = parser.parse_args()

project_id = args.project_id
subscription_id = args.subscription_id
publisher_topic_id = args.publisher_topic_id

subscriber = pubsub_v1.SubscriberClient()
publisher = pubsub_v1.PublisherClient()

subscription_path = subscriber.subscription_path(project_id, subscription_id)
publisher_topic_path = publisher.topic_path(project_id, publisher_topic_id)

def execute_command_and_publish_result(command):
    try:
        # Execute the command
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Command failed: {e.stderr}"

def callback(message):
    print(f"Received message: {message.data.decode('utf-8')}")
    command_output = execute_command_and_publish_result(message.data.decode('utf-8'))
    if command_output == "":
        command_output = "Command executed successfully but result is empty"

    print(f"Publishing result: {command_output} to {publisher_topic_path}")
    # Publish the result to the other topic
    publisher.publish(publisher_topic_path, command_output.encode('utf-8'))
    print("Result published")
    # Acknowledge the message
    message.ack()

streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print(f"Listening for messages on {subscription_path}...")

# Keep the main thread alive, or the process will exit.
try:
    streaming_pull_future.result()
except KeyboardInterrupt:
    streaming_pull_future.cancel()