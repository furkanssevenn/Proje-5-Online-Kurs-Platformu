"""
═══════════════════════════════════════════════════════════════════════════
  ANA SAYFA (Hero + öne çıkan kurslar + kategoriler)
═══════════════════════════════════════════════════════════════════════════
"""
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QLinearGradient, QFont, QPainterPath
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QScrollArea, QFrame, QPushButton,
                             QGridLayout, QSizePolicy)

from widgets.modern import (StatCard, CourseCard, SectionHeader,
                            kart_olustur, GradientBanner)


class HeroBanner(QFrame):
    def __init__(self, ad: str = "", parent=None):
        super().__init__(parent)
        self.ad = ad or "Öğrenci"
        self.setMinimumHeight(200)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        v = QVBoxLayout(self)
        v.setContentsMargins(36, 30, 36, 30)
        v.setSpacing(8)

        chip = QLabel("⚡ Yeni Sezon Başladı")
        chip.setStyleSheet(
            "background: rgba(255,255,255,0.18); color: white; "
            "padding: 5px 14px; border-radius: 12px; font-size: 11px; "
            "font-weight: 600; max-height: 24px;"
        )
        chip.setMaximumWidth(150)
        v.addWidget(chip)

        b = QLabel(f"Hoş geldin, {self.ad} 👋")
        b.setStyleSheet(
            "font-size: 30px; font-weight: 800; color: white; background: transparent;"
        )
        v.addWidget(b)

        s = QLabel("Yeni şeyler keşfetmek, yeni şeyler öğrenmek için harika bir gün.")
        s.setStyleSheet("font-size: 14px; color: rgba(255,255,255,0.9); background: transparent;")
        v.addWidget(s)

        v.addStretch()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 16, 16)
        p.setClipPath(path)

        g = QLinearGradient(0, 0, self.width(), self.height())
        g.setColorAt(0, QColor("#4338ca"))
        g.setColorAt(0.6, QColor("#7c3aed"))
        g.setColorAt(1, QColor("#db2777"))
        p.fillRect(self.rect(), g)

        p.setPen(Qt.NoPen)
        p.setBrush(QColor(255, 255, 255, 22))
        p.drawEllipse(self.width() - 200, -60, 320, 320)
        p.setBrush(QColor(255, 255, 255, 14))
        p.drawEllipse(self.width() - 350, self.height() - 100, 200, 200)


