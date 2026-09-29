"""Kararsızım — üyelik formları (Faz 1).

Django'nun yerleşik mesajları LANGUAGE_CODE="tr" sayesinde otomatik Türkçe gelir;
burada yalnızca özel kuralların (e-posta tekliği, e-posta ile giriş) mesajları yazılır.
"""
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    """Kayıt formu: kullanıcı adı + e-posta (tek) + parola x2."""

    email = forms.EmailField(
        label="E-posta",
        required=True,
        help_text="E-posta adresin kimseye gösterilmez, yalnızca hesap işlemleri için kullanılır.",
        error_messages={
            "required": "E-posta adresi zorunludur.",
            "invalid": "Geçerli bir e-posta adresi girin.",
        },
    )

    class Meta:
        model = User
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["placeholder"] = "kullaniciadi"
        self.fields["email"].widget.attrs["placeholder"] = "ornek@eposta.com"
        self.fields["password1"].widget.attrs["placeholder"] = "••••••••"
        self.fields["password2"].widget.attrs["placeholder"] = "••••••••"

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Bu e-posta adresi zaten kayıtlı.")
        return email


class EmailOrUsernameAuthenticationForm(AuthenticationForm):
    """Giriş formu: kullanıcı adı VEYA e-posta + parola."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Kullanıcı adı veya e-posta"
        self.fields["username"].widget.attrs["placeholder"] = "kullaniciadi veya ornek@eposta.com"
        self.fields["password"].widget.attrs["placeholder"] = "••••••••"

    def clean(self):
        # E-posta girildiyse, karşılık gelen kullanıcı adına çevrilerek doğrulanır
        kimlik = self.cleaned_data.get("username")
        if kimlik and "@" in kimlik:
            user = User.objects.filter(email__iexact=kimlik).first()
            if user:
                self.cleaned_data["username"] = user.username
        return super().clean()
