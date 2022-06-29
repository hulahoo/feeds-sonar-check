from django.shortcuts import render
from django.http import HttpResponse
from .forms import FeedForm
from confluent_kafka import Consumer, Producer
from confluent_kafka.admin import AdminClient, NewTopic

# Create your views here.
def feed_add(request):
    if request.method == "POST":
        form = FeedForm(request.POST)
        if form.is_valid():
            feed = form.save()
            return HttpResponse("Succesfully added!")
    else:
        form = FeedForm()
    return render(request, "form_add.html", {"form": form})


# def delivery_report(err, msg):
#     """Called once for each message produced to indicate delivery result.
#     Triggered by poll() or flush()."""
#     if err is not None:
#         print("Message delivery failed: {}".format(err))
#     else:
#         print("Message delivered to {} [{}]".format(msg.topic(), msg.partition()))


# data = '{"kek": "wait"}'


# def add_to_query(request):
#     p = Producer({"bootstrap.servers": "broker"})
#     p.produce("threatintel", data.encode("utf-8"), callback=delivery_report)
#     p.flush()
#     return HttpResponse(200)


# def read_from_query(request):

#     c = Consumer(
#         {
#             "bootstrap.servers": "broker:9092",
#             "group.id": "mygroup",
#             "auto.offset.reset": "earliest",
#         }
#     )

#     c.subscribe(["threatintel"])

#     while True:
#         msg = c.poll(1.0)

#         if msg is None:
#             continue
#         if msg.error():
#             print("Consumer error: {}".format(msg.error()))
#             continue
#         print("Received message: {}".format(msg.value().decode("utf-8")))
#         c.close()
#         return HttpResponse(200)
