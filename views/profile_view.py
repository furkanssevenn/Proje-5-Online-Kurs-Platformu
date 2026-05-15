"""
═══════════════════════════════════════════════════════════════════════════
  PROFİL — Bilgi güncelleme + şifre değiştirme
═══════════════════════════════════════════════════════════════════════════
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QScrollArea, QFrame, QPushButton, QLineEdit,
                             QTextEdit, QSizePolicy)

from widgets.modern import Avatar, ToastYoneticisi, temizle_layout


class ProfileView(QWidget):
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

        self.ic = QWidget()
        scroll.setWidget(self.ic)
        self.v = QVBoxLayout(self.ic)
        self.v.setContentsMargins(28, 24, 28, 28)
        self.v.setSpacing(18)

    def yenile(self, **_):
        temizle_layout(self.v)

        # Güncel kullanıcıyı tekrar çek
        k = self.services["kul"].getir(self.kullanici["id"]) or self.kullanici

        # ── Üst karşılama kartı ──
        ust = QFrame()
        ust.setProperty("card", True)
        h = QHBoxLayout(ust)
        h.setContentsMargins(24, 20, 24, 20)
        h.setSpacing(16)

        h.addWidget(Avatar(k.get("ad", "?"), k.get("soyad", ""),
                           k.get("avatar_renk") or "#6366f1", 72))

        v = QVBoxLayout()
        v.setSpacing(4)
        ad = QLabel(f"{k.get('ad','')} {k.get('soyad','')}")
        ad.setProperty("pageTitle", True)
        v.addWidget(ad)
        ku = QLabel(f"@{k.get('kullanici_adi','')}  ·  {k.get('eposta','')}")
        ku.setProperty("muted", True)
        v.addWidget(ku)

        rol_emoji = {"admin": "🛡️ Yönetici", "egitmen": "🎓 Eğitmen",
                     "ogrenci": "📖 Öğrenci"}
        rol = QLabel(rol_emoji.get(k.get("rol", "ogrenci"), ""))
        rol.setProperty("chip", True)
        rol.setProperty("chipBrand", True)
        v.addWidget(rol, 0, Qt.AlignLeft)
        h.addLayout(v, 1)
        self.v.addWidget(ust)

        # ── İki kolon: Bilgileri Güncelle / Şifre Değiştir ──
        kolon = QHBoxLayout()
        kolon.setSpacing(16)
        kolon.addWidget(self._bilgi_karti(k), 1)
        kolon.addWidget(self._sifre_karti(), 1)
        self.v.addLayout(kolon)

        self.v.addStretch()

    # ───── BİLGİ ─────
    def _bilgi_karti(self, k: dict) -> QFrame:
        kart = QFrame()
        kart.setProperty("card", True)
        v = QVBoxLayout(kart)
        v.setContentsMargins(20, 18, 20, 18)
        v.setSpacing(10)

        b = QLabel("📝  Profil Bilgilerini Güncelle")
        b.setProperty("sectionTitle", True)
        v.addWidget(b)

        v.addWidget(self._etiket("Ad"))
        self._ad = QLineEdit(k.get("ad", ""))
        v.addWidget(self._ad)

        v.addWidget(self._etiket("Soyad"))
        self._soyad = QLineEdit(k.get("soyad", ""))
        v.addWidget(self._soyad)

        v.addWidget(self._etiket("Biyografi"))
        self._bio = QTextEdit(k.get("biyografi") or "")
        self._bio.setPlaceholderText("Kendiniz hakkında kısa bir bilgi...")
        self._bio.setMaximumHeight(120)
        v.addWidget(self._bio)

        gn = QPushButton("💾  Bilgileri Kaydet")
        gn.setProperty("primary", True)
        gn.setMinimumHeight(40)
        gn.setCursor(Qt.PointingHandCursor)
        gn.clicked.connect(self._bilgi_kaydet)
        v.addWidget(gn)
        v.addStretch()
        return kart

    # ───── ŞİFRE ─────
    def _sifre_karti(self) -> QFrame:
        kart = QFrame()
        kart.setProperty("card", True)
        v = QVBoxLayout(kart)
        v.setContentsMargins(20, 18, 20, 18)
        v.setSpacing(10)

        b = QLabel("🔐  Şifre Değiştir")
        b.setProperty("sectionTitle", True)
        v.addWidget(b)

        v.addWidget(self._etiket("Mevcut Şifre"))
        self._eski = QLineEdit()
        self._eski.setEchoMode(QLineEdit.Password)
        self._eski.setPlaceholderText("••••••••")
        v.addWidget(self._eski)

        v.addWidget(self._etiket("Yeni Şifre (en az 6 karakter)"))
        self._yeni1 = QLineEdit()
        self._yeni1.setEchoMode(QLineEdit.Password)
        self._yeni1.setPlaceholderText("••••••••")
        v.addWidget(self._yeni1)

        v.addWidget(self._etiket("Yeni Şifre (Tekrar)"))
        self._yeni2 = QLineEdit()
        self._yeni2.setEchoMode(QLineEdit.Password)
        self._yeni2.setPlaceholderText("••••••••")
        v.addWidget(self._yeni2)

        gn = QPushButton("🔑  Şifreyi Değiştir")
        gn.setProperty("primary", True)
        gn.setMinimumHeight(40)
        gn.setCursor(Qt.PointingHandCursor)
        gn.clicked.connect(self._sifre_kaydet)
        v.addWidget(gn)
        v.addStretch()
        return kart

    def _etiket(self, m: str) -> QLabel:
        l = QLabel(m)
        l.setStyleSheet("font-size: 12px; font-weight: 600; background: transparent;")
        return l

    def _bilgi_kaydet(self):
        ad = self._ad.text().strip()
        soyad = self._soyad.text().strip()
        bio = self._bio.toPlainText().strip()
        if not (ad and soyad):
            ToastYoneticisi.goster(self.mw, "Ad ve soyad gerekli.", "uyari")
            return
        self.services["kul"].guncelle(self.kullanici["id"],
            ad=ad, soyad=soyad, biyografi=bio)
        # Oturumdaki kullanıcıyı güncelle
        self.kullanici["ad"] = ad
        self.kullanici["soyad"] = soyad
        self.kullanici["biyografi"] = bio
        self.services["logger"].info("profil",
            "Profil güncellendi", kullanici_id=self.kullanici["id"])
        ToastYoneticisi.goster(self.mw, "✅ Profil güncellendi.", "basari")

    def _sifre_kaydet(self):
        eski = self._eski.text()
        y1 = self._yeni1.text()
        y2 = self._yeni2.text()
        if not (eski and y1 and y2):
            ToastYoneticisi.goster(self.mw, "Tüm alanları doldurun.", "uyari")
            return
        if y1 != y2:
            ToastYoneticisi.goster(self.mw, "Yeni şifreler eşleşmiyor.", "hata")
            return
        sonuc = self.services["kul"].sifre_degistir(self.kullanici["id"], eski, y1)
        if sonuc["basarili"]:
            self.services["logger"].info("auth",
                "Şifre değişti", kullanici_id=self.kullanici["id"])
            ToastYoneticisi.goster(self.mw, "🔐 Şifre değiştirildi.", "basari")
            self._eski.clear(); self._yeni1.clear(); self._yeni2.clear()
        else:
            ToastYoneticisi.goster(self.mw, sonuc.get("mesaj", "Hata"), "hata")
