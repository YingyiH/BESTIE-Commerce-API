# BESTIE-Commerce-API
This is an API for an e-commerce store


# Be aware:
If there is "NoBroker" problem in Kafka, I need to:
    1. Stop Zookeeper and Kafka container
    2. Remove Zookeeper and Kafka container
    3. "docker compose down"
    4. "docker compose up -d"
    5. Restart Receiver container "docker restaet [Receiver_container_ID]"
    6. Restart Audit container

If processing stats keep showing the same data on website, I need to:
    - Make sure I delete "sqlite" in processing folder
    - Make sure there is no ROLLBACK command in docker logs
    - Make sure restart storage container