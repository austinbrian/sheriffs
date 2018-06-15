#!/usr/bin/.env python
# howdy/urls.py
from django.conf.urls import url
from . import views

urlpatterns = [
        url('^$', views.HomePageView.as_view()),
        url('^about/$', views.AboutPageView.as_view()),
        ]

