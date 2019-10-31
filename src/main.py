from confluent_kafka.admin import AdminClient

c=AdminClient({"bootstrap.servers":"localhost:9092"})

response = c.list_topics()
for topic in response.topics:
    topicMeta = response.topics[topic]
    print(topic, len(topicMeta.partitions))