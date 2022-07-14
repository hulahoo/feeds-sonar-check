import json

from dagster import op, job, get_dagster_logger, Field, DynamicOut, DynamicOutput

from worker.utils import django_init


from kafka import KafkaConsumer, TopicPartition



@op(config_schema={'partitions': Field(list)}, out=DynamicOut())
def consumer_dispatcher_op(context):
    partitions = context.op_config['partitions']

    for partition in partitions:
        yield DynamicOutput(
            value=partition,
            mapping_key=f'partition_{partition}'
        )


@op
def consumer_collector(data):
    return len(data)

def event_worker(data:dict):
    print('|||||||||||||||||||||||||||||||||||||||||')
    print()
    print()
    print(data)
    print()
    print()
    print('|||||||||||||||||||||||||||||||||||||||||')
    pass


@op
def op_consumer(context, partition: int):
    from worker.utils import django_init
    django_init()
    from django.conf import settings
    logger = get_dagster_logger()
    group_id = settings.KAFKA_GROUP_ID
    kafka_ip = settings.KAFKA_IP
    topic = settings.KAFKA_TOPIC

    kafka_consumer = KafkaConsumer(
        bootstrap_servers={f'{kafka_ip}:9092'},
        auto_offset_reset='earliest',
        group_id=group_id,
        # enable_auto_commit=False,
        # max_poll_records=500,
        # max_poll_interval_ms=12 * 60_000,
        # session_timeout_ms=1000 * 60 * 5,
        # heartbeat_interval_ms=1000 * 60 * 5,
    )
    topic_partition = TopicPartition(topic, partition)
    topics = [topic_partition]
    kafka_consumer.assign(topics)
    while True:
        for tp, messages in tuple(kafka_consumer.poll(timeout_ms=5000).items()):
            for message in messages:
                data = json.loads(message.value)
                logger.info(f'{data}')
                event_worker(data)


@job
def job_consumer():
    results = consumer_dispatcher_op().map(op_consumer)
    consumer_collector(results.collect())
