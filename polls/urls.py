from django.urls import path

from . import views

app_name = "polls"

urlpatterns = [
    path("", views.poll_list, name="index"),
    path("kayit/", views.register, name="register"),
    path("giris/", views.GirisView.as_view(), name="login"),
    path("cikis/", views.CikisView.as_view(), name="logout"),
    # Sıra önemli: sabit yollar, <int:pk>'den ÖNCE tanımlanmalı
    path("anket/olustur/", views.poll_create, name="poll_create"),
    path("anketlerim/", views.my_polls, name="my_polls"),
    path("anket/<int:pk>/oy/", views.vote, name="vote"),
    path("anket/<int:pk>/sil/", views.poll_delete, name="poll_delete"),
    path("anket/<int:pk>/", views.poll_detail, name="poll_detail"),
]
