from confluent_kafka.admin import AdminClient, ConfigResource, ConfigSource
from confluent_kafka.cimpl import KafkaException

c=AdminClient({"bootstrap.servers":"localhost:9092"})

def print_config(config, depth):
    print('%40s = %-50s  [%s,is:read-only=%r,default=%r,sensitive=%r,synonym=%r,synonyms=%s]' %
          ((' ' * depth) + config.name, config.value, ConfigSource(config.source),
           config.is_read_only, config.is_default,
           config.is_sensitive, config.is_synonym,
           ["%s:%s" % (x.name, ConfigSource(x.source))
            for x in iter(config.synonyms.values())]))

def describe_configs(a, topicName):
    """ describe configs """
    resources = [ConfigResource('topic', topicName)]

    fs = a.describe_configs(resources)

    # Wait for operation to finish.
    for res, f in fs.items():
        try:
            configs = f.result()
            for config in iter(configs.values()):
                print_config(config, 1)

        except KafkaException as e:
            print("Failed to describe {}: {}".format(res, e))
        except Exception:
            raise

response = c.list_topics()
for topic in response.topics:
    topicMeta = response.topics[topic]
    print("topic : %s [%s partitions]" % (topic, len(topicMeta.partitions)))

    describe_configs(c, topic)