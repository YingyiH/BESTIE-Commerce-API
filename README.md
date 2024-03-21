# BESTIE-Commerce-API
This is an API for an e-commerce store


# Be aware:
If there is "NoBroker" problem in Kafka, I need to:
    1. Stop Zookeeper and Kafka container
    2. Remove Zookeeper and Kafka container
    3. "docker compose down"
    4. "docker compose up -d"
    5. Restart Receiver container "docker restaet [Receiver_container_ID]"