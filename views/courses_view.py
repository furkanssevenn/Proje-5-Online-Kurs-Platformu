"""
═══════════════════════════════════════════════════════════════════════════
  KURSLAR — Listeleme + filtreler
═══════════════════════════════════════════════════════════════════════════
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QScrollArea, QPushButton, QGridLayout,
                             QComboBox, QLineEdit, QFrame)

from widgets.modern import CourseCard, SearchBar


class CoursesView(QWidget):
    KATEGORILER = ["Tümü", "Programlama", "Web Geliştirme", "Veri Bilimi", "Tasarım", "Genel"]
    SEVIYELER   = ["Tümü", "Başlangıç", "Orta", "İleri"]

    def __init__(self, vt, kullanici, services, main_window):
        super().__init__()
        self.vt = vt
        self.kullanici = kullanici
        self.services = services
        self.mw = main_window
        self._arama = ""
        self._kategori = None
        self._seviye = None

        ana = QVBoxLayout(self)
        ana.setContentsMargins(28, 20, 28, 20)
        ana.setSpacing(16)

        # ── Filtre satırı ──
        filtre_row = QHBoxLayout()
        filtre_row.setSpacing(10)

        self.search = SearchBar("Kurs adı veya açıklama ara...")
        self.search.aramaDegisti.connect(self._arama_degisti)
        filtre_row.addWidget(self.search, 1)

        self.kat_combo = QComboBox()
        self.kat_combo.addItems(self.KATEGORILER)
        self.kat_combo.setMinimumWidth(170)
        self.kat_combo.currentTextChanged.connect(self._kategori_degisti)
        filtre_row.addWidget(self.kat_combo)

        self.sev_combo = QComboBox()
        self.sev_combo.addItems(self.SEVIYELER)
        self.sev_combo.setMinimumWidth(140)
        self.sev_combo.currentTextChanged.connect(self._seviye_degisti)
        filtre_row.addWidget(self.sev_combo)

        ana.addLayout(filtre_row)

        # ── Sonuç sayısı ──
        self.sonuc_lbl = QLabel("")
        self.sonuc_lbl.setProperty("muted", True)
        ana.addWidget(self.sonuc_lbl)

        # ── Kurs grid (scroll) ──
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        ana.addWidget(scroll, 1)

        ic = QWidget()
        scroll.setWidget(ic)
        self.grid = QGridLayout(ic)
        self.grid.setSpacing(14)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setAlignment(Qt.AlignTop)

    # ─── Olaylar ────────────────────────────────────────────────────────
    def _arama_degisti(self, t: str):
        self._arama = t.strip() or None
        self._yenile_grid()

    def _kategori_degisti(self, t: str):
        self._kategori = None if t == "Tümü" else t
        self._yenile_grid()

    def _seviye_degisti(self, t: str):
        self._seviye = None if t == "Tümü" else t
        self._yenile_grid()

    # ─── Yenileme ───────────────────────────────────────────────────────
    def yenile(self, kategori: str = None, **_):
        if kategori and kategori in self.KATEGORILER:
            self.kat_combo.setCurrentText(kategori)
        self._yenile_grid()

    def _yenile_grid(self):
        # Grid'i temizle
        while self.grid.count():
            it = self.grid.takeAt(0)
            w = it.widget()
            if w:
                w.deleteLater()

        kurslar = self.services["kurs"].listele(
            kategori=self._kategori,
            seviye=self._seviye,
            arama=self._arama,
        )

        self.sonuc_lbl.setText(f"{len(kurslar)} kurs bulundu")

        if not kurslar:
            bos = QLabel("🔍  Aramanıza uygun kurs bulunamadı.\nFiltreleri değiştirip tekrar deneyin.")
            bos.setProperty("muted", True)
            bos.setAlignment(Qt.AlignCenter)
            bos.setMinimumHeight(200)
            self.grid.addWidget(bos, 0, 0, 1, 3)
            return

        for i, k in enumerate(kurslar):
            kart = CourseCard(k)
            kart.tiklandi.connect(
                lambda kid=k["id"]: self.mw.sayfayaGec("kurs_detay", kurs_id=kid)
            )
            self.grid.addWidget(kart, i // 3, i % 3)
