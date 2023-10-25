from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse

# Create your views here.
def home(request):
    return render(request, 'pages/business.html',)

# Create your views here.
def personal(request):
    return render(request, 'pages/personal.html',)
    

@login_required
def redirect(request):
    # Assuming your user model has an 'id' field that represents the user's ID
    user_id = request.user.id
    return HttpResponseRedirect(reverse("accounts:user", kwargs={"id": user_id}))
