"""
═══════════════════════════════════════════════════════════════════════════
  KURS DETAY — Kurs bilgisi + kayıt/favori + yorumlar + ilerleme
═══════════════════════════════════════════════════════════════════════════
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QScrollArea, QPushButton, QFrame,
                             QTextEdit, QLineEdit, QSizePolicy,
                             QProgressBar, QSpacerItem, QMessageBox)

from widgets.modern import (Avatar, GradientBanner, StarRating,
                            ToastYoneticisi, kart_olustur,
                            ProgressRing, SectionHeader)
from widgets.kurs_dialog import KursDialog


class CourseDetailView(QWidget):
    def __init__(self, vt, kullanici, services, main_window):
        super().__init__()
        self.vt = vt
        self.kullanici = kullanici
        self.services = services
        self.mw = main_window
        self.kurs = None
        self.kurs_id = None

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

    # ════════════════════════════════════════════════════════════════════
    def yenile(self, kurs_id: int = None, **_):
        if kurs_id is None:
            return
        self.kurs_id = kurs_id
        self.kurs = self.services["kurs"].getir(kurs_id)
        self._render()

    def _temizle(self, layout=None):
        if layout is None:
            layout = self.v
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                child_layout = item.layout()
                if child_layout is not None:
                    self._temizle(child_layout)
                    child_layout.deleteLater()

    def _render(self):
        self._temizle()
        if not self.kurs:
            l = QLabel("⚠ Kurs bulunamadı.")
            l.setProperty("muted", True)
            self.v.addWidget(l)
            return

        k = self.kurs

        # ── Geri butonu ──
        geri = QPushButton("← Tüm Kurslar")
        geri.setProperty("ghost", True)
        geri.setCursor(Qt.PointingHandCursor)
        geri.setMaximumWidth(180)
        geri.clicked.connect(lambda: self.mw.sayfayaGec("kurslar"))
        self.v.addWidget(geri)

        # ── Hero banner ──
        from views.home_view import HeroBanner
        banner = GradientBanner(
            k.get("kapak_renk") or "#6366f1,#8b5cf6",
            k["ad"],
            "📚",
            yukseklik=160
        )
        self.v.addWidget(banner)

        # ── İki kolon: sol içerik / sağ aksiyon kartı ──
        kolon = QHBoxLayout()
        kolon.setSpacing(18)
        self.v.addLayout(kolon, 1)

        # ────── SOL ──────
        sol = QVBoxLayout()
        sol.setSpacing(14)

        # Chip'ler
        chip_row = QHBoxLayout()
        chip_row.setSpacing(6)
        for metin, prop in [
            (k.get("kategori", "Genel"), "chipBrand"),
            (k.get("seviye", "Başlangıç"), "chipInfo"),
        ]:
            l = QLabel(metin)
            l.setProperty("chip", True)
            l.setProperty(prop, True)
            chip_row.addWidget(l)
        if (k.get("fiyat") or 0) <= 0:
            l = QLabel("ÜCRETSİZ")
            l.setProperty("chip", True)
            l.setProperty("chipSuccess", True)
            chip_row.addWidget(l)
        chip_row.addStretch()
        sol.addLayout(chip_row)

        # Başlık
        bas = QLabel(k["ad"])
        bas.setProperty("heroTitle", True)
        bas.setWordWrap(True)
        sol.addWidget(bas)

        # Yıldız + yorum sayısı
        rating_row = QHBoxLayout()
        rating_row.setSpacing(8)
        rt = StarRating(k.get("ort_puan") or 0, etkilesimli=False)
        rating_row.addWidget(rt)
        ort_p = float(k.get("ort_puan") or 0)
        puan_lbl = QLabel(f"{ort_p:.1f}")
        puan_lbl.setProperty("textStyle", "bold14")
        rating_row.addWidget(puan_lbl)
        ys = QLabel(f"({k.get('yorum_sayisi', 0)} yorum)")
        ys.setProperty("muted", True)
        rating_row.addWidget(ys)
        rating_row.addStretch()
        sol.addLayout(rating_row)

        # Açıklama
        ack = QLabel("Kurs Açıklaması")
        ack.setProperty("sectionTitle", True)
        sol.addWidget(ack)
        ac_lbl = QLabel(k.get("aciklama") or "Bu kurs için açıklama henüz girilmemiş.")
        ac_lbl.setProperty("muted", True)
        ac_lbl.setWordWrap(True)
        sol.addWidget(ac_lbl)

        # Eğitmen kartı
        sol.addWidget(self._egitmen_karti())

        # ── İlerleme (eğer kayıtlıysa) ──
        kayitli = self._kayitli_mi()
        if kayitli:
            sol.addWidget(self._ilerleme_karti(kayitli))

        # ── Yorumlar ──
        sol.addWidget(self._yorumlar_karti())

        sol.addStretch()
        kolon.addLayout(sol, 2)

        # ────── SAĞ ──────
        sag = QVBoxLayout()
        sag.setSpacing(14)
        sag.addWidget(self._aksiyon_karti(kayitli))
        sag.addStretch()
        kolon.addLayout(sag, 1)

    # ────── KARTLAR ─────────────────────────────────────────────────────
    def _egitmen_karti(self) -> QFrame:
        k = self.kurs
        kart = QFrame()
        kart.setProperty("card", True)
        h = QHBoxLayout(kart)
        h.setContentsMargins(16, 14, 16, 14)
        h.setSpacing(14)

        av = Avatar(k.get("egitmen_ad", "?"),
                    k.get("egitmen_soyad", ""),
                    "#10b981", 56)
        h.addWidget(av)

        v = QVBoxLayout()
        v.setSpacing(2)
        et = QLabel("EĞİTMEN")
        et.setStyleSheet("font-size: 10px; font-weight: 700; color: #6b7280; letter-spacing: 1px; background: transparent;")
        v.addWidget(et)
        ad = QLabel(f"{k.get('egitmen_ad', '')} {k.get('egitmen_soyad', '')}")
        ad.setProperty("textStyle", "bold16")
        v.addWidget(ad)
        if k.get("egitmen_uzmanlik"):
            uz = QLabel(f"📌 {k['egitmen_uzmanlik']}")
            uz.setProperty("muted", True)
            v.addWidget(uz)
        h.addLayout(v, 1)
        return kart

    def _aksiyon_karti(self, kayitli) -> QFrame:
        k = self.kurs
        kart = QFrame()
        kart.setProperty("card", True)
        v = QVBoxLayout(kart)
        v.setContentsMargins(20, 20, 20, 20)
        v.setSpacing(12)

        # Fiyat
        f = float(k.get("fiyat") or 0)
        if f > 0:
            fiy_lbl = QLabel(f"{f:,.0f} ₺".replace(",", "."))
            fiy_lbl.setProperty("textStyle", "bold32")
        else:
            fiy_lbl = QLabel("Ücretsiz")
            fiy_lbl.setStyleSheet("font-size: 28px; font-weight: 800; color: #10b981; background: transparent;")
        v.addWidget(fiy_lbl)

        # Ana buton
        if self.kullanici.get("rol") == "ogrenci":
            if kayitli:
                btn = QPushButton("✓ Kayıtlısınız")
                btn.setProperty("success", True)
                btn.setEnabled(False)
                btn.setMinimumHeight(46)
                v.addWidget(btn)

                cik = QPushButton("Kurstan Ayrıl")
                cik.setProperty("danger", True)
                cik.setMinimumHeight(40)
                cik.setCursor(Qt.PointingHandCursor)
                cik.clicked.connect(self._kurstan_cik)
                v.addWidget(cik)
            else:
                btn = QPushButton("🚀  Kursa Kaydol")
                btn.setProperty("primary", True)
                btn.setMinimumHeight(46)
                btn.setCursor(Qt.PointingHandCursor)
                btn.clicked.connect(self._kursa_kaydol)
                v.addWidget(btn)
        elif self._kursu_yonetebilir():
            # Eğitmen (sahibi) veya Admin için yönetim butonları
            yonet_lbl = QLabel(
                "🛠  Bu kursu yönetebilirsiniz" if self.kullanici.get("rol") == "egitmen"
                else "🛡  Admin olarak yönetiyorsunuz")
            yonet_lbl.setProperty("chip", True)
            yonet_lbl.setProperty("chipBrand", True)
            yonet_lbl.setAlignment(Qt.AlignCenter)
            v.addWidget(yonet_lbl)

            duz = QPushButton("✏️  Kursu Düzenle")
            duz.setProperty("primary", True)
            duz.setMinimumHeight(40)
            duz.setCursor(Qt.PointingHandCursor)
            duz.clicked.connect(self._kursu_duzenle)
            v.addWidget(duz)

            yay = QPushButton("📥 Yayından Kaldır" if k.get("yayinda") else "🚀 Yayınla")
            yay.setMinimumHeight(36)
            yay.setCursor(Qt.PointingHandCursor)
            yay.clicked.connect(self._yayin_toggle)
            v.addWidget(yay)

            sil = QPushButton("🗑  Kursu Sil")
            sil.setProperty("danger", True)
            sil.setMinimumHeight(36)
            sil.setCursor(Qt.PointingHandCursor)
            sil.clicked.connect(self._kursu_sil)
            v.addWidget(sil)
        else:
            inf = QLabel("⚠ Sadece öğrenciler kursa kayıt olabilir.")
            inf.setProperty("muted", True)
            inf.setWordWrap(True)
            v.addWidget(inf)

        # Favori (sadece öğrenciler için anlamlı)
        if self.kullanici.get("rol") == "ogrenci":
            fav_mi = self.services["favori"].favori_mi(self.kurs_id, self.kullanici["id"])
            fav_btn = QPushButton(("💖  Favoriden Çıkar" if fav_mi else "🤍  Favorilere Ekle"))
            fav_btn.setMinimumHeight(40)
            fav_btn.setCursor(Qt.PointingHandCursor)
            fav_btn.clicked.connect(lambda: self._favori_toggle(fav_btn))
            v.addWidget(fav_btn)

        # Ayrac
        sep = QFrame()
        sep.setProperty("separator", True)
        sep.setFixedHeight(1)
        v.addWidget(sep)

        # Detaylar
        for emoji, etiket, deger in [
            ("👥", "Kayıtlı Öğrenci", str(k.get("kayit_sayisi", 0))),
            ("🎯", "Kontenjan",         str(k.get("kontenjan", "?"))),
            ("📊", "Seviye",            k.get("seviye", "—")),
            ("📂", "Kategori",          k.get("kategori", "—")),
        ]:
            r = QHBoxLayout()
            r.setSpacing(8)
            r.addWidget(QLabel(f"{emoji}  {etiket}"))
            d = QLabel(deger)
            d.setProperty("textStyle", "bold13")
            d.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            r.addWidget(d, 1)
            v.addLayout(r)

        # Kontenjan progress
        kon = k.get("kontenjan", 0)
        kay = k.get("kayit_sayisi", 0)
        if kon > 0:
            pb = QProgressBar()
            pb.setMaximum(kon)
            pb.setValue(kay)
            pb.setTextVisible(False)
            v.addWidget(pb)
            doluluk = QLabel(f"%{int(kay / kon * 100)} doluluk")
            doluluk.setProperty("dim", True)
            doluluk.setAlignment(Qt.AlignCenter)
            v.addWidget(doluluk)

        return kart

    def _ilerleme_karti(self, kayit) -> QFrame:
        kart = QFrame()
        kart.setProperty("card", True)
        h = QHBoxLayout(kart)
        h.setContentsMargins(20, 16, 20, 16)
        h.setSpacing(18)

        ring = ProgressRing(kayit.get("ilerleme", 0), 80, "#10b981")
        h.addWidget(ring)

        v = QVBoxLayout()
        bas = QLabel("İlerleme Durumu")
        bas.setProperty("sectionTitle", True)
        v.addWidget(bas)
        alt = QLabel(f"Bu kursta %{kayit.get('ilerleme', 0)} tamamladınız.")
        alt.setProperty("muted", True)
        v.addWidget(alt)
        h.addLayout(v, 1)

        # +25% buton (demo)
        ileri = QPushButton("+25% İlerle")
        ileri.setMinimumHeight(36)
        ileri.setCursor(Qt.PointingHandCursor)
        ileri.clicked.connect(self._ilerleme_arttir)
        h.addWidget(ileri)
        return kart

    def _yorumlar_karti(self) -> QFrame:
        kart = QFrame()
        kart.setProperty("card", True)
        v = QVBoxLayout(kart)
        v.setContentsMargins(18, 16, 18, 16)
        v.setSpacing(12)

        bas = QLabel(f"💬 Yorumlar ({self.kurs.get('yorum_sayisi', 0)})")
        bas.setProperty("sectionTitle", True)
        v.addWidget(bas)

        # Yorum yazma (sadece kayıtlılara)
        if self._kayitli_mi():
            v.addWidget(self._yorum_yazma_alani())
        elif self.kullanici.get("rol") == "ogrenci":
            inf = QLabel("ℹ️ Yorum yazmak için bu kursa kayıtlı olmalısınız.")
            inf.setProperty("muted", True)
            v.addWidget(inf)

        # Yorum listesi
        yorumlar = self.services["yorum"].kurs_yorumlari(self.kurs_id)
        if not yorumlar:
            bos = QLabel("Henüz yorum yapılmamış. İlk yorumu sen yap!")
            bos.setProperty("muted", True)
            bos.setAlignment(Qt.AlignCenter)
            bos.setMinimumHeight(60)
            v.addWidget(bos)
        else:
            for y in yorumlar:
                v.addWidget(self._yorum_satiri(y))

        return kart

    def _yorum_satiri(self, y) -> QFrame:
        f = QFrame()
        f.setStyleSheet("QFrame{ background: transparent; border-bottom: 1px solid rgba(150,150,150,0.15); padding: 4px 0; }")
        h = QHBoxLayout(f)
        h.setContentsMargins(0, 8, 0, 8)
        h.setSpacing(12)

        av = Avatar(y.get("kullanici_ad", "?"),
                    y.get("kullanici_soyad", ""),
                    y.get("avatar_renk") or "#6366f1", 36)
        h.addWidget(av, 0, Qt.AlignTop)

        v = QVBoxLayout()
        v.setSpacing(4)
        ust = QHBoxLayout()
        ad = QLabel(f"{y.get('kullanici_ad','')} {y.get('kullanici_soyad','')}")
        ad.setProperty("textStyle", "bold13")
        ust.addWidget(ad)
        rt = StarRating(y.get("puan", 0), boyut=12, etkilesimli=False)
        ust.addWidget(rt)
        ust.addStretch()
        tar = QLabel((y.get("tarih") or "")[:16])
        tar.setProperty("dim", True)
        ust.addWidget(tar)
        # Silme yetkisi kontrolü
        if self.services["yorum"].silebilir_mi(y["id"], self.kullanici):
            sil = QPushButton("🗑")
            sil.setProperty("ghost", True)
            sil.setFixedWidth(30)
            sil.setToolTip("Yorumu sil")
            sil.setCursor(Qt.PointingHandCursor)
            sil.clicked.connect(lambda _, yid=y["id"]: self._yorum_sil(yid))
            ust.addWidget(sil)
        v.addLayout(ust)
        if y.get("mesaj"):
            m = QLabel(y["mesaj"])
            m.setProperty("muted", True)
            m.setWordWrap(True)
            v.addWidget(m)
        h.addLayout(v, 1)
        return f

    def _yorum_yazma_alani(self) -> QFrame:
        f = QFrame()
        f.setStyleSheet("QFrame{background: rgba(99,102,241,0.05); border-radius: 10px;}")
        v = QVBoxLayout(f)
        v.setContentsMargins(14, 12, 14, 12)
        v.setSpacing(8)

        # Yıldız seçici
        h1 = QHBoxLayout()
        h1.addWidget(QLabel("Puanın:"))
        self._yorum_rating = StarRating(5, etkilesimli=True, boyut=20)
        h1.addWidget(self._yorum_rating)
        h1.addStretch()
        v.addLayout(h1)

        self._yorum_input = QTextEdit()
        self._yorum_input.setPlaceholderText("Bu kurs hakkında ne düşünüyorsun?")
        self._yorum_input.setMaximumHeight(80)
        v.addWidget(self._yorum_input)

        gonder = QPushButton("Yorumu Gönder")
        gonder.setProperty("primary", True)
        gonder.setCursor(Qt.PointingHandCursor)
        gonder.clicked.connect(self._yorum_gonder)
        v.addWidget(gonder, 0, Qt.AlignRight)
        return f

    # ────── İŞLEMLER ────────────────────────────────────────────────────
    def _kayitli_mi(self):
        if self.kullanici.get("rol") != "ogrenci":
            return None
        og = self.services["ogrenci"].kullanici_id_ile_bul(self.kullanici["id"])
        if not og:
            return None
        c = self.vt.baglanti.cursor()
        c.execute("SELECT * FROM kayitlar WHERE kurs_id = ? AND ogrenci_id = ?",
                  (self.kurs_id, og["id"]))
        r = c.fetchone()
        return dict(r) if r else None

    def _kursa_kaydol(self):
        og = self.services["ogrenci"].kullanici_id_ile_bul(self.kullanici["id"])
        if not og:
            ToastYoneticisi.goster(self.mw, "Öğrenci kaydı bulunamadı.", "hata")
            return
        sonuc = self.services["kurs"].ogrenci_kaydet(self.kurs_id, og["id"])
        if sonuc["basarili"]:
            self.services["bildirim"].gonder(
                self.kullanici["id"],
                "Kursa kayıt olundu",
                f"{self.kurs['ad']} kursuna başarıyla kaydoldunuz.",
                "basari")
            self.services["logger"].info("kurs",
                f"Kayıt: {self.kullanici['kullanici_adi']} → {self.kurs['ad']}",
                kullanici_id=self.kullanici["id"])
            ToastYoneticisi.goster(self.mw, "🎉 Kursa başarıyla kaydoldunuz!", "basari")
            self.mw.bildirim_sayisini_guncelle()
            self.yenile(kurs_id=self.kurs_id)
        else:
            ToastYoneticisi.goster(self.mw, sonuc.get("mesaj", "Kayıt başarısız"), "hata")

    def _kurstan_cik(self):
        og = self.services["ogrenci"].kullanici_id_ile_bul(self.kullanici["id"])
        if not og:
            return
        sonuc = self.services["kurs"].ogrenci_cikar(self.kurs_id, og["id"])
        if sonuc["basarili"]:
            ToastYoneticisi.goster(self.mw, "Kurstan ayrıldınız.", "bilgi")
            self.yenile(kurs_id=self.kurs_id)

    def _favori_toggle(self, btn):
        sonuc = self.services["favori"].ekle_cikar(self.kurs_id, self.kullanici["id"])
        if sonuc.get("favori"):
            btn.setText("💖  Favoriden Çıkar")
            ToastYoneticisi.goster(self.mw, "Favorilere eklendi.", "basari")
        else:
            btn.setText("🤍  Favorilere Ekle")
            ToastYoneticisi.goster(self.mw, "Favorilerden çıkarıldı.", "bilgi")

    def _yorum_gonder(self):
        mesaj = self._yorum_input.toPlainText().strip()
        puan = int(self._yorum_rating.puan())
        if not mesaj:
            ToastYoneticisi.goster(self.mw, "Lütfen bir yorum yazın.", "uyari")
            return
        sonuc = self.services["yorum"].ekle(
            self.kurs_id, self.kullanici["id"], puan, mesaj)
        if sonuc["basarili"]:
            ToastYoneticisi.goster(self.mw, "Yorumunuz eklendi 🎉", "basari")
            self.yenile(kurs_id=self.kurs_id)

    def _ilerleme_arttir(self):
        og = self.services["ogrenci"].kullanici_id_ile_bul(self.kullanici["id"])
        if not og:
            return
        kayit = self._kayitli_mi()
        if not kayit:
            return
        yeni = min(100, kayit.get("ilerleme", 0) + 25)
        self.services["kurs"].ilerleme_guncelle(self.kurs_id, og["id"], yeni)
        ToastYoneticisi.goster(self.mw, f"İlerleme %{yeni}'e güncellendi", "basari")
        if yeni >= 100:
            self.services["bildirim"].gonder(
                self.kullanici["id"],
                "🎓 Kursu tamamladınız!",
                f"{self.kurs['ad']} kursunu başarıyla tamamladınız.",
                "basari")
            self.mw.bildirim_sayisini_guncelle()
        self.yenile(kurs_id=self.kurs_id)

    # ────── EĞİTMEN/ADMIN YETKİLERİ ─────────────────────────────────────
    def _kursu_yonetebilir(self) -> bool:
        """Bu kullanıcı bu kursu düzenleyebilir/silebilir mi?"""
        if self.kullanici.get("rol") == "admin":
            return True
        if self.kullanici.get("rol") == "egitmen":
            return self.services["kurs"].sahibi_mi(
                self.kurs_id, self.kullanici["id"])
        return False

    def _kursu_duzenle(self):
        if not self._kursu_yonetebilir():
            return
        d = KursDialog(self.kurs, parent=self.mw)
        if d.exec_() != d.Accepted:
            return
        vals = d.degerler()
        sonuc = self.services["kurs"].guncelle(self.kurs_id, **vals)
        if sonuc.get("basarili"):
            self.services["logger"].info("kurs",
                f"Kurs güncellendi: {vals['ad']}",
                kullanici_id=self.kullanici["id"])
            ToastYoneticisi.goster(self.mw, "✅ Kurs güncellendi.", "basari")
            self.yenile(kurs_id=self.kurs_id)
        else:
            ToastYoneticisi.goster(self.mw,
                sonuc.get("mesaj", "Güncelleme başarısız."), "hata")

    def _yayin_toggle(self):
        if not self._kursu_yonetebilir():
            return
        yeni = 0 if self.kurs.get("yayinda") else 1
        self.services["kurs"].guncelle(self.kurs_id, yayinda=yeni)
        self.services["logger"].info("kurs",
            f"Kurs {'yayında' if yeni else 'taslakta'}: {self.kurs['ad']}",
            kullanici_id=self.kullanici["id"])
        ToastYoneticisi.goster(self.mw,
            "🚀 Kurs yayında" if yeni else "📥 Kurs taslağa alındı", "basari")
        self.yenile(kurs_id=self.kurs_id)

    def _kursu_sil(self):
        if not self._kursu_yonetebilir():
            return
        m = QMessageBox(self.mw)
        m.setWindowTitle("Kursu Sil")
        m.setText(f"\"{self.kurs['ad']}\" kursunu silmek istiyor musunuz?\n"
                  "Bu işlem geri alınamaz! Tüm kayıtlar ve yorumlar da silinir.")
        m.setIcon(QMessageBox.Warning)
        evet = m.addButton("Evet, sil", QMessageBox.YesRole)
        m.addButton("Vazgeç", QMessageBox.NoRole)
        m.exec_()
        if m.clickedButton() != evet:
            return
        self.services["kurs"].sil(self.kurs_id)
        self.services["logger"].uyari("kurs",
            f"Kurs silindi: {self.kurs['ad']}",
            kullanici_id=self.kullanici["id"])
        ToastYoneticisi.goster(self.mw, "🗑 Kurs silindi.", "basari")
        # Geri dön
        self.mw.sayfayaGec("kurslar")

    def _yorum_sil(self, yid: int):
        if not self.services["yorum"].silebilir_mi(yid, self.kullanici):
            ToastYoneticisi.goster(self.mw,
                "⛔ Bu yorumu silme yetkiniz yok.", "hata")
            return
        self.services["yorum"].sil(yid)
        self.services["logger"].uyari("yorum",
            f"Yorum silindi: ID={yid}",
            kullanici_id=self.kullanici["id"])
        ToastYoneticisi.goster(self.mw, "🗑 Yorum silindi.", "basari")
        self.yenile(kurs_id=self.kurs_id)
