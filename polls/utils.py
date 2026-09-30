"""Kararsızım — ortak yardımcılar (doct/PROJE.md Bölüm 4)."""
import uuid


def get_voter_key(request):
    """Oy verici anahtarı: üyeler için 'user:<id>', misafirler için session'daki 'guest:<uuid>'.

    Misafir için anahtar yoksa OLUŞTURUR — bu yüzden yalnızca oy verme anında çağrılmalı;
    sayfa görüntüleyen herkese gereksiz session çerezi verilmesin.
    """
    if request.user.is_authenticated:
        return f"user:{request.user.id}"
    if not request.session.get("guest_key"):
        request.session["guest_key"] = uuid.uuid4().hex
    return f"guest:{request.session['guest_key']}"


def peek_voter_key(request):
    """get_voter_key'in session OLUŞTURMAYAN hali.

    Detay sayfasında 'oy vermiş mi?' kontrolü için: misafirin anahtarı henüz yoksa
    None döner (yani oy vermemiştir, ekran oylama modunda açılır).
    """
    if request.user.is_authenticated:
        return f"user:{request.user.id}"
    guest = request.session.get("guest_key")
    return f"guest:{guest}" if guest else None
