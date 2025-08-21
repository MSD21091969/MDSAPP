# MDSAPP/core/managers/pubsub_manager.py

import logging
import os
import json
from typing import Dict, Any

from google.cloud import pubsub_v1
from google.api_core import exceptions

logger = logging.getLogger(__name__)

class PubSubManager:
    """
    Manages publishing messages to Google Cloud Pub/Sub.
    """
    def __init__(self):
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        if not self.project_id:
            logger.warning("GOOGLE_CLOUD_PROJECT environment variable not set. Pub/Sub will be disabled.")
            self.publisher = None
        else:
            try:
                self.publisher = pubsub_v1.PublisherClient()
                logger.info("PubSubManager initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize Pub/Sub publisher: {e}", exc_info=True)
                self.publisher = None

    async def publish_message(self, topic_id: str, message_data: Dict[str, Any]):
        """
        Publishes a message to a Pub/Sub topic.
        """
        if not self.publisher:
            logger.debug(f"Pub/Sub is disabled. Skipping message publication to topic '{topic_id}'.")
            return

        topic_path = self.publisher.topic_path(self.project_id, topic_id)
        message_json = json.dumps(message_data)
        message_bytes = message_json.encode("utf-8")

        try:
            future = self.publisher.publish(topic_path, message_bytes)
            # The future returned by publish() is awaitable
            message_id = await future
            logger.info(f"Published message {message_id} to topic {topic_id}.")
        except exceptions.NotFound:
            logger.warning(f"Pub/Sub topic not found: {topic_path}. Please create it.")
        except Exception as e:
            logger.error(f"Failed to publish message to topic {topic_id}: {e}", exc_info=True)
