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


MIN_SECENEK = 2
MAKS_SECENEK = 5


class PollForm(forms.Form):
    """Anket oluşturma formu: soru + 2-5 seçenek (doct/PROJE.md Bölüm 6, kural 2)."""

    question = forms.CharField(
        label="Sorun",
        widget=forms.Textarea(
            attrs={"rows": 2, "placeholder": "Örn: Bugün sinemaya mı gitsem, restorana mı?"}
        ),
        error_messages={
            "required": "Soru alanı zorunludur.",
            "min_length": "Soru en az %(min_length)s karakter olmalı.",
            "max_length": "Soru en fazla %(max_length)s karakter olabilir.",
        },
        min_length=10,
        max_length=200,
        help_text="10-200 karakter. Ne kadar net sorarsan o kadar iyi cevap alırsın.",
    )

    # 5 sabit slot; JS görünür satırları yönetir, sunucu boş olanları yok sayar
    choice1 = forms.CharField(required=False)
    choice2 = forms.CharField(required=False)
    choice3 = forms.CharField(required=False)
    choice4 = forms.CharField(required=False)
    choice5 = forms.CharField(required=False)

    def clean(self):
        cleaned = super().clean()
        soru = (cleaned.get("question") or "").strip()
        secenekler = [
            (cleaned.get(f"choice{i}") or "").strip()
            for i in range(1, MAKS_SECENEK + 1)
        ]
        dolu = [s for s in secenekler if s]

        if len(dolu) < MIN_SECENEK:
            raise forms.ValidationError(
                f"En az {MIN_SECENEK} seçenek yazmalısın (boş seçenek kabul edilmez)."
            )
        if any(len(s) > 80 for s in dolu):
            raise forms.ValidationError("Seçenekler en fazla 80 karakter olabilir.")
        kucuk = [s.casefold() for s in dolu]
        if len(set(kucuk)) != len(kucuk):
            raise forms.ValidationError("Aynı seçeneği birden fazla kez yazamazsın.")

        cleaned["question"] = soru
        cleaned["choices"] = dolu
        return cleaned
