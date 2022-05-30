from django.shortcuts import render
from django.http import HttpResponse
from .forms import FeedForm

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
