// Kararsızım — ince JS katmanı (doct/PROJE.md Bölüm 7.8)
// 1) Toast bildirimlerinin otomatik kaybolması
// 2) Anket oluşturma: dinamik seçenek satırları (2-5 arası)

document.addEventListener("DOMContentLoaded", function () {
  // --- Toast: ~3 sn sonra yumuşakça kaybol ---
  document.querySelectorAll(".toast").forEach(function (toast) {
    setTimeout(function () {
      toast.style.transition = "opacity .3s ease";
      toast.style.opacity = "0";
      setTimeout(function () { toast.remove(); }, 300);
    }, 3000);
  });

  // --- Anket oluşturma: seçenek satırı ekle/kaldır ---
  var rowsContainer = document.getElementById("choice-rows");
  if (rowsContainer) {
    var rows = Array.prototype.slice.call(rowsContainer.querySelectorAll(".choice-row"));
    var addBtn = document.getElementById("add-choice");
    var MIN = 2;

    // Sayfa yüklenince: değeri olan son satıra kadar göster (en az 2 satır açık kalır)
    var lastFilled = -1;
    rows.forEach(function (row, i) {
      if (row.querySelector("input").value.trim() !== "") lastFilled = i;
    });
    rows.forEach(function (row, i) {
      if (i > Math.max(lastFilled, MIN - 1)) row.classList.add("is-hidden");
    });

    function refresh() {
      var visible = rows.filter(function (r) { return !r.classList.contains("is-hidden"); });
      rows.forEach(function (row) {
        var rm = row.querySelector(".choice-row__remove");
        if (rm) rm.hidden = visible.length <= MIN; // 2 satır kalınca kaldırma kapanır
      });
      if (addBtn) addBtn.disabled = visible.length >= rows.length; // 5 satırda ekleme kapanır
    }

    rows.forEach(function (row) {
      var rm = row.querySelector(".choice-row__remove");
      if (!rm) return;
      rm.addEventListener("click", function () {
        row.querySelector("input").value = "";
        row.classList.add("is-hidden");
        refresh();
      });
    });

    if (addBtn) {
      addBtn.addEventListener("click", function () {
        var next = rows.find(function (r) { return r.classList.contains("is-hidden"); });
        if (next) {
          next.classList.remove("is-hidden");
          next.querySelector("input").focus();
        }
        refresh();
      });
    }

    refresh();
  }
});
