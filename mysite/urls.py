"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    path('', views.index),
    path('date-selection', views.date_selection),
    path('get-vlf-data', views.get_vlf_data),
    path('send-term', views.send_term),
    path('stats', views.show_stats),
    path('contacts', views.contacts),
    path('lessons', views.lessons),
    path('cards', views.cards),
    path('test', views.test),
    path('send-answers', views.send_answers),
    path('submit-login', views.submit_login),
    path('sign_in', views.sign_in),
    path('submit-register', views.submit_register),
    path('menu', views.get_menu),
    path('vlf-data', views.get_vlf_data),
]
