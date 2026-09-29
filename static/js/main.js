// Kararsızım — ince JS katmanı (doct/PROJE.md Bölüm 7.8)
// Faz 0: yalnızca toast bildirimlerinin otomatik kaybolması.
// Sonraki fazlarda: anket formunda dinamik seçenek alanları, "Anketi paylaş" butonu.

document.addEventListener("DOMContentLoaded", function () {
  // Toast mesajlarını ~3 sn sonra yumuşakça gizle
  document.querySelectorAll(".toast").forEach(function (toast) {
    setTimeout(function () {
      toast.style.transition = "opacity .3s ease";
      toast.style.opacity = "0";
      setTimeout(function () { toast.remove(); }, 300);
    }, 3000);
  });
});
