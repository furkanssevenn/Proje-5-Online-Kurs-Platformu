"""
═══════════════════════════════════════════════════════════════════════════
  ADMIN PANELLERİ
═══════════════════════════════════════════════════════════════════════════
  • AdminView            — genel istatistikler + grafikler + duyuru
  • AdminUsersView       — kullanıcı yönetimi tablosu
  • AdminInstructorsView — eğitmen kart grid + ekleme formu
  • AdminLogsView        — sistem log tablosu
"""
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPainter, QColor, QFont, QBrush
from PyQt5.QtChart import (QChart, QChartView, QPieSeries, QBarSet,
                           QBarSeries, QBarCategoryAxis, QValueAxis)
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QScrollArea, QFrame, QPushButton, QGridLayout,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QComboBox, QLineEdit, QTextEdit, QSpinBox,
                             QDoubleSpinBox, QSizePolicy, QMessageBox,
                             QAbstractItemView)

from widgets.modern import (StatCard, SectionHeader, ToastYoneticisi,
                            Avatar, GradientBanner, temizle_layout)


# ═════════════════════════════════════════════════════════════════════════
#  ADMIN ANA PANEL — istatistikler, grafikler, duyuru
# ═════════════════════════════════════════════════════════════════════════
class AdminView(QWidget):
    PASTA_RENKLERI = ["#6366f1", "#10b981", "#f59e0b", "#ef4444",
                      "#8b5cf6", "#06b6d4", "#ec4899", "#14b8a6"]

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

        self.ic = QFrame()
        self.ic.setObjectName("RootBg")
        scroll.setWidget(self.ic)
        self.v = QVBoxLayout(self.ic)
        self.v.setContentsMargins(28, 24, 28, 28)
        self.v.setSpacing(20)

    def _yetki_kontrol(self):
        if self.kullanici.get("rol") != "admin":
            uy = QLabel("⛔ Bu sayfa sadece yöneticiler için.")
            uy.setProperty("muted", True)
            uy.setAlignment(Qt.AlignCenter)
            uy.setMinimumHeight(200)
            self.v.addWidget(uy)
            return False
        return True

    def yenile(self, **_):
        temizle_layout(self.v)

        if not self._yetki_kontrol():
            return

        ist = self.services["istatistik"].genel_istatistikler()

        # ── Stat row ──
        stat_row = QHBoxLayout()
        stat_row.setSpacing(14)
        for bas, deg, em, rk in [
            ("Kullanıcı",  str(ist["toplam_kullanici"]), "👥", "#6366f1,#8b5cf6"),
            ("Eğitmen",    str(ist["toplam_egitmen"]),    "🎓", "#10b981,#14b8a6"),
            ("Kurs",       str(ist["toplam_kurs"]),        "📚", "#3b82f6,#06b6d4"),
            ("Toplam Kayıt", str(ist["toplam_kayit"]),      "📝", "#ec4899,#f43f5e"),
        ]:
            stat_row.addWidget(StatCard(bas, deg, em, rk))
        self.v.addLayout(stat_row)

        # ── Grafik satırı ──
        graf_row = QHBoxLayout()
        graf_row.setSpacing(14)
        graf_row.addWidget(self._kategori_pasta(ist.get("kategori_dagilimi", {})), 1)
        graf_row.addWidget(self._seviye_bar(ist.get("seviye_dagilimi", {})), 1)
        self.v.addLayout(graf_row)

        # ── Alt satır: Popüler kurslar + Duyuru ──
        alt_row = QHBoxLayout()
        alt_row.setSpacing(14)
        alt_row.addWidget(self._populer_kurslar(ist.get("en_populer_kurslar", [])), 1)
        alt_row.addWidget(self._duyuru_karti(), 1)
        self.v.addLayout(alt_row)

        self.v.addStretch()

    # ───── PASTA ─────
    def _kategori_pasta(self, dag: dict) -> QFrame:
        kart = QFrame()
        kart.setProperty("card", True)
        v = QVBoxLayout(kart)
        v.setContentsMargins(16, 14, 16, 14)
        v.setSpacing(8)

        b = QLabel("📊  Kategori Dağılımı")
        b.setProperty("sectionTitle", True)
        v.addWidget(b)

        if not dag:
            l = QLabel("Henüz kurs verisi yok.")
            l.setProperty("muted", True)
            l.setAlignment(Qt.AlignCenter)
            l.setMinimumHeight(220)
            v.addWidget(l)
            return kart

        seri = QPieSeries()
        seri.setHoleSize(0.55)
        for i, (kat, sayi) in enumerate(dag.items()):
            slice_ = seri.append(f"{kat} ({sayi})", sayi)
            slice_.setBrush(QColor(self.PASTA_RENKLERI[i % len(self.PASTA_RENKLERI)]))
            slice_.setLabelVisible(False)
            slice_.setBorderColor(QColor("#1a1d27"))
            slice_.setBorderWidth(2)

        chart = QChart()
        chart.addSeries(seri)
        chart.setBackgroundBrush(QBrush(Qt.transparent))
        chart.setBackgroundVisible(False)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        chart.legend().setLabelColor(QColor("#9aa0ad"))
        chart.legend().setFont(QFont("Inter", 10))

        view = QChartView(chart)
        view.setRenderHint(QPainter.Antialiasing)
        view.setMinimumHeight(260)
        view.setStyleSheet("background: transparent;")
        v.addWidget(view)
        return kart

    # ───── BAR ─────
    def _seviye_bar(self, dag: dict) -> QFrame:
        kart = QFrame()
        kart.setProperty("card", True)
        v = QVBoxLayout(kart)
        v.setContentsMargins(16, 14, 16, 14)
        v.setSpacing(8)

        b = QLabel("📈  Seviye Dağılımı")
        b.setProperty("sectionTitle", True)
        v.addWidget(b)

        if not dag:
            l = QLabel("Veri yok.")
            l.setProperty("muted", True)
            l.setAlignment(Qt.AlignCenter)
            l.setMinimumHeight(220)
            v.addWidget(l)
            return kart

        kategoriler = ["Başlangıç", "Orta", "İleri"]
        bset = QBarSet("Kurs sayısı")
        bset.setColor(QColor("#6366f1"))
        bset.setBorderColor(QColor("#6366f1"))
        for k in kategoriler:
            bset.append(dag.get(k, 0))

        seri = QBarSeries()
        seri.append(bset)
        seri.setBarWidth(0.55)

        chart = QChart()
        chart.addSeries(seri)
        chart.setBackgroundBrush(QBrush(Qt.transparent))
        chart.setBackgroundVisible(False)
        chart.legend().setVisible(False)

        eks_x = QBarCategoryAxis()
        eks_x.append(kategoriler)
        eks_x.setLabelsColor(QColor("#9aa0ad"))
        eks_x.setGridLineVisible(False)
        chart.addAxis(eks_x, Qt.AlignBottom)
        seri.attachAxis(eks_x)

        eks_y = QValueAxis()
        eks_y.setLabelsColor(QColor("#9aa0ad"))
        eks_y.setGridLineColor(QColor(255, 255, 255, 25))
        max_d = max(dag.values()) if dag else 1
        eks_y.setRange(0, max(max_d + 1, 5))
        eks_y.setTickCount(min(6, max(2, max_d + 2)))
        eks_y.setLabelFormat("%d")
        chart.addAxis(eks_y, Qt.AlignLeft)
        seri.attachAxis(eks_y)

        view = QChartView(chart)
        view.setRenderHint(QPainter.Antialiasing)
        view.setMinimumHeight(260)
        view.setStyleSheet("background: transparent;")
        v.addWidget(view)
        return kart

    # ───── POPÜLER ─────
    def _populer_kurslar(self, kurslar: list) -> QFrame:
        kart = QFrame()
        kart.setProperty("card", True)
        v = QVBoxLayout(kart)
        v.setContentsMargins(16, 14, 16, 14)
        v.setSpacing(8)
        b = QLabel("🔥  En Popüler Kurslar")
        b.setProperty("sectionTitle", True)
        v.addWidget(b)
        if not kurslar:
            l = QLabel("Veri yok.")
            l.setProperty("muted", True)
            v.addWidget(l)
            return kart
        for i, k in enumerate(kurslar, 1):
            r = QHBoxLayout()
            r.setSpacing(10)
            sira = QLabel(f"#{i}")
            sira.setFixedWidth(28)
            sira.setStyleSheet("font-weight: 800; color: #6366f1; background: transparent;")
            r.addWidget(sira)
            ad = QLabel(k.get("ad", "?"))
            ad.setStyleSheet("font-weight: 600; background: transparent;")
            r.addWidget(ad, 1)
            sayi = QLabel(f"👥 {k.get('c', 0)}")
            sayi.setProperty("muted", True)
            r.addWidget(sayi)
            v.addLayout(r)
        v.addStretch()
        return kart

    # ───── DUYURU ─────
    def _duyuru_karti(self) -> QFrame:
        kart = QFrame()
        kart.setProperty("card", True)
        v = QVBoxLayout(kart)
        v.setContentsMargins(16, 14, 16, 14)
        v.setSpacing(8)

        b = QLabel("📢  Toplu Duyuru Gönder")
        b.setProperty("sectionTitle", True)
        v.addWidget(b)

        eti1 = QLabel("Hedef Kitle")
        eti1.setStyleSheet("font-size: 12px; font-weight: 600; background: transparent;")
        v.addWidget(eti1)
        self._duy_rol = QComboBox()
        self._duy_rol.addItems(["Tüm Kullanıcılar", "Sadece Öğrenciler",
                                 "Sadece Eğitmenler", "Sadece Adminler"])
        v.addWidget(self._duy_rol)

        eti2 = QLabel("Başlık")
        eti2.setStyleSheet("font-size: 12px; font-weight: 600; background: transparent;")
        v.addWidget(eti2)
        self._duy_baslik = QLineEdit()
        self._duy_baslik.setPlaceholderText("Önemli duyuru başlığı")
        v.addWidget(self._duy_baslik)

        eti3 = QLabel("Mesaj")
        eti3.setStyleSheet("font-size: 12px; font-weight: 600; background: transparent;")
        v.addWidget(eti3)
        self._duy_mesaj = QTextEdit()
        self._duy_mesaj.setPlaceholderText("Duyuru içeriği...")
        self._duy_mesaj.setMaximumHeight(80)
        v.addWidget(self._duy_mesaj)

        gnd = QPushButton("📣  Duyuru Gönder")
        gnd.setProperty("primary", True)
        gnd.setMinimumHeight(40)
        gnd.setCursor(Qt.PointingHandCursor)
        gnd.clicked.connect(self._duyuru_gonder)
        v.addWidget(gnd)

        v.addStretch()
        return kart

    def _duyuru_gonder(self):
        b = self._duy_baslik.text().strip()
        m = self._duy_mesaj.toPlainText().strip()
        if not b or not m:
            ToastYoneticisi.goster(self.mw, "Başlık ve mesaj gerekli.", "uyari")
            return
        rol_map = {
            "Tüm Kullanıcılar": None,
            "Sadece Öğrenciler": "ogrenci",
            "Sadece Eğitmenler": "egitmen",
            "Sadece Adminler":   "admin",
        }
        rol = rol_map.get(self._duy_rol.currentText())
        sonuc = self.services["bildirim"].toplu_gonder(b, m, "bilgi", rol=rol)
        self.services["logger"].info("admin",
            f"Toplu duyuru → {sonuc.get('gonderilen', 0)} kişi",
            kullanici_id=self.kullanici["id"])
        ToastYoneticisi.goster(self.mw,
            f"✅ {sonuc.get('gonderilen', 0)} kişiye duyuru gönderildi.", "basari")
        self._duy_baslik.clear()
        self._duy_mesaj.clear()
        self.mw.bildirim_sayisini_guncelle()


