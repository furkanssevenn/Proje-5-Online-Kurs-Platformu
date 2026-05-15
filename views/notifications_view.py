"""
═══════════════════════════════════════════════════════════════════════════
  BİLDİRİMLER — Liste + okundu işaretleme
═══════════════════════════════════════════════════════════════════════════
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QScrollArea, QFrame, QPushButton)

from widgets.modern import ToastYoneticisi, temizle_layout


class NotificationsView(QWidget):
    def __init__(self, vt, kullanici, services, main_window):
        super().__init__()
        self.vt = vt
        self.kullanici = kullanici
        self.services = services
        self.mw = main_window

        ana = QVBoxLayout(self)
        ana.setContentsMargins(0, 0, 0, 0)

        ust = QFrame()
        uh = QHBoxLayout(ust)
        uh.setContentsMargins(28, 18, 28, 12)
        uh.setSpacing(10)

        bas_v = QVBoxLayout()
        bas_v.setSpacing(2)
        b = QLabel("🔔  Bildirimlerin")
        b.setProperty("pageTitle", True)
        bas_v.addWidget(b)
        self.alt_lbl = QLabel("")
        self.alt_lbl.setProperty("muted", True)
        bas_v.addWidget(self.alt_lbl)
        uh.addLayout(bas_v)
        uh.addStretch()

        self.tum_okundu_btn = QPushButton("✓  Tümünü Okundu İşaretle")
        self.tum_okundu_btn.setCursor(Qt.PointingHandCursor)
        self.tum_okundu_btn.clicked.connect(self._tumu_okundu)
        uh.addWidget(self.tum_okundu_btn)

        ana.addWidget(ust)

        # Liste
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        ana.addWidget(scroll)

        self.ic = QWidget()
        scroll.setWidget(self.ic)
        self.v = QVBoxLayout(self.ic)
        self.v.setContentsMargins(28, 0, 28, 28)
        self.v.setSpacing(8)

    def yenile(self, **_):
        temizle_layout(self.v)

        bildirimler = self.services["bildirim"].kullanici_bildirimleri(self.kullanici["id"])
        okunmamis = sum(1 for b in bildirimler if not b.get("okundu"))
        self.alt_lbl.setText(f"Toplam {len(bildirimler)} bildirim · {okunmamis} okunmamış")
        self.tum_okundu_btn.setEnabled(okunmamis > 0)

        if not bildirimler:
            bos = QLabel("📭 Henüz hiç bildirim yok.\nKursa kayıt olduğunda veya yeni bir duyuru geldiğinde burada görünecek.")
            bos.setProperty("muted", True)
            bos.setAlignment(Qt.AlignCenter)
            bos.setMinimumHeight(220)
            self.v.addWidget(bos)
            return

        for b in bildirimler:
            self.v.addWidget(self._satir(b))
        self.v.addStretch()

    def _satir(self, b: dict) -> QFrame:
        f = QFrame()
        f.setProperty("card", True)
        f.setProperty("cardHover", True)

        # Okunmamışsa farklı stil
        okunmadi = not b.get("okundu")
        if okunmadi:
            f.setStyleSheet("QFrame[card='true']{ background: rgba(99,102,241,0.08); border-color: rgba(99,102,241,0.30); }")

        h = QHBoxLayout(f)
        h.setContentsMargins(16, 14, 16, 14)
        h.setSpacing(12)

        # Tip ikonu
        ren = {"basari": "#10b981", "hata": "#ef4444",
               "uyari": "#f59e0b", "bilgi": "#3b82f6"}.get(b.get("tip", "bilgi"), "#3b82f6")
        sem = {"basari": "✓", "hata": "✕",
               "uyari": "!", "bilgi": "i"}.get(b.get("tip", "bilgi"), "i")
        ic = QLabel(sem)
        ic.setFixedSize(34, 34)
        ic.setAlignment(Qt.AlignCenter)
        ic.setStyleSheet(f"""
            background: {ren}; color: white; border-radius: 17px;
            font-weight: 800; font-size: 14px;
        """)
        h.addWidget(ic, 0, Qt.AlignTop)

        # İçerik
        v = QVBoxLayout()
        v.setSpacing(3)
        bas_row = QHBoxLayout()
        bas_row.setSpacing(8)
        bas = QLabel(b.get("baslik", ""))
        bas.setStyleSheet("font-weight: 700; font-size: 14px; background: transparent;")
        bas_row.addWidget(bas)
        if okunmadi:
            yeni = QLabel("●")
            yeni.setStyleSheet("color: #6366f1; font-size: 12px; background: transparent;")
            bas_row.addWidget(yeni)
        bas_row.addStretch()
        tar = QLabel((b.get("tarih") or "")[:16])
        tar.setProperty("dim", True)
        bas_row.addWidget(tar)
        v.addLayout(bas_row)

        if b.get("mesaj"):
            m = QLabel(b["mesaj"])
            m.setProperty("muted", True)
            m.setWordWrap(True)
            v.addWidget(m)
        h.addLayout(v, 1)

        # Okundu butonu
        if okunmadi:
            ok = QPushButton("Okundu")
            ok.setProperty("ghost", True)
            ok.setCursor(Qt.PointingHandCursor)
            ok.clicked.connect(lambda: self._okundu(b["id"]))
            h.addWidget(ok)
        return f

    def _okundu(self, bid: int):
        self.services["bildirim"].okundu_isaretle(bid)
        self.mw.bildirim_sayisini_guncelle()
        self.yenile()

    def _tumu_okundu(self):
        sonuc = self.services["bildirim"].tumu_okundu(self.kullanici["id"])
        ToastYoneticisi.goster(self.mw,
            f"✓ {sonuc.get('guncellenen', 0)} bildirim okundu olarak işaretlendi.", "basari")
        self.mw.bildirim_sayisini_guncelle()
        self.yenile()
