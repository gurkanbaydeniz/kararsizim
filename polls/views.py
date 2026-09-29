from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render

from .forms import EmailOrUsernameAuthenticationForm, RegisterForm


def index(request):
    """Anasayfa — Faz 2'de anket akışına (poll_list) dönüşecek."""
    return render(request, "polls/poll_list.html")


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


@login_required
def poll_create(request):
    """Anket oluşturma — Faz 2'de gerçek form buraya gelecek."""
    return render(request, "polls/poll_form.html")