# ═════════════════════════════════════════════════════════════════════════
#  KULLANICI YÖNETİMİ
# ═════════════════════════════════════════════════════════════════════════
class AdminUsersView(QWidget):
    def __init__(self, vt, kullanici, services, main_window):
        super().__init__()
        self.vt = vt
        self.kullanici = kullanici
        self.services = services
        self.mw = main_window
        self._rol_filt = None

        v = QVBoxLayout(self)
        v.setContentsMargins(28, 22, 28, 22)
        v.setSpacing(14)

        # Başlık + filtre
        ust = QHBoxLayout()
        ust.setSpacing(10)
        bas = QLabel("👥  Kullanıcı Yönetimi")
        bas.setProperty("pageTitle", True)
        ust.addWidget(bas)
        ust.addStretch()
        ust.addWidget(QLabel("Rol filtresi:"))
        self.rol_combo = QComboBox()
        self.rol_combo.addItems(["Tümü", "admin", "egitmen", "ogrenci"])
        self.rol_combo.setMinimumWidth(160)
        self.rol_combo.currentTextChanged.connect(self._rol_degisti)
        ust.addWidget(self.rol_combo)
        v.addLayout(ust)

        self.bilgi = QLabel("")
        self.bilgi.setProperty("muted", True)
        v.addWidget(self.bilgi)

        # Tablo
        self.tablo = QTableWidget()
        self.tablo.setColumnCount(7)
        self.tablo.setHorizontalHeaderLabels(
            ["#", "Ad Soyad", "Kullanıcı Adı", "E-posta",
             "Rol", "Durum", "İşlem"])
        self.tablo.verticalHeader().setVisible(False)
        self.tablo.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tablo.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tablo.setShowGrid(False)
        self.tablo.setAlternatingRowColors(True)
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tablo.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.tablo.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tablo.setMinimumHeight(420)
        v.addWidget(self.tablo, 1)

    def _rol_degisti(self, t: str):
        self._rol_filt = None if t == "Tümü" else t
        self.yenile()

    def yenile(self, **_):
        if self.kullanici.get("rol") != "admin":
            self.bilgi.setText("⛔ Yetkisiz erişim")
            self.tablo.setRowCount(0)
            return

        kullanicilar = self.services["kul"].listele(self._rol_filt)
        self.bilgi.setText(f"Toplam {len(kullanicilar)} kullanıcı")
        self.tablo.setRowCount(len(kullanicilar))
        ROL_RENK = {"admin": "chipDanger", "egitmen": "chipBrand", "ogrenci": "chipInfo"}
        ROL_EMOJI = {"admin": "🛡️", "egitmen": "🎓", "ogrenci": "📖"}

        for i, k in enumerate(kullanicilar):
            self.tablo.setItem(i, 0, QTableWidgetItem(str(k["id"])))
            self.tablo.setItem(i, 1, QTableWidgetItem(f"{k.get('ad','')} {k.get('soyad','')}"))
            self.tablo.setItem(i, 2, QTableWidgetItem(k.get("kullanici_adi", "")))
            self.tablo.setItem(i, 3, QTableWidgetItem(k.get("eposta", "")))

            rol_lbl = QLabel(f"{ROL_EMOJI.get(k['rol'], '')} {k['rol']}")
            rol_lbl.setProperty("chip", True)
            rol_lbl.setProperty(ROL_RENK.get(k["rol"], "chipInfo"), True)
            rol_lbl.setAlignment(Qt.AlignCenter)
            rol_lbl.setStyleSheet("padding: 4px 8px;")
            self.tablo.setCellWidget(i, 4, rol_lbl)

            durum = QLabel("Aktif" if k.get("aktif") else "Pasif")
            durum.setProperty("chip", True)
            durum.setProperty("chipSuccess" if k.get("aktif") else "chipDanger", True)
            durum.setAlignment(Qt.AlignCenter)
            self.tablo.setCellWidget(i, 5, durum)

            # İşlem butonu hücresi
            buton_w = QWidget()
            bh = QHBoxLayout(buton_w)
            bh.setContentsMargins(4, 4, 4, 4)
            bh.setSpacing(6)
            tg = QPushButton("Askıya Al" if k.get("aktif") else "Aktif Et")
            tg.setProperty("actionBtn", True)
            tg.setCursor(Qt.PointingHandCursor)
            tg.clicked.connect(lambda _, kid=k["id"], a=k.get("aktif"): self._toggle_aktif(kid, a))
            bh.addWidget(tg)
            sl = QPushButton("Sil")
            sl.setProperty("actionBtn", True)
            sl.setProperty("danger", True)
            sl.setCursor(Qt.PointingHandCursor)
            sl.clicked.connect(lambda _, kid=k["id"]: self._sil(kid))
            bh.addWidget(sl)
            self.tablo.setCellWidget(i, 6, buton_w)

    def _toggle_aktif(self, kid, mevcut):
        if kid == self.kullanici["id"]:
            ToastYoneticisi.goster(self.mw, "Kendi hesabınızı değiştiremezsiniz.", "uyari")
            return
        self.services["kul"].guncelle(kid, aktif=0 if mevcut else 1)
        self.services["logger"].info("admin",
            f"Kullanıcı durum değişti: ID={kid}",
            kullanici_id=self.kullanici["id"])
        ToastYoneticisi.goster(self.mw, "Durum güncellendi.", "basari")
        self.yenile()

    def _sil(self, kid):
        if kid == self.kullanici["id"]:
            ToastYoneticisi.goster(self.mw, "Kendi hesabınızı silemezsiniz!", "hata")
            return
        m = QMessageBox(self)
        m.setWindowTitle("Kullanıcı Sil")
        m.setText("Bu kullanıcıyı kalıcı olarak silmek istediğinize emin misiniz?")
        m.setIcon(QMessageBox.Warning)
        evet = m.addButton("Sil", QMessageBox.YesRole)
        m.addButton("Vazgeç", QMessageBox.NoRole)
        m.exec_()
        if m.clickedButton() != evet:
            return
        self.services["kul"].sil(kid)
        self.services["logger"].uyari("admin", f"Kullanıcı silindi: ID={kid}",
            kullanici_id=self.kullanici["id"])
        ToastYoneticisi.goster(self.mw, "Kullanıcı silindi.", "basari")
        self.yenile()


