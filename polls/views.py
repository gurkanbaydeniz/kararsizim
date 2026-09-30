from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from .forms import EmailOrUsernameAuthenticationForm, PollForm, RegisterForm
from .models import Poll, Vote
from .utils import get_voter_key, peek_voter_key

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
    """Anket detayı: oylama modu veya sonuç modu (doct/PROJE.md Bölüm 5)."""
    poll = get_object_or_404(
        Poll.objects.select_related("creator").annotate(
            total_votes=Count("votes", distinct=True)
        ),
        pk=pk,
    )
    # Not: annotate() Meta.ordering'i uygulamayabilir; sırayı açıkça veriyoruz
    choices = list(
        poll.choices.annotate(vote_count=Count("votes")).order_by("position", "id")
    )

    voter_key = peek_voter_key(request)
    my_vote = (
        Vote.objects.filter(poll=poll, voter_key=voter_key).select_related("choice").first()
        if voter_key
        else None
    )
    has_voted = my_vote is not None
    sonuc_acik = has_voted or request.GET.get("sonuc") == "1"

    toplam = poll.total_votes
    max_votes = max((c.vote_count for c in choices), default=0)
    results = [
        {
            "text": c.text,
            "votes": c.vote_count,
            "percent": round(c.vote_count * 100 / toplam) if toplam else 0,
            "is_mine": has_voted and c.id == my_vote.choice_id,
            "is_winner": max_votes > 0 and c.vote_count == max_votes,
        }
        for c in choices
    ]

    return render(
        request,
        "polls/poll_detail.html",
        {
            "poll": poll,
            "choices": choices,
            "results": results,
            "has_voted": has_voted,
            "sonuc_acik": sonuc_acik,
        },
    )


def vote(request, pk):
    """Oy kullanma (misafir dahil herkese açık, yalnızca POST)."""
    poll = get_object_or_404(Poll, pk=pk)

    if request.method != "POST":
        return redirect("polls:poll_detail", pk=pk)

    voter_key = get_voter_key(request)  # misafirse session anahtarı burada oluşur

    if Vote.objects.filter(poll=poll, voter_key=voter_key).exists():
        messages.info(request, "Bu ankete zaten oy verdin.")
        return redirect("polls:poll_detail", pk=pk)

    choice = poll.choices.filter(pk=request.POST.get("choice_id")).first()
    if choice is None:
        messages.error(request, "Geçersiz seçenek — tekrar dener misin?")
        return redirect("polls:poll_detail", pk=pk)

    try:
        with transaction.atomic():
            Vote.objects.create(
                poll=poll,
                choice=choice,
                voter_key=voter_key,
                user=request.user if request.user.is_authenticated else None,
            )
    except IntegrityError:
        # Yarış durumu: aynı anahtarla eşzamanlı ikinci oy (unique constraint yakalar)
        messages.info(request, "Bu ankete zaten oy verdin.")
        return redirect("polls:poll_detail", pk=pk)

    messages.success(request, "Oyun kaydedildi 🎉")
    return redirect("polls:poll_detail", pk=pk)


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


@login_required
def poll_delete(request, pk):
    """Anket sahibi kendi anketini silebilir (onaylı; oylarla birlikte kaldırılır)."""
    poll = get_object_or_404(Poll, pk=pk)
    if request.method == "POST" and poll.creator_id == request.user.id:
        poll.delete()
        messages.success(request, "Anketin silindi. Gerisi sana kalmış! 🧹")
        return redirect("polls:my_polls")
    messages.error(request, "Bu anketi silme yetkin yok.")
    return redirect("polls:poll_detail", pk=pk)


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
