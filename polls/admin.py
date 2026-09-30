from django.contrib import admin

from .models import Choice, Poll, Vote


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ("question", "creator", "created_at")
    search_fields = ("question", "creator__username")
    list_filter = ("created_at",)
    inlines = [ChoiceInline]


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ("poll", "choice", "voter_key", "created_at")
    list_filter = ("poll",)