class CategoryCard(QFrame):
    KAT = [
        ("💻", "Programlama",   "#6366f1,#8b5cf6"),
        ("🌐", "Web Geliştirme", "#06b6d4,#3b82f6"),
        ("📊", "Veri Bilimi",   "#10b981,#14b8a6"),
        ("🎨", "Tasarım",        "#ec4899,#f43f5e"),
        ("📚", "Genel",          "#f97316,#eab308"),
    ]

    def __init__(self, emoji, ad, renk, sayi, on_click=None, parent=None):
        super().__init__(parent)
        self.setProperty("card", True)
        self.setProperty("cardHover", True)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(140)
        self._on_click = on_click

        v = QVBoxLayout(self)
        v.setContentsMargins(18, 16, 18, 16)
        v.setSpacing(6)

        ic = QLabel(emoji)
        ic.setFixedSize(46, 46)
        ic.setAlignment(Qt.AlignCenter)
        renkler = renk.split(",")
        ic.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 {renkler[0]},stop:1 {renkler[1]});
            border-radius: 12px;
            font-size: 22px;
        """)
        v.addWidget(ic)

        ad_lbl = QLabel(ad)
        ad_lbl.setStyleSheet("font-size: 15px; font-weight: 700; background: transparent;")
        v.addWidget(ad_lbl)

        say_lbl = QLabel(f"{sayi} kurs")
        say_lbl.setProperty("muted", True)
        say_lbl.setStyleSheet("font-size: 12px; background: transparent;")
        v.addWidget(say_lbl)
        v.addStretch()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton and self._on_click:
            self._on_click()


class HomeView(QWidget):
    def __init__(self, vt, kullanici, services, main_window):
        super().__init__()
        self.vt = vt
        self.kullanici = kullanici
        self.services = services
        self.mw = main_window

        ana = QVBoxLayout(self)
        ana.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        ana.addWidget(scroll)

        ic = QFrame()
        ic.setObjectName("RootBg")
        scroll.setWidget(ic)
        v = QVBoxLayout(ic)
        v.setContentsMargins(28, 24, 28, 28)
        v.setSpacing(22)

        # Hero
        v.addWidget(HeroBanner(kullanici.get("ad", "")))

        # Stat kartlar
        self.stat_row = QHBoxLayout()
        self.stat_row.setSpacing(14)
        v.addLayout(self.stat_row)

        # Kategoriler
        v.addWidget(SectionHeader("Kategoriler", "İlgi alanına göre kurs keşfet"))
        self.kat_grid = QGridLayout()
        self.kat_grid.setSpacing(14)
        kat_w = QWidget()
        kat_w.setLayout(self.kat_grid)
        v.addWidget(kat_w)

        # Öne çıkan kurslar
        v.addWidget(SectionHeader("🔥 Öne Çıkan Kurslar", "En popüler 6 kurs"))
        self.kurs_grid = QGridLayout()
        self.kurs_grid.setSpacing(14)
        kurs_w = QWidget()
        kurs_w.setLayout(self.kurs_grid)
        v.addWidget(kurs_w)

        v.addStretch()

    def yenile(self, **_):
        # ── Stat kartlarını yenile ──
        self._temizle(self.stat_row)
        ist = self.services["istatistik"].genel_istatistikler()
        for baslik, deger, emoji, renk in [
            ("Toplam Kurs",     str(ist["toplam_kurs"]),       "📚", "#6366f1,#8b5cf6"),
            ("Eğitmen",         str(ist["toplam_egitmen"]),    "🎓", "#10b981,#14b8a6"),
            ("Öğrenci",         str(ist["toplam_ogrenci"]),    "👥", "#06b6d4,#3b82f6"),
            ("Toplam Kayıt",    str(ist["toplam_kayit"]),      "📝", "#ec4899,#f43f5e"),
        ]:
            self.stat_row.addWidget(StatCard(baslik, deger, emoji, renk))

        # ── Kategoriler ──
        self._temizle_grid(self.kat_grid)
        kat_dag = ist.get("kategori_dagilimi", {})
        for i, (emoji, ad, renk) in enumerate(CategoryCard.KAT):
            sayi = kat_dag.get(ad, 0)
            kart = CategoryCard(emoji, ad, renk, sayi,
                                on_click=lambda a=ad: self.mw.sayfayaGec("kurslar", kategori=a))
            self.kat_grid.addWidget(kart, i // 5, i % 5)

        # ── Öne çıkan kurslar (en popüler 6) ──
        self._temizle_grid(self.kurs_grid)
        kurslar = self.services["kurs"].listele()
        # Popülerlikle sırala
        kurslar = sorted(kurslar, key=lambda k: k.get("kayit_sayisi", 0), reverse=True)[:6]
        if not kurslar:
            bos = QLabel("📭 Henüz kurs yok.")
            bos.setProperty("muted", True)
            bos.setAlignment(Qt.AlignCenter)
            bos.setMinimumHeight(120)
            self.kurs_grid.addWidget(bos, 0, 0, 1, 3)
        else:
            for i, k in enumerate(kurslar):
                kart = CourseCard(k)
                kart.tiklandi.connect(
                    lambda kid=k["id"]: self.mw.sayfayaGec("kurs_detay", kurs_id=kid)
                )
                self.kurs_grid.addWidget(kart, i // 3, i % 3)

    def _temizle(self, lay):
        while lay.count():
            it = lay.takeAt(0)
            w = it.widget()
            if w:
                w.deleteLater()

    def _temizle_grid(self, grid):
        while grid.count():
            it = grid.takeAt(0)
            w = it.widget()
            if w:
                w.deleteLater()
