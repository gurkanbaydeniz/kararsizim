from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from .forms import EmailOrUsernameAuthenticationForm, PollForm, RegisterForm
from .models import Poll

SAYFA_BASI_ANKET = 12  # feed sayfa boyutu (doct/PROJE.md Bölüm 5)


def poll_list(request):
    """Anasayfa / feed: en yeni anketler, sayfa başına 12."""
    polls = (
        Poll.objects.select_related("creator")
        .annotate(total_votes=Count("votes", distinct=True))
        .order_by("-created_at")
    )
    page_obj = Paginator(polls, SAYFA_BASI_ANKET).get_page(request.GET.get("page"))
    return render(request, "polls/poll_list.html", {"page_obj": page_obj})


@login_required
def poll_create(request):
    """Anket oluşturma (yalnızca üyeler). Başarıda detay sayfasına yönlenir."""
    form = PollForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            poll = Poll.objects.create(
                creator=request.user, question=form.cleaned_data["question"]
            )
            for position, text in enumerate(form.cleaned_data["choices"]):
                poll.choices.create(text=text, position=position)
        messages.success(request, "Anketin yayında! Şimdi oyları topla 🎉")
        return redirect("polls:poll_detail", pk=poll.pk)
    return render(request, "polls/poll_form.html", {"form": form})


def poll_detail(request, pk):
    """Anket detayı. Oy butonları Faz 3'te aktifleşecek; şimdilik pasif görünür."""
    poll = get_object_or_404(
        Poll.objects.select_related("creator").annotate(
            total_votes=Count("votes", distinct=True)
        ),
        pk=pk,
    )
    choices = poll.choices.annotate(vote_count=Count("votes"))
    return render(request, "polls/poll_detail.html", {"poll": poll, "choices": choices})


@login_required
def my_polls(request):
    """Sadece kullanıcının kendi anketleri."""
    polls = (
        Poll.objects.filter(creator=request.user)
        .annotate(total_votes=Count("votes", distinct=True))
        .order_by("-created_at")
    )
    page_obj = Paginator(polls, SAYFA_BASI_ANKET).get_page(request.GET.get("page"))
    return render(request, "polls/my_polls.html", {"page_obj": page_obj})


# ---------- Üyelik (Faz 1) ----------


def register(request):
    """Kayıt sayfası: başarılı kayıttan sonra otomatik giriş yapılır."""
    if request.user.is_authenticated:
        return redirect("polls:index")

    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Hoş geldin! Hesabın hazır 🎉")
        return redirect("polls:index")

    return render(request, "registration/register.html", {"form": form})


class GirisView(LoginView):
    template_name = "registration/login.html"
    form_class = EmailOrUsernameAuthenticationForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, "Tekrar hoş geldin! 👋")
        return super().form_valid(form)


class CikisView(LogoutView):
    """Çıkış yalnızca POST ile kabul edilir (Django 5 varsayılanı)."""

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        messages.success(request, "Çıkış yapıldı. Görüşürüz! 👋")
        return response