# ═════════════════════════════════════════════════════════════════════════
#  EĞİTMEN YÖNETİMİ
# ═════════════════════════════════════════════════════════════════════════
class AdminInstructorsView(QWidget):
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

        self.ic = QFrame()
        self.ic.setObjectName("RootBg")
        scroll.setWidget(self.ic)
        self.v = QVBoxLayout(self.ic)
        self.v.setContentsMargins(28, 22, 28, 28)
        self.v.setSpacing(14)

    def yenile(self, **_):
        temizle_layout(self.v)

        if self.kullanici.get("rol") != "admin":
            l = QLabel("⛔ Yetkisiz")
            l.setProperty("muted", True)
            self.v.addWidget(l)
            return

        bas = QLabel("🎓  Eğitmen Yönetimi")
        bas.setProperty("pageTitle", True)
        self.v.addWidget(bas)

        # Ekle formu
        self.v.addWidget(self._ekle_formu())

        # Eğitmen kartları
        egitmenler = self.services["egitmen"].listele()
        if not egitmenler:
            l = QLabel("Henüz eğitmen yok.")
            l.setProperty("muted", True)
            l.setAlignment(Qt.AlignCenter)
            l.setMinimumHeight(120)
            self.v.addWidget(l)
        else:
            grid = QGridLayout()
            grid.setSpacing(14)
            for i, eg in enumerate(egitmenler):
                grid.addWidget(self._egitmen_karti(eg), i // 3, i % 3)
            holder = QWidget()
            holder.setLayout(grid)
            self.v.addWidget(holder)

        self.v.addStretch()

    def _ekle_formu(self) -> QFrame:
        kart = QFrame()
        kart.setProperty("card", True)
        v = QVBoxLayout(kart)
        v.setContentsMargins(18, 16, 18, 16)
        v.setSpacing(10)

        b = QLabel("➕  Yeni Eğitmen Ekle")
        b.setProperty("sectionTitle", True)
        v.addWidget(b)

        r1 = QHBoxLayout()
        r1.setSpacing(10)
        self._ad = QLineEdit(); self._ad.setPlaceholderText("Ad")
        self._soyad = QLineEdit(); self._soyad.setPlaceholderText("Soyad")
        self._eposta = QLineEdit(); self._eposta.setPlaceholderText("E-posta")
        self._uzm = QLineEdit(); self._uzm.setPlaceholderText("Uzmanlık")
        for w in (self._ad, self._soyad, self._eposta, self._uzm):
            r1.addWidget(w)
        v.addLayout(r1)

        ekle = QPushButton("Eğitmen Ekle")
        ekle.setProperty("primary", True)
        ekle.setCursor(Qt.PointingHandCursor)
        ekle.clicked.connect(self._ekle)
        v.addWidget(ekle, 0, Qt.AlignRight)

        return kart

    def _ekle(self):
        ad = self._ad.text().strip()
        sy = self._soyad.text().strip()
        ep = self._eposta.text().strip()
        uz = self._uzm.text().strip() or "Genel"
        if not (ad and sy and ep):
            ToastYoneticisi.goster(self.mw, "Ad, soyad, e-posta gerekli.", "uyari")
            return
        sonuc = self.services["egitmen"].ekle(ad, sy, ep, uz)
        if sonuc["basarili"]:
            ToastYoneticisi.goster(self.mw, "Eğitmen eklendi.", "basari")
            self._ad.clear(); self._soyad.clear(); self._eposta.clear(); self._uzm.clear()
            self.yenile()
        else:
            ToastYoneticisi.goster(self.mw, sonuc.get("mesaj", "Hata"), "hata")

    def _egitmen_karti(self, eg: dict) -> QFrame:
        kart = QFrame()
        kart.setProperty("card", True)
        v = QVBoxLayout(kart)
        v.setContentsMargins(16, 14, 16, 14)
        v.setSpacing(8)

        h = QHBoxLayout()
        h.setSpacing(12)
        # Avatar (sabit yeşil)
        renkler = ["#10b981", "#06b6d4", "#8b5cf6", "#f59e0b", "#ec4899"]
        renk = renkler[eg["id"] % len(renkler)]
        h.addWidget(Avatar(eg["ad"], eg["soyad"], renk, 48))

        vv = QVBoxLayout()
        vv.setSpacing(2)
        ad = QLabel(f"{eg['ad']} {eg['soyad']}")
        ad.setStyleSheet("font-size: 14px; font-weight: 700; background: transparent;")
        vv.addWidget(ad)
        ep = QLabel(eg.get("eposta", ""))
        ep.setProperty("muted", True)
        ep.setStyleSheet("font-size: 11px; background: transparent;")
        vv.addWidget(ep)
        h.addLayout(vv, 1)
        v.addLayout(h)

        if eg.get("uzmanlik"):
            uz = QLabel(f"📌 {eg['uzmanlik']}")
            uz.setProperty("chip", True)
            uz.setProperty("chipBrand", True)
            uz.setAlignment(Qt.AlignCenter)
            v.addWidget(uz, 0, Qt.AlignLeft)

        # Kurs sayısı
        c = self.vt.baglanti.cursor()
        c.execute("SELECT COUNT(*) FROM kurslar WHERE egitmen_id = ?", (eg["id"],))
        ks = c.fetchone()[0]
        s = QLabel(f"📚 {ks} kurs")
        s.setProperty("muted", True)
        v.addWidget(s)

        sil = QPushButton("Sil")
        sil.setProperty("danger", True)
        sil.setCursor(Qt.PointingHandCursor)
        sil.clicked.connect(lambda: self._sil(eg["id"]))
        v.addWidget(sil)

        return kart

    def _sil(self, eid):
        m = QMessageBox(self)
        m.setWindowTitle("Eğitmen Sil")
        m.setText("Eğitmeni silmek istiyor musunuz? (İlgili kurslar da silinir!)")
        m.setIcon(QMessageBox.Warning)
        evet = m.addButton("Sil", QMessageBox.YesRole)
        m.addButton("Vazgeç", QMessageBox.NoRole)
        m.exec_()
        if m.clickedButton() != evet:
            return
        self.services["egitmen"].sil(eid)
        ToastYoneticisi.goster(self.mw, "Eğitmen silindi.", "basari")
        self.yenile()


# ═════════════════════════════════════════════════════════════════════════
#  SİSTEM LOGLARI
# ═════════════════════════════════════════════════════════════════════════
class AdminLogsView(QWidget):
    def __init__(self, vt, kullanici, services, main_window):
        super().__init__()
        self.vt = vt
        self.kullanici = kullanici
        self.services = services
        self.mw = main_window
        self._sev_filt = None

        v = QVBoxLayout(self)
        v.setContentsMargins(28, 22, 28, 22)
        v.setSpacing(14)

        ust = QHBoxLayout()
        bas = QLabel("📋  Sistem Logları")
        bas.setProperty("pageTitle", True)
        ust.addWidget(bas)
        ust.addStretch()
        ust.addWidget(QLabel("Seviye:"))
        self.sev_combo = QComboBox()
        self.sev_combo.addItems(["Tümü", "INFO", "UYARI", "HATA"])
        self.sev_combo.setMinimumWidth(140)
        self.sev_combo.currentTextChanged.connect(self._filt_degisti)
        ust.addWidget(self.sev_combo)
        v.addLayout(ust)

        self.bilgi = QLabel("")
        self.bilgi.setProperty("muted", True)
        v.addWidget(self.bilgi)

        self.tablo = QTableWidget()
        self.tablo.setColumnCount(5)
        self.tablo.setHorizontalHeaderLabels(["Tarih", "Seviye", "Kaynak", "Mesaj", "Kullanıcı"])
        self.tablo.verticalHeader().setVisible(False)
        self.tablo.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tablo.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tablo.setShowGrid(False)
        self.tablo.setAlternatingRowColors(True)
        self.tablo.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.tablo.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        v.addWidget(self.tablo, 1)

    def _filt_degisti(self, t: str):
        self._sev_filt = None if t == "Tümü" else t
        self.yenile()

    def yenile(self, **_):
        if self.kullanici.get("rol") != "admin":
            self.bilgi.setText("⛔ Yetkisiz")
            self.tablo.setRowCount(0)
            return

        loglar = self.services["logger"].son_loglar(200, self._sev_filt)
        self.bilgi.setText(f"Son {len(loglar)} log gösteriliyor")
        self.tablo.setRowCount(len(loglar))
        SEV_RENK = {"INFO": "chipInfo", "UYARI": "chipWarning", "HATA": "chipDanger"}

        for i, l in enumerate(loglar):
            self.tablo.setItem(i, 0, QTableWidgetItem((l.get("tarih") or "")[:19]))

            sev = QLabel(l.get("seviye", ""))
            sev.setProperty("chip", True)
            sev.setProperty(SEV_RENK.get(l.get("seviye"), "chipInfo"), True)
            sev.setAlignment(Qt.AlignCenter)
            self.tablo.setCellWidget(i, 1, sev)

            self.tablo.setItem(i, 2, QTableWidgetItem(l.get("kaynak", "")))
            self.tablo.setItem(i, 3, QTableWidgetItem(l.get("mesaj", "")))
            self.tablo.setItem(i, 4, QTableWidgetItem(
                str(l.get("kullanici_id", "")) if l.get("kullanici_id") else "—"))


# ═════════════════════════════════════════════════════════════════════════
#  KURS YÖNETİMİ — Admin tüm kursları görür, düzenler, siler
# ═════════════════════════════════════════════════════════════════════════
class AdminCoursesView(QWidget):
    def __init__(self, vt, kullanici, services, main_window):
        super().__init__()
        self.vt = vt
        self.kullanici = kullanici
        self.services = services
        self.mw = main_window
        self._kat_filt = None
        self._sev_filt = None
        self._arama = ""

        v = QVBoxLayout(self)
        v.setContentsMargins(28, 22, 28, 22)
        v.setSpacing(14)

        ust = QHBoxLayout()
        bas = QLabel("📚  Kurs Yönetimi")
        bas.setProperty("pageTitle", True)
        ust.addWidget(bas)
        ust.addStretch()
        ust.addWidget(QLabel("Kategori:"))
        self.kat_combo = QComboBox()
        self.kat_combo.addItems(["Tümü", "Programlama", "Web Geliştirme",
                                  "Veri Bilimi", "Tasarım", "Genel"])
        self.kat_combo.currentTextChanged.connect(self._kat_degisti)
        ust.addWidget(self.kat_combo)
        ust.addWidget(QLabel("Seviye:"))
        self.sev_combo = QComboBox()
        self.sev_combo.addItems(["Tümü", "Başlangıç", "Orta", "İleri"])
        self.sev_combo.currentTextChanged.connect(self._sev_degisti)
        ust.addWidget(self.sev_combo)
        v.addLayout(ust)

        # Arama
        self.arama_input = QLineEdit()
        self.arama_input.setPlaceholderText("🔍 Kurs adında ara...")
        self.arama_input.textChanged.connect(self._arama_degisti)
        v.addWidget(self.arama_input)

        self.bilgi = QLabel("")
        self.bilgi.setProperty("muted", True)
        v.addWidget(self.bilgi)

        self.tablo = QTableWidget()
        self.tablo.setColumnCount(8)
        self.tablo.setHorizontalHeaderLabels(
            ["#", "Kurs Adı", "Eğitmen", "Kategori", "Seviye",
             "Kayıt", "Durum", "İşlem"])
        self.tablo.verticalHeader().setVisible(False)
        self.tablo.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tablo.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tablo.setShowGrid(False)
        self.tablo.setAlternatingRowColors(True)
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tablo.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeToContents)
        self.tablo.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        v.addWidget(self.tablo, 1)

    def _kat_degisti(self, t):
        self._kat_filt = None if t == "Tümü" else t
        self.yenile()

    def _sev_degisti(self, t):
        self._sev_filt = None if t == "Tümü" else t
        self.yenile()

    def _arama_degisti(self, t):
        self._arama = t.strip() or None
        self.yenile()

    def yenile(self, **_):
        if self.kullanici.get("rol") != "admin":
            self.bilgi.setText("⛔ Yetkisiz erişim")
            self.tablo.setRowCount(0)
            return

        kurslar = self.services["kurs"].listele(
            kategori=self._kat_filt,
            seviye=self._sev_filt,
            arama=self._arama,
            yayinda=False,
        )
        self.bilgi.setText(f"Toplam {len(kurslar)} kurs")
        self.tablo.setRowCount(len(kurslar))

        for i, k in enumerate(kurslar):
            self.tablo.setItem(i, 0, QTableWidgetItem(str(k["id"])))
            self.tablo.setItem(i, 1, QTableWidgetItem(k.get("ad", "")))
            self.tablo.setItem(i, 2, QTableWidgetItem(
                f"{k.get('egitmen_ad', '')} {k.get('egitmen_soyad', '')}"))

            kat = QLabel(k.get("kategori", "Genel"))
            kat.setProperty("chip", True)
            kat.setProperty("chipBrand", True)
            kat.setAlignment(Qt.AlignCenter)
            self.tablo.setCellWidget(i, 3, kat)

            sev = QLabel(k.get("seviye", "?"))
            sev.setProperty("chip", True)
            sev.setProperty("chipInfo", True)
            sev.setAlignment(Qt.AlignCenter)
            self.tablo.setCellWidget(i, 4, sev)

            self.tablo.setItem(i, 5, QTableWidgetItem(
                f"{k.get('kayit_sayisi', 0)}/{k.get('kontenjan', 0)}"))

            durum = QLabel("Yayında" if k.get("yayinda") else "Taslak")
            durum.setProperty("chip", True)
            durum.setProperty("chipSuccess" if k.get("yayinda") else "chipWarning", True)
            durum.setAlignment(Qt.AlignCenter)
            self.tablo.setCellWidget(i, 6, durum)

            # İşlem butonları
            cell = QWidget()
            ch = QHBoxLayout(cell)
            ch.setContentsMargins(4, 4, 4, 4)
            ch.setSpacing(6)
            duz = QPushButton("✏️")
            duz.setProperty("actionBtn", True)
            duz.setToolTip("Düzenle")
            duz.setCursor(Qt.PointingHandCursor)
            duz.setFixedWidth(36)
            duz.clicked.connect(lambda _, kk=k: self._duzenle(kk))
            ch.addWidget(duz)
            sl = QPushButton("🗑")
            sl.setProperty("actionBtn", True)
            sl.setProperty("danger", True)
            sl.setToolTip("Sil")
            sl.setCursor(Qt.PointingHandCursor)
            sl.setFixedWidth(36)
            sl.clicked.connect(lambda _, kid=k["id"], ad=k["ad"]: self._sil(kid, ad))
            ch.addWidget(sl)
            self.tablo.setCellWidget(i, 7, cell)

    def _duzenle(self, kurs):
        from widgets.kurs_dialog import KursDialog
        d = KursDialog(kurs, parent=self.mw)
        if d.exec_() != d.Accepted:
            return
        vals = d.degerler()
        sonuc = self.services["kurs"].guncelle(kurs["id"], **vals)
        if sonuc.get("basarili"):
            self.services["logger"].info("admin",
                f"Kurs düzenlendi: {vals['ad']}",
                kullanici_id=self.kullanici["id"])
            ToastYoneticisi.goster(self.mw, "✅ Kurs güncellendi.", "basari")
            self.yenile()

    def _sil(self, kid, ad):
        m = QMessageBox(self.mw)
        m.setWindowTitle("Kursu Sil")
        m.setText(f"\"{ad}\" kursunu silmek istiyor musunuz?\n"
                  "Tüm kayıtlar ve yorumlar da silinir!")
        m.setIcon(QMessageBox.Warning)
        evet = m.addButton("Sil", QMessageBox.YesRole)
        m.addButton("Vazgeç", QMessageBox.NoRole)
        m.exec_()
        if m.clickedButton() != evet:
            return
        self.services["kurs"].sil(kid)
        self.services["logger"].uyari("admin",
            f"Kurs silindi: {ad} (ID={kid})",
            kullanici_id=self.kullanici["id"])
        ToastYoneticisi.goster(self.mw, "🗑 Kurs silindi.", "basari")
        self.yenile()


