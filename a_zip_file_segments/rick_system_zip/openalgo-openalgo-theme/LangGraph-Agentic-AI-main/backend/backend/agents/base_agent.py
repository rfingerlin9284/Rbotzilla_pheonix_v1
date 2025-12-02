import json
import redis
import threading
import time

class BaseAgent:
    def __init__(self, name, subscribe_channels, publish_channel):
        self.name = name
        self.subscribe_channels = subscribe_channels
        self.publish_channel = publish_channel
        self.redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)
        self.pubsub = self.redis_client.pubsub()
        self.pubsub.subscribe(*subscribe_channels)
        self.running = False

    def process_message(self, message):
        # Override this in child classes
        raise NotImplementedError()

    def publish(self, message):
        self.redis_client.publish(self.publish_channel, json.dumps(message))

    def listen(self):
        print(f"Agent '{self.name}' listening on channels: {self.subscribe_channels}")
        for item in self.pubsub.listen():
            if item['type'] == 'message':
                try:
                    data = json.loads(item['data'])
                    print(f"[{self.name}] Received message on {item['channel']}: {data}")
                    output = self.process_message(data)
                    if output:
                        self.publish(output)
                        print(f"[{self.name}] Published message on {self.publish_channel}: {output}")
                except Exception as e:
                    print(f"[{self.name}] Error processing message: {e}")

    def run(self):
        self.running = True
        try:
            self.listen()
        except KeyboardInterrupt:
            print(f"Agent '{self.name}' shutting down.")
            self.running = False
