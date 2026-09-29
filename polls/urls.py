from django.urls import path

from . import views

app_name = "polls"

urlpatterns = [
    path("", views.index, name="index"),
    path("kayit/", views.register, name="register"),
    path("giris/", views.GirisView.as_view(), name="login"),
    path("cikis/", views.CikisView.as_view(), name="logout"),
    # Not: /anket/olustur/, Faz 2'de /anket/<int:pk>/ adresinden ÖNCE tanımlı kalmalı
    path("anket/olustur/", views.poll_create, name="poll_create"),
]
