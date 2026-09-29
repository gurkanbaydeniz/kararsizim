from django.shortcuts import render


def index(request):
    """Anasayfa — Faz 2'de anket akışına (poll_list) dönüşecek."""
    return render(request, "polls/poll_list.html")
