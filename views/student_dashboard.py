"""
═══════════════════════════════════════════════════════════════════════════
  ÖĞRENCİ PANELİ — Kayıtlı kurslar, ilerleme, favoriler, bildirimler
═══════════════════════════════════════════════════════════════════════════
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QScrollArea, QFrame, QPushButton, QGridLayout,
                             QProgressBar, QSizePolicy, QTabWidget)

from widgets.modern import (StatCard, CourseCard, SectionHeader,
                            ProgressRing, GradientBanner, ToastYoneticisi,
                            kart_olustur, temizle_layout)


class _KayitliKursSatiri(QFrame):
    def __init__(self, kurs: dict, on_ac, parent=None):
        super().__init__(parent)
        self.setProperty("card", True)
        self.setProperty("cardHover", True)
        self.setCursor(Qt.PointingHandCursor)
        self._on_ac = on_ac
        self._kurs_id = kurs["id"]

        h = QHBoxLayout(self)
        h.setContentsMargins(16, 14, 16, 14)
        h.setSpacing(16)

        # Sol mini banner
        renkler = (kurs.get("kapak_renk") or "#6366f1,#8b5cf6").split(",")
        ic = QLabel("📚")
        ic.setFixedSize(56, 56)
        ic.setAlignment(Qt.AlignCenter)
        ic.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 {renkler[0].strip()},stop:1 {renkler[1].strip() if len(renkler)>1 else renkler[0]});
            border-radius: 12px; font-size: 26px;
        """)
        h.addWidget(ic, 0, Qt.AlignTop)

        # Orta: ad + eğitmen + progress bar
        v = QVBoxLayout()
        v.setSpacing(6)
        ad = QLabel(kurs["ad"])
        ad.setStyleSheet("font-size: 15px; font-weight: 700; background: transparent;")
        v.addWidget(ad)

        eg = QLabel(f"👤 {kurs.get('egitmen_ad','')} {kurs.get('egitmen_soyad','')}")
        eg.setProperty("muted", True)
        eg.setStyleSheet("font-size: 12px; background: transparent;")
        v.addWidget(eg)

        # Progress
        pr_row = QHBoxLayout()
        pr_row.setSpacing(10)
        pb = QProgressBar()
        pb.setMaximum(100)
        pb.setValue(int(kurs.get("ilerleme", 0)))
        pb.setTextVisible(False)
        pb.setFixedHeight(8)
        pr_row.addWidget(pb, 1)
        yz = QLabel(f"%{int(kurs.get('ilerleme', 0))}")
        yz.setStyleSheet("font-size: 12px; font-weight: 700; min-width: 36px; background: transparent;")
        pr_row.addWidget(yz)
        v.addLayout(pr_row)
        h.addLayout(v, 1)

        # Sağ: tamamlandı chip + buton
        sag = QVBoxLayout()
        sag.setSpacing(6)
        sag.setAlignment(Qt.AlignRight | Qt.AlignTop)
        if kurs.get("tamamlandi"):
            ch = QLabel("✓ Tamamlandı")
            ch.setProperty("chip", True)
            ch.setProperty("chipSuccess", True)
            sag.addWidget(ch)
        else:
            ch = QLabel("📖 Devam Ediyor")
            ch.setProperty("chip", True)
            ch.setProperty("chipInfo", True)
            sag.addWidget(ch)
        ac = QPushButton("Aç →")
        ac.setProperty("ghost", True)
        ac.setCursor(Qt.PointingHandCursor)
        ac.clicked.connect(lambda: self._on_ac(self._kurs_id))
        sag.addWidget(ac)
        h.addLayout(sag)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._on_ac(self._kurs_id)


