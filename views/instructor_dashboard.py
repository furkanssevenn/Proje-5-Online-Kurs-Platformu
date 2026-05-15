"""
═══════════════════════════════════════════════════════════════════════════
  EĞİTMEN PANELİ — Tam yetkili kurs yönetimi
═══════════════════════════════════════════════════════════════════════════
  Sekmeler:
    • 📚 Kurslarım  — kurs ekle/düzenle/sil/yayınla
    • 👥 Öğrencilerim — kayıtlı öğrenci tablosu + ilerleme
    • 💬 Yorumlar    — kendi kurslarına yapılan yorumlar (silebilir)
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QScrollArea, QFrame, QPushButton, QProgressBar,
                             QTabWidget, QTableWidget, QTableWidgetItem,
                             QHeaderView, QAbstractItemView, QMessageBox)

from widgets.modern import (StatCard, Avatar, StarRating,
                            ToastYoneticisi, temizle_layout)
from widgets.kurs_dialog import KursDialog


# ═════════════════════════════════════════════════════════════════════════
#  EĞİTMENİN BİR KURS SATIRI — yönetim butonlarıyla
# ═════════════════════════════════════════════════════════════════════════
class _EgitmenKursSatiri(QFrame):
    def __init__(self, kurs: dict, parent_view, parent=None):
        super().__init__(parent)
        self.setProperty("card", True)
        self._kurs = kurs
        self._mw = parent_view.mw
        self._pv = parent_view

        h = QHBoxLayout(self)
        h.setContentsMargins(16, 14, 16, 14)
        h.setSpacing(16)

        # Sol mini ikon
        renkler = (kurs.get("kapak_renk") or "#6366f1,#8b5cf6").split(",")
        ic = QLabel("📘")
        ic.setFixedSize(56, 56)
        ic.setAlignment(Qt.AlignCenter)
        ic.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 {renkler[0].strip()},
                stop:1 {renkler[1].strip() if len(renkler)>1 else renkler[0]});
            border-radius: 12px; font-size: 26px;
        """)
        h.addWidget(ic, 0, Qt.AlignTop)

        # Orta: ad + chip'ler + dolu/kontenjan
        v = QVBoxLayout()
        v.setSpacing(6)
        ad = QLabel(kurs["ad"])
        ad.setStyleSheet("font-size: 15px; font-weight: 700; background: transparent;")
        v.addWidget(ad)

        meta_row = QHBoxLayout()
        meta_row.setSpacing(6)
        for txt, prop in [
            (kurs.get("kategori", "Genel"), "chipBrand"),
            (kurs.get("seviye", "Başlangıç"), "chipInfo"),
            ("Yayında" if kurs.get("yayinda") else "Taslak",
             "chipSuccess" if kurs.get("yayinda") else "chipWarning"),
        ]:
            l = QLabel(txt)
            l.setProperty("chip", True)
            l.setProperty(prop, True)
            meta_row.addWidget(l)
        ort = float(kurs.get("ort_puan") or 0)
        ys  = int(kurs.get("yorum_sayisi") or 0)
        if ys > 0:
            puan_lbl = QLabel(f"⭐ {ort:.1f} ({ys})")
            puan_lbl.setProperty("chip", True)
            puan_lbl.setProperty("chipWarning", True)
            meta_row.addWidget(puan_lbl)
        meta_row.addStretch()
        v.addLayout(meta_row)

        kayit = kurs.get("kayit_sayisi", 0)
        kon = kurs.get("kontenjan", 0) or 1
        pr_row = QHBoxLayout()
        pr_row.setSpacing(10)
        pb = QProgressBar()
        pb.setMaximum(kon)
        pb.setValue(kayit)
        pb.setTextVisible(False)
        pb.setFixedHeight(6)
        pr_row.addWidget(pb, 1)
        yz = QLabel(f"{kayit}/{kon}")
        yz.setStyleSheet("font-size: 11px; color: #9aa0ad; min-width: 50px; background: transparent;")
        pr_row.addWidget(yz)
        v.addLayout(pr_row)
        h.addLayout(v, 1)

        # Sağ: aksiyon butonları (dikey)
        sag = QVBoxLayout()
        sag.setSpacing(6)
        sag.setAlignment(Qt.AlignTop)

        ac_btn = QPushButton("👁  Görüntüle")
        ac_btn.setProperty("ghost", True)
        ac_btn.setCursor(Qt.PointingHandCursor)
        ac_btn.clicked.connect(self._goruntule)
        sag.addWidget(ac_btn)

        duz_btn = QPushButton("✏️  Düzenle")
        duz_btn.setProperty("actionBtn", True)
        duz_btn.setCursor(Qt.PointingHandCursor)
        duz_btn.clicked.connect(self._duzenle)
        sag.addWidget(duz_btn)

        yay_btn = QPushButton(
            "📥 Yayından Kaldır" if kurs.get("yayinda") else "🚀 Yayınla"
        )
        yay_btn.setProperty("actionBtn", True)
        yay_btn.setCursor(Qt.PointingHandCursor)
        yay_btn.clicked.connect(self._yayin_toggle)
        sag.addWidget(yay_btn)

        sil_btn = QPushButton("🗑  Sil")
        sil_btn.setProperty("actionBtn", True)
        sil_btn.setProperty("danger", True)
        sil_btn.setCursor(Qt.PointingHandCursor)
        sil_btn.clicked.connect(self._sil)
        sag.addWidget(sil_btn)

        h.addLayout(sag)

    # ─── Aksiyonlar ─────────────────────────────────────────────────
    def _goruntule(self):
        self._mw.sayfayaGec("kurs_detay", kurs_id=self._kurs["id"])

    def _duzenle(self):
        d = KursDialog(self._kurs, parent=self._mw)
        if d.exec_() != d.Accepted:
            return
        vals = d.degerler()
        sonuc = self._pv.services["kurs"].guncelle(self._kurs["id"], **vals)
        if sonuc.get("basarili"):
            self._pv.services["logger"].info("kurs",
                f"Kurs güncellendi: {vals['ad']}",
                kullanici_id=self._pv.kullanici["id"])
            ToastYoneticisi.goster(self._mw, "✅ Kurs güncellendi.", "basari")
            self._pv.yenile()
        else:
            ToastYoneticisi.goster(self._mw,
                sonuc.get("mesaj", "Güncelleme başarısız."), "hata")

    def _yayin_toggle(self):
        yeni = 0 if self._kurs.get("yayinda") else 1
        self._pv.services["kurs"].guncelle(self._kurs["id"], yayinda=yeni)
        self._pv.services["logger"].info("kurs",
            f"Kurs {'yayında' if yeni else 'taslakta'}: {self._kurs['ad']}",
            kullanici_id=self._pv.kullanici["id"])
        ToastYoneticisi.goster(self._mw,
            "🚀 Kurs yayında" if yeni else "📥 Kurs taslağa alındı", "basari")
        self._pv.yenile()

    def _sil(self):
        m = QMessageBox(self._mw)
        m.setWindowTitle("Kursu Sil")
        m.setText(f"\"{self._kurs['ad']}\" kursunu silmek istiyor musunuz?\n"
                  "Bu işlem geri alınamaz! Tüm kayıtlar ve yorumlar da silinir.")
        m.setIcon(QMessageBox.Warning)
        evet = m.addButton("Evet, sil", QMessageBox.YesRole)
        m.addButton("Vazgeç", QMessageBox.NoRole)
        m.exec_()
        if m.clickedButton() != evet:
            return
        self._pv.services["kurs"].sil(self._kurs["id"])
        self._pv.services["logger"].uyari("kurs",
            f"Kurs silindi: {self._kurs['ad']}",
            kullanici_id=self._pv.kullanici["id"])
        ToastYoneticisi.goster(self._mw, "🗑 Kurs silindi.", "basari")
        self._pv.yenile()


