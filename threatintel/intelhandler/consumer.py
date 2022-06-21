from confluent_kafka import Consumer, Producer


c = Consumer(
    {
        "bootstrap.servers": "broker",
        "group.id": "mygroup",
        "auto.offset.reset": "earliest",
    }
)

c.subscribe(["threatintel"])

while True:
    msg = c.poll(1.0)

    if msg is None:
        continue
    if msg.error():
        print("Consumer error: {}".format(msg.error()))
        continue
    print("Received message: {}".format(msg.value().decode("utf-8")))

c.close()
