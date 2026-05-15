"""
═══════════════════════════════════════════════════════════════════════════
  SIDEBAR — Sol navigasyon paneli
═══════════════════════════════════════════════════════════════════════════
"""
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QPainter, QColor, QLinearGradient, QBrush
from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QWidget, QSizePolicy)

from widgets.modern import Avatar


class LogoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(40, 40)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        g = QLinearGradient(0, 0, self.width(), self.height())
        g.setColorAt(0, QColor("#6366f1"))
        g.setColorAt(1, QColor("#8b5cf6"))
        p.setBrush(QBrush(g))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(self.rect(), 10, 10)
        p.setPen(QColor("white"))
        f = QFont("Inter", 18, QFont.Bold)
        p.setFont(f)
        p.drawText(self.rect(), Qt.AlignCenter, "K")


class NavButton(QPushButton):
    def __init__(self, ikon: str, etiket: str, anahtar: str, parent=None):
        super().__init__(f"  {ikon}    {etiket}", parent)
        self.anahtar = anahtar
        self.setProperty("sidebar", True)
        self.setCursor(Qt.PointingHandCursor)
        self.setCheckable(True)
        self.setMinimumHeight(42)

    def setActive(self, aktif: bool):
        self.setProperty("active", aktif)
        self.setChecked(aktif)
        self.style().unpolish(self)
        self.style().polish(self)


class Sidebar(QFrame):
    sayfaSecildi = pyqtSignal(str)
    cikisIstendi = pyqtSignal()
    profilIstendi = pyqtSignal()

    NAV_OGRENCI = [
        ("🏠", "Ana Sayfa",     "anasayfa"),
        ("📚", "Kurslar",        "kurslar"),
        ("📊", "Panelim",        "dashboard"),
        ("⭐", "Favoriler",      "favoriler"),
        ("🔔", "Bildirimler",    "bildirimler"),
    ]
    NAV_EGITMEN = [
        ("🏠", "Ana Sayfa",       "anasayfa"),
        ("📚", "Tüm Kurslar",     "kurslar"),
        ("🎓", "Eğitmen Panelim", "egitmen"),
        ("🔔", "Bildirimler",     "bildirimler"),
    ]
    NAV_ADMIN = [
        ("🏠", "Ana Sayfa",         "anasayfa"),
        ("📚", "Tüm Kurslar",       "kurslar"),
        ("🛡️", "Admin Paneli",      "admin"),
        ("👥", "Kullanıcılar",      "admin_kullanicilar"),
        ("🎓", "Eğitmenler",        "admin_egitmenler"),
        ("📖", "Kurs Yönetimi",     "admin_kurslar"),
        ("💬", "Yorum Moderasyonu", "admin_yorumlar"),
        ("📋", "Sistem Logları",    "admin_loglar"),
        ("🔔", "Bildirimler",       "bildirimler"),
    ]

    def __init__(self, kullanici: dict, parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setFixedWidth(260)
        self.kullanici = kullanici
        self._butonlar: dict = {}

        v = QVBoxLayout(self)
        v.setContentsMargins(16, 18, 16, 16)
        v.setSpacing(4)

        # ───── LOGO ─────
        logo_row = QHBoxLayout()
        logo_row.setSpacing(10)
        logo_row.addWidget(LogoWidget())
        marka_v = QVBoxLayout()
        marka_v.setSpacing(0)
        m1 = QLabel("ByTeach")
        m1.setStyleSheet("font-size: 15px; font-weight: 800; background: transparent;")
        marka_v.addWidget(m1)
        m2 = QLabel("Online Eğitim")
        m2.setProperty("dim", True)
        marka_v.addWidget(m2)
        logo_row.addLayout(marka_v)
        logo_row.addStretch()
        v.addLayout(logo_row)

        v.addSpacing(22)

        # ───── BAŞLIK: MENÜ ─────
        bas = QLabel("MENÜ")
        bas.setStyleSheet(
            "font-size: 10px; font-weight: 700; color: #6b7280; "
            "padding-left: 8px; background: transparent;"
        )
        v.addWidget(bas)
        v.addSpacing(6)

        # ───── NAV ─────
        rol = kullanici.get("rol", "ogrenci")
        nav = self.NAV_ADMIN if rol == "admin" \
              else self.NAV_EGITMEN if rol == "egitmen" \
              else self.NAV_OGRENCI

        for ikon, etiket, anahtar in nav:
            btn = NavButton(ikon, etiket, anahtar)
            btn.clicked.connect(lambda _, a=anahtar: self._tiklandi(a))
            self._butonlar[anahtar] = btn
            v.addWidget(btn)

        v.addStretch()

        # ───── KULLANICI KARTI ─────
        v.addWidget(self._kullanici_karti())

    def _kullanici_karti(self) -> QFrame:
        kart = QFrame()
        kart.setProperty("card", True)
        kart.setStyleSheet("QFrame[card='true']{ padding: 0; }")
        h = QHBoxLayout(kart)
        h.setContentsMargins(10, 10, 10, 10)
        h.setSpacing(10)

        av = Avatar(
            self.kullanici.get("ad", "?"),
            self.kullanici.get("soyad", ""),
            self.kullanici.get("avatar_renk") or "#6366f1",
            36
        )
        av.setCursor(Qt.PointingHandCursor)
        av.mousePressEvent = lambda e: self.profilIstendi.emit()
        h.addWidget(av)

        v = QVBoxLayout()
        v.setSpacing(0)
        ad = QLabel(f"{self.kullanici.get('ad','')} {self.kullanici.get('soyad','')}".strip())
        ad.setStyleSheet("font-size: 13px; font-weight: 600; background: transparent;")
        v.addWidget(ad)
        rol = QLabel({
            "admin":   "🛡️ Yönetici",
            "egitmen": "🎓 Eğitmen",
            "ogrenci": "📖 Öğrenci",
        }.get(self.kullanici.get("rol", "ogrenci"), ""))
        rol.setProperty("dim", True)
        v.addWidget(rol)
        h.addLayout(v, 1)

        cikis = QPushButton("🚪")
        cikis.setProperty("ghost", True)
        cikis.setFixedSize(30, 30)
        cikis.setCursor(Qt.PointingHandCursor)
        cikis.setToolTip("Çıkış")
        cikis.setStyleSheet("font-family: 'Segoe UI Emoji', 'Inter', sans-serif; font-size: 14px;")
        cikis.clicked.connect(self.cikisIstendi.emit)
        h.addWidget(cikis)

        return kart

    def _tiklandi(self, anahtar: str):
        self.setActive(anahtar)
        self.sayfaSecildi.emit(anahtar)

    def setActive(self, anahtar: str):
        for k, btn in self._butonlar.items():
            btn.setActive(k == anahtar)