# ═════════════════════════════════════════════════════════════════════════
#  ANA EĞİTMEN PANELİ
# ═════════════════════════════════════════════════════════════════════════
class InstructorDashboard(QWidget):
    def __init__(self, vt, kullanici, services, main_window):
        super().__init__()
        self.vt = vt
        self.kullanici = kullanici
        self.services = services
        self.mw = main_window
        self._egitmen = None

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
        self.v.setSpacing(18)

    # ════════════════════════════════════════════════════════════════
    def yenile(self, **_):
        temizle_layout(self.v)

        if self.kullanici.get("rol") not in ("egitmen", "admin"):
            uy = QLabel("ℹ️ Bu panel eğitmenler içindir.")
            uy.setProperty("muted", True)
            uy.setAlignment(Qt.AlignCenter)
            uy.setMinimumHeight(180)
            self.v.addWidget(uy)
            return

        eg = self.services["egitmen"].kullanici_id_ile_bul(self.kullanici["id"])
        if not eg and self.kullanici.get("rol") == "admin":
            uy = QLabel("ℹ️ Admin hesabının eğitmen profili yok.\n"
                        "Eğitmen olarak kurs eklemek için eğitmen hesabıyla giriş yapın.")
            uy.setProperty("muted", True)
            uy.setAlignment(Qt.AlignCenter)
            uy.setMinimumHeight(180)
            self.v.addWidget(uy)
            return
        if not eg:
            return
        self._egitmen = eg

        # ─── Hero ───
        karsilama = QFrame()
        karsilama.setProperty("card", True)
        kh = QHBoxLayout(karsilama)
        kh.setContentsMargins(24, 18, 24, 18)
        kh.setSpacing(12)
        ic = QLabel("🎓")
        ic.setStyleSheet("font-size: 38px; background: transparent;")
        kh.addWidget(ic)
        karsv = QVBoxLayout()
        karsv.setSpacing(2)
        b1 = QLabel(f"Hoş geldin, {eg['ad']} {eg['soyad']}")
        b1.setProperty("pageTitle", True)
        karsv.addWidget(b1)
        b2 = QLabel(f"📌 Uzmanlık: {eg.get('uzmanlik') or 'Henüz belirtilmedi'}")
        b2.setProperty("muted", True)
        karsv.addWidget(b2)
        kh.addLayout(karsv, 1)

        yeni_btn = QPushButton("➕  Yeni Kurs Oluştur")
        yeni_btn.setProperty("primary", True)
        yeni_btn.setMinimumHeight(40)
        yeni_btn.setCursor(Qt.PointingHandCursor)
        yeni_btn.clicked.connect(self._yeni_kurs)
        kh.addWidget(yeni_btn)
        self.v.addWidget(karsilama)

        # ─── İstatistik kartları ───
        ist = self.services["istatistik"].egitmen_istatistikleri(eg["id"])
        stat_row = QHBoxLayout()
        stat_row.setSpacing(14)
        for bas, deg, em, rk in [
            ("Toplam Kurs",   str(ist["toplam_kurs"]),    "📚", "#6366f1,#8b5cf6"),
            ("Yayında",       str(ist["yayinda"]),         "🚀", "#10b981,#14b8a6"),
            ("Toplam Öğrenci", str(ist["toplam_ogrenci"]), "👥", "#3b82f6,#06b6d4"),
            ("Ort. Puan",     f"⭐ {ist['ortalama_puan']}", "⭐", "#f59e0b,#ef4444"),
        ]:
            stat_row.addWidget(StatCard(bas, deg, em, rk))
        self.v.addLayout(stat_row)

        # ─── Sekmeler ───
        sekme = QTabWidget()
        kurslar = self.services["kurs"].egitmen_kurslari(eg["id"])

        sekme.addTab(self._kurslar_sekmesi(kurslar),
                     f"📚  Kurslarım ({len(kurslar)})")

        sekme.addTab(self._ogrenciler_sekmesi(kurslar),
                     f"👥  Öğrencilerim ({ist['toplam_ogrenci']})")

        yorumlar = self.services["yorum"].egitmen_yorumlari(eg["id"])
        sekme.addTab(self._yorumlar_sekmesi(yorumlar),
                     f"💬  Yorumlar ({len(yorumlar)})")

        self.v.addWidget(sekme, 1)

    # ════════════════════════════════════════════════════════════════
    #  SEKME — KURSLARIM
    # ════════════════════════════════════════════════════════════════
    def _kurslar_sekmesi(self, kurslar) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(16, 16, 16, 16)
        v.setSpacing(10)

        if not kurslar:
            bos = QLabel("📭 Henüz hiç kursunuz yok.\n"
                         "Yukarıdan \"Yeni Kurs Oluştur\" butonuna tıklayın.")
            bos.setProperty("muted", True)
            bos.setAlignment(Qt.AlignCenter)
            bos.setMinimumHeight(180)
            v.addWidget(bos)
            return w

        for k in kurslar:
            v.addWidget(_EgitmenKursSatiri(k, self))
        v.addStretch()
        return w

    # ════════════════════════════════════════════════════════════════
    #  SEKME — ÖĞRENCİLERİM
    # ════════════════════════════════════════════════════════════════
    def _ogrenciler_sekmesi(self, kurslar) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(16, 16, 16, 16)
        v.setSpacing(10)

        satirlar = []
        for k in kurslar:
            kayitli = self.services["kurs"].kayitli_ogrenciler(k["id"])
            for o in kayitli:
                satirlar.append({**o, "kurs_ad": k["ad"]})

        if not satirlar:
            bos = QLabel("📭 Henüz hiç kayıtlı öğrenciniz yok.")
            bos.setProperty("muted", True)
            bos.setAlignment(Qt.AlignCenter)
            bos.setMinimumHeight(180)
            v.addWidget(bos)
            return w

        bilgi = QLabel(f"Toplam {len(satirlar)} kayıt")
        bilgi.setProperty("muted", True)
        v.addWidget(bilgi)

        tablo = QTableWidget()
        tablo.setColumnCount(5)
        tablo.setHorizontalHeaderLabels(
            ["Öğrenci", "E-posta", "Kurs", "İlerleme", "Kayıt Tarihi"])
        tablo.verticalHeader().setVisible(False)
        tablo.setEditTriggers(QAbstractItemView.NoEditTriggers)
        tablo.setSelectionBehavior(QAbstractItemView.SelectRows)
        tablo.setShowGrid(False)
        tablo.setAlternatingRowColors(True)
        tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tablo.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        tablo.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        tablo.setRowCount(len(satirlar))

        for i, s in enumerate(satirlar):
            tablo.setItem(i, 0, QTableWidgetItem(f"{s.get('ad','')} {s.get('soyad','')}"))
            tablo.setItem(i, 1, QTableWidgetItem(s.get("eposta", "—")))
            tablo.setItem(i, 2, QTableWidgetItem(s.get("kurs_ad", "—")))

            ilerleme = int(s.get("ilerleme", 0) or 0)
            cell_w = QWidget()
            ch = QHBoxLayout(cell_w)
            ch.setContentsMargins(4, 4, 4, 4)
            ch.setSpacing(8)
            pb = QProgressBar()
            pb.setMaximum(100)
            pb.setValue(ilerleme)
            pb.setTextVisible(False)
            pb.setFixedHeight(8)
            pb.setFixedWidth(100)
            ch.addWidget(pb)
            yz = QLabel(f"%{ilerleme}")
            yz.setStyleSheet("font-size: 11px; font-weight: 700; background: transparent;")
            ch.addWidget(yz)
            tablo.setCellWidget(i, 3, cell_w)

            tablo.setItem(i, 4, QTableWidgetItem((s.get("kayit_zamani") or "")[:16]))

        v.addWidget(tablo, 1)
        return w

    # ════════════════════════════════════════════════════════════════
    #  SEKME — YORUMLAR
    # ════════════════════════════════════════════════════════════════
    def _yorumlar_sekmesi(self, yorumlar) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(16, 16, 16, 16)
        v.setSpacing(10)

        if not yorumlar:
            bos = QLabel("💬 Henüz kurslarınıza yorum yapılmamış.")
            bos.setProperty("muted", True)
            bos.setAlignment(Qt.AlignCenter)
            bos.setMinimumHeight(180)
            v.addWidget(bos)
            return w

        for y in yorumlar:
            v.addWidget(self._yorum_karti(y))
        v.addStretch()
        return w

    def _yorum_karti(self, y: dict) -> QFrame:
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

        sil = QPushButton("🗑")
        sil.setProperty("actionBtn", True)
        sil.setProperty("danger", True)
        sil.setFixedWidth(40)
        sil.setToolTip("Yorumu sil")
        sil.setCursor(Qt.PointingHandCursor)
        sil.clicked.connect(lambda: self._yorum_sil(y["id"]))
        h.addWidget(sil, 0, Qt.AlignTop)
        return f

    def _yorum_sil(self, yid: int):
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
        self.services["logger"].uyari("yorum",
            f"Eğitmen yorumu sildi: ID={yid}",
            kullanici_id=self.kullanici["id"])
        ToastYoneticisi.goster(self.mw, "🗑 Yorum silindi.", "basari")
        self.yenile()

    # ════════════════════════════════════════════════════════════════
    #  YENİ KURS OLUŞTUR
    # ════════════════════════════════════════════════════════════════
    def _yeni_kurs(self):
        d = KursDialog(parent=self.mw)
        if d.exec_() != d.Accepted:
            return
        vals = d.degerler()
        sonuc = self.services["kurs"].ekle(
            vals["ad"], self._egitmen["id"],
            kontenjan=vals["kontenjan"],
            aciklama=vals["aciklama"],
            kategori=vals["kategori"],
            seviye=vals["seviye"],
            fiyat=vals["fiyat"],
            yayinda=vals["yayinda"],
        )
        if sonuc.get("basarili"):
            self.services["logger"].info("kurs",
                f"Yeni kurs oluşturuldu: {vals['ad']}",
                kullanici_id=self.kullanici["id"])
            ToastYoneticisi.goster(self.mw,
                "🎉 Kurs başarıyla oluşturuldu.", "basari")
            self.yenile()
        else:
            ToastYoneticisi.goster(self.mw,
                sonuc.get("mesaj", "Kurs eklenemedi."), "hata")
