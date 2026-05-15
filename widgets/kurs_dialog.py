"""
═══════════════════════════════════════════════════════════════════════════
  KURS EKLE/DÜZENLE DIALOG'U
═══════════════════════════════════════════════════════════════════════════
  Hem eğitmen hem admin paneli kullanır.
  Dönüş: dialog.exec_() → Accepted/Rejected
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox,
                             QComboBox, QCheckBox, QPushButton, QFrame)


class KursDialog(QDialog):
    KATEGORILER = ["Programlama", "Web Geliştirme", "Veri Bilimi",
                   "Tasarım", "Genel"]
    SEVIYELER   = ["Başlangıç", "Orta", "İleri"]

    def __init__(self, kurs: dict = None, parent=None):
        super().__init__(parent)
        self.kurs = kurs or {}
        self.setWindowTitle("Kursu Düzenle" if kurs else "Yeni Kurs Ekle")
        self.setMinimumWidth(540)
        self.setModal(True)

        v = QVBoxLayout(self)
        v.setContentsMargins(24, 22, 24, 22)
        v.setSpacing(14)

        bas = QLabel("✏️ Kursu Düzenle" if kurs else "📚 Yeni Kurs Ekle")
        bas.setProperty("pageTitle", True)
        v.addWidget(bas)

        # Ad
        v.addWidget(self._etiket("Kurs Adı"))
        self.ad = QLineEdit(self.kurs.get("ad", ""))
        self.ad.setPlaceholderText("Örn: İleri Python ile Web Scraping")
        v.addWidget(self.ad)

        # Açıklama
        v.addWidget(self._etiket("Açıklama"))
        self.aciklama = QTextEdit(self.kurs.get("aciklama", ""))
        self.aciklama.setPlaceholderText("Kursun içeriğini, hedeflerini, kazanımlarını anlat...")
        self.aciklama.setMaximumHeight(110)
        v.addWidget(self.aciklama)

        # Satır 1: Kategori + Seviye
        r1 = QHBoxLayout()
        r1.setSpacing(10)
        kol1 = QVBoxLayout()
        kol1.setSpacing(4)
        kol1.addWidget(self._etiket("Kategori"))
        self.kategori = QComboBox()
        self.kategori.addItems(self.KATEGORILER)
        if self.kurs.get("kategori") in self.KATEGORILER:
            self.kategori.setCurrentText(self.kurs["kategori"])
        kol1.addWidget(self.kategori)
        r1.addLayout(kol1, 1)

        kol2 = QVBoxLayout()
        kol2.setSpacing(4)
        kol2.addWidget(self._etiket("Seviye"))
        self.seviye = QComboBox()
        self.seviye.addItems(self.SEVIYELER)
        if self.kurs.get("seviye") in self.SEVIYELER:
            self.seviye.setCurrentText(self.kurs["seviye"])
        kol2.addWidget(self.seviye)
        r1.addLayout(kol2, 1)
        v.addLayout(r1)

        # Satır 2: Kontenjan + Fiyat
        r2 = QHBoxLayout()
        r2.setSpacing(10)
        kol3 = QVBoxLayout()
        kol3.setSpacing(4)
        kol3.addWidget(self._etiket("Kontenjan"))
        self.kontenjan = QSpinBox()
        self.kontenjan.setRange(1, 9999)
        self.kontenjan.setValue(int(self.kurs.get("kontenjan", 30) or 30))
        self.kontenjan.setSuffix("  öğrenci")
        kol3.addWidget(self.kontenjan)
        r2.addLayout(kol3, 1)

        kol4 = QVBoxLayout()
        kol4.setSpacing(4)
        kol4.addWidget(self._etiket("Fiyat (₺) — 0 = Ücretsiz"))
        self.fiyat = QDoubleSpinBox()
        self.fiyat.setRange(0, 99999)
        self.fiyat.setDecimals(0)
        self.fiyat.setSingleStep(50)
        self.fiyat.setValue(float(self.kurs.get("fiyat") or 0))
        self.fiyat.setSuffix(" ₺")
        kol4.addWidget(self.fiyat)
        r2.addLayout(kol4, 1)
        v.addLayout(r2)

        # Yayında
        self.yayinda = QCheckBox("📡  Yayında (öğrenciler kayıt olabilsin)")
        self.yayinda.setChecked(bool(self.kurs.get("yayinda", 1)))
        v.addWidget(self.yayinda)

        # Ayrac
        sep = QFrame()
        sep.setProperty("separator", True)
        sep.setFixedHeight(1)
        v.addWidget(sep)

        # Butonlar
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        vazgec = QPushButton("Vazgeç")
        vazgec.setProperty("ghost", True)
        vazgec.setCursor(Qt.PointingHandCursor)
        vazgec.clicked.connect(self.reject)
        btn_row.addWidget(vazgec)

        kaydet = QPushButton("💾  Kaydet" if kurs else "✓  Kursu Oluştur")
        kaydet.setProperty("primary", True)
        kaydet.setMinimumHeight(38)
        kaydet.setCursor(Qt.PointingHandCursor)
        kaydet.clicked.connect(self._kaydet_clicked)
        btn_row.addWidget(kaydet)
        v.addLayout(btn_row)

    def _etiket(self, t: str) -> QLabel:
        l = QLabel(t)
        l.setStyleSheet("font-size: 12px; font-weight: 600; background: transparent;")
        return l

    def _kaydet_clicked(self):
        if not self.ad.text().strip():
            self.ad.setFocus()
            self.ad.setStyleSheet("border: 1.5px solid #ef4444;")
            return
        self.accept()

    def degerler(self) -> dict:
        return {
            "ad":        self.ad.text().strip(),
            "aciklama":  self.aciklama.toPlainText().strip(),
            "kategori":  self.kategori.currentText(),
            "seviye":    self.seviye.currentText(),
            "kontenjan": self.kontenjan.value(),
            "fiyat":     float(self.fiyat.value()),
            "yayinda":   1 if self.yayinda.isChecked() else 0,
        }
