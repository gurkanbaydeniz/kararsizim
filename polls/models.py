"""Kararsızım — veri modeli (doct/PROJE.md Bölüm 4).

Poll (anket) ← Choice (seçenek) ← Vote (oy). Oylama mantığı Faz 3'te;
şimdilik tablolar oluşturulur.
"""
from django.conf import settings
from django.db import models
from django.utils.timesince import timesince


class Poll(models.Model):
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="polls"
    )
    question = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.question

    @property
    def gecen_sure(self):
        """Kart meta satırı için: '5 dakika önce' / 'az önce'."""
        fark = timesince(self.created_at)
        return "az önce" if fark.startswith("0") else f"{fark} önce"


class Choice(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=80)
    position = models.PositiveSmallIntegerField(default=0)  # seçenek sırası

    class Meta:
        ordering = ["position", "id"]

    def __str__(self):
        return self.text


class Vote(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="votes")
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, related_name="votes")
    # Kullanıcı silinse bile oy sayıları korunur (oy anonim sayılır)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    voter_key = models.CharField(max_length=64)  # "user:<id>" veya "guest:<uuid>"
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            # Bir oy verici, bir ankete yalnızca bir kez oy verebilir (Faz 3'te kullanılacak)
            models.UniqueConstraint(fields=["poll", "voter_key"], name="unique_vote_per_poll"),
        ]

    def __str__(self):
        return f"{self.voter_key} → {self.choice_id}"