# ═════════════════════════════════════════════════════════════════════════
#  YORUM MODERASYONU
# ═════════════════════════════════════════════════════════════════════════
class AdminCommentsView(QWidget):
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

        self.ic = QFrame()
        self.ic.setObjectName("RootBg")
        scroll.setWidget(self.ic)
        self.v = QVBoxLayout(self.ic)
        self.v.setContentsMargins(28, 22, 28, 28)
        self.v.setSpacing(14)

    def yenile(self, **_):
        temizle_layout(self.v)

        if self.kullanici.get("rol") != "admin":
            l = QLabel("⛔ Yetkisiz erişim")
            l.setProperty("muted", True)
            l.setAlignment(Qt.AlignCenter)
            l.setMinimumHeight(180)
            self.v.addWidget(l)
            return

        bas = QLabel("💬  Yorum Moderasyonu")
        bas.setProperty("pageTitle", True)
        self.v.addWidget(bas)

        yorumlar = self.services["yorum"].tum_yorumlar(limit=300)
        bilgi = QLabel(f"Son {len(yorumlar)} yorum gösteriliyor — "
                       "uygunsuz olanları silebilirsiniz.")
        bilgi.setProperty("muted", True)
        self.v.addWidget(bilgi)

        if not yorumlar:
            bos = QLabel("💬 Henüz hiç yorum yok.")
            bos.setProperty("muted", True)
            bos.setAlignment(Qt.AlignCenter)
            bos.setMinimumHeight(180)
            self.v.addWidget(bos)
            return

        for y in yorumlar:
            self.v.addWidget(self._yorum_karti(y))
        self.v.addStretch()

    def _yorum_karti(self, y: dict) -> QFrame:
        from widgets.modern import StarRating
        f = QFrame()
        f.setProperty("card", True)
        h = QHBoxLayout(f)
        h.setContentsMargins(16, 14, 16, 14)
        h.setSpacing(14)

        av = Avatar(y.get("kullanici_ad", "?"),
                    y.get("kullanici_soyad", ""),
                    y.get("avatar_renk") or "#6366f1", 40)
        h.addWidget(av, 0, Qt.AlignTop)

        v = QVBoxLayout()
        v.setSpacing(4)

        ust = QHBoxLayout()
        ust.setSpacing(8)
        ad = QLabel(f"{y.get('kullanici_ad','')} {y.get('kullanici_soyad','')}")
        ad.setStyleSheet("font-size: 13px; font-weight: 700; background: transparent;")
        ust.addWidget(ad)
        rt = StarRating(y.get("puan", 0), boyut=12, etkilesimli=False)
        ust.addWidget(rt)
        ust.addStretch()
        kurs_lbl = QLabel(f"📚 {y.get('kurs_ad', '')}")
        kurs_lbl.setProperty("chip", True)
        kurs_lbl.setProperty("chipBrand", True)
        ust.addWidget(kurs_lbl)
        tar = QLabel((y.get("tarih") or "")[:16])
        tar.setProperty("dim", True)
        ust.addWidget(tar)
        v.addLayout(ust)

        if y.get("mesaj"):
            m = QLabel(y["mesaj"])
            m.setProperty("muted", True)
            m.setWordWrap(True)
            v.addWidget(m)
        h.addLayout(v, 1)

        sil = QPushButton("🗑  Sil")
        sil.setProperty("actionBtn", True)
        sil.setProperty("danger", True)
        sil.setCursor(Qt.PointingHandCursor)
        sil.clicked.connect(lambda: self._sil(y["id"]))
        h.addWidget(sil, 0, Qt.AlignTop)
        return f

    def _sil(self, yid):
        m = QMessageBox(self.mw)
        m.setWindowTitle("Yorumu Sil")
        m.setText("Bu yorumu silmek istediğinize emin misiniz?")
        m.setIcon(QMessageBox.Question)
        evet = m.addButton("Sil", QMessageBox.YesRole)
        m.addButton("Vazgeç", QMessageBox.NoRole)
        m.exec_()
        if m.clickedButton() != evet:
            return
        self.services["yorum"].sil(yid)
        self.services["logger"].uyari("admin",
            f"Yorum moderasyonla silindi: ID={yid}",
            kullanici_id=self.kullanici["id"])
        ToastYoneticisi.goster(self.mw, "🗑 Yorum silindi.", "basari")
        self.yenile()
