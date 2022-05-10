from django.shortcuts import render
from .models import *
from django.views.generic import ListView, DetailView


class Home(ListView):
    model = GroupList
    template_name = 'likes_parser/home.html'
    context_object_name = 'parser'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['main'] = 'Hello from parser'
        return context