class StudentDashboard(QWidget):
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
        self.v.setSpacing(20)

    def yenile(self, **_):
        # Temizle
        temizle_layout(self.v)

        # Sadece öğrenci hesapları için
        if self.kullanici.get("rol") != "ogrenci":
            uy = QLabel(
                "ℹ️ Bu panel sadece öğrenci hesapları içindir.\n"
                "Eğitmen panelini kullanmak için sol menüden 'Eğitmen Panelim'i seçin.")
            uy.setProperty("muted", True)
            uy.setAlignment(Qt.AlignCenter)
            uy.setMinimumHeight(200)
            self.v.addWidget(uy)
            return

        og = self.services["ogrenci"].kullanici_id_ile_bul(self.kullanici["id"])
        if not og:
            l = QLabel("⚠ Öğrenci kaydı bulunamadı.")
            l.setProperty("muted", True)
            self.v.addWidget(l)
            return

        kurslar = self.services["ogrenci"].kurs_listesi(og["id"])

        # ── Stat kartlar ──
        toplam = len(kurslar)
        tamamlanan = sum(1 for k in kurslar if k.get("ilerleme", 0) >= 100)
        devam = toplam - tamamlanan
        ort_iler = (sum(k.get("ilerleme", 0) for k in kurslar) // toplam) if toplam else 0

        stat_row = QHBoxLayout()
        stat_row.setSpacing(14)
        for bas, deg, em, rk in [
            ("Kayıtlı Kurs", str(toplam),     "📚", "#6366f1,#8b5cf6"),
            ("Tamamlanan",   str(tamamlanan), "✅", "#10b981,#14b8a6"),
            ("Devam Eden",   str(devam),      "📖", "#3b82f6,#06b6d4"),
            ("Ort. İlerleme", f"%{ort_iler}", "📊", "#ec4899,#f43f5e"),
        ]:
            stat_row.addWidget(StatCard(bas, deg, em, rk))
        self.v.addLayout(stat_row)

        # ── Tabs: Kayıtlı kurslar / Favoriler / Bildirimler ──
        sekme = QTabWidget()

        # Kayıtlı kurslar sekmesi
        kayit_w = QWidget()
        kayit_v = QVBoxLayout(kayit_w)
        kayit_v.setContentsMargins(16, 16, 16, 16)
        kayit_v.setSpacing(10)
        if not kurslar:
            bos = QLabel("📭 Henüz hiçbir kursa kayıtlı değilsin.\nKurslar sayfasından bir tane seçebilirsin.")
            bos.setProperty("muted", True)
            bos.setAlignment(Qt.AlignCenter)
            bos.setMinimumHeight(140)
            kayit_v.addWidget(bos)
        else:
            for k in kurslar:
                kayit_v.addWidget(_KayitliKursSatiri(
                    k, on_ac=lambda kid: self.mw.sayfayaGec("kurs_detay", kurs_id=kid)))
            kayit_v.addStretch()
        sekme.addTab(kayit_w, f"📚  Kayıtlı Kurslarım ({toplam})")

        # Favoriler sekmesi
        fav_w = QWidget()
        fav_v = QVBoxLayout(fav_w)
        fav_v.setContentsMargins(16, 16, 16, 16)
        fav_v.setSpacing(10)
        favoriler = self.services["favori"].kullanici_favorileri(self.kullanici["id"])
        if not favoriler:
            bos = QLabel("⭐ Favori listende henüz bir kurs yok.")
            bos.setProperty("muted", True)
            bos.setAlignment(Qt.AlignCenter)
            bos.setMinimumHeight(140)
            fav_v.addWidget(bos)
        else:
            grid = QGridLayout()
            grid.setSpacing(14)
            for i, k in enumerate(favoriler):
                kart = CourseCard(k)
                kart.tiklandi.connect(
                    lambda kid=k["id"]: self.mw.sayfayaGec("kurs_detay", kurs_id=kid))
                grid.addWidget(kart, i // 3, i % 3)
            holder = QWidget()
            holder.setLayout(grid)
            fav_v.addWidget(holder)
            fav_v.addStretch()
        sekme.addTab(fav_w, f"⭐  Favorilerim ({len(favoriler)})")

        # Son bildirimler sekmesi
        bld_w = QWidget()
        bld_v = QVBoxLayout(bld_w)
        bld_v.setContentsMargins(16, 16, 16, 16)
        bld_v.setSpacing(8)
        bildirimler = self.services["bildirim"].kullanici_bildirimleri(self.kullanici["id"])[:10]
        if not bildirimler:
            bos = QLabel("🔔 Henüz bildirim yok.")
            bos.setProperty("muted", True)
            bos.setAlignment(Qt.AlignCenter)
            bos.setMinimumHeight(140)
            bld_v.addWidget(bos)
        else:
            for b in bildirimler:
                bld_v.addWidget(self._bildirim_satiri(b))
            bld_v.addStretch()
        sekme.addTab(bld_w, f"🔔  Son Bildirimler")

        self.v.addWidget(sekme, 1)

    def _bildirim_satiri(self, b: dict) -> QFrame:
        f = QFrame()
        f.setProperty("card", True)
        h = QHBoxLayout(f)
        h.setContentsMargins(14, 12, 14, 12)
        h.setSpacing(12)

        ren = {"basari": "#10b981", "hata": "#ef4444",
               "uyari": "#f59e0b", "bilgi": "#3b82f6"}.get(b.get("tip", "bilgi"), "#3b82f6")
        sem = {"basari": "✓", "hata": "✕", "uyari": "!", "bilgi": "i"}.get(b.get("tip", "bilgi"), "i")
        ic = QLabel(sem)
        ic.setFixedSize(32, 32)
        ic.setAlignment(Qt.AlignCenter)
        ic.setStyleSheet(f"""
            background: {ren}; color: white; border-radius: 16px;
            font-weight: 800; font-size: 13px;
        """)
        h.addWidget(ic)

        v = QVBoxLayout()
        v.setSpacing(2)
        bas = QLabel(b.get("baslik", ""))
        bas.setStyleSheet("font-weight: 700; font-size: 13px; background: transparent;")
        v.addWidget(bas)
        if b.get("mesaj"):
            m = QLabel(b["mesaj"])
            m.setProperty("muted", True)
            m.setWordWrap(True)
            v.addWidget(m)
        h.addLayout(v, 1)

        tar = QLabel((b.get("tarih") or "")[:16])
        tar.setProperty("dim", True)
        tar.setAlignment(Qt.AlignTop)
        h.addWidget(tar)
        return f
