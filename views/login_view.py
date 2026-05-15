"""
═══════════════════════════════════════════════════════════════════════════
  GİRİŞ EKRANI — Modern split-screen tasarım
═══════════════════════════════════════════════════════════════════════════
  Sol: gradient art panel (hero metin + özellikler)
  Sağ: giriş / kayıt formu (sekmeler ile)
"""
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import (QPainter, QColor, QLinearGradient, QBrush,
                         QFont, QPainterPath)
from PyQt5.QtWidgets import (QDialog, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QFrame,
                             QStackedWidget, QButtonGroup, QRadioButton,
                             QComboBox, QSizePolicy, QMessageBox,
                             QGraphicsDropShadowEffect)

from widgets.modern import ToastYoneticisi
import theme


# ═════════════════════════════════════════════════════════════════════════
#  HERO PANEL (sol taraf)
# ═════════════════════════════════════════════════════════════════════════
class HeroPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(440)

        v = QVBoxLayout(self)
        v.setContentsMargins(48, 56, 48, 56)
        v.setSpacing(0)

        # Logo
        lg = QLabel("🎓")
        lg.setStyleSheet("font-size: 56px; background: transparent;")
        v.addWidget(lg)

        v.addSpacing(28)

        marka = QLabel("ByTeach")
        marka.setStyleSheet(
            "font-size: 36px; font-weight: 800; color: white; "
            "background: transparent;"
        )
        v.addWidget(marka)

        slogan = QLabel("Ultra Profesyonel Online Eğitim Platformu")
        slogan.setStyleSheet(
            "font-size: 15px; color: rgba(255,255,255,0.85); "
            "background: transparent;"
        )
        v.addWidget(slogan)

        v.addSpacing(46)

        # Özellik listesi
        ozellikler = [
            ("⚡", "Hızlı ve Performanslı",
                "Modern PyQt5 ile sıfır gecikmeli arayüz"),
            ("🔐", "Güvenli Altyapı",
                "PBKDF2 hashleme + per-user salt + RBAC"),
            ("🎨", "Modern Tasarım",
                "Dark/light tema, sıvı animasyonlar"),
            ("📊", "Canlı İstatistikler",
                "Pasta ve çubuk grafiklerle yönetim"),
        ]
        for emoji, bas, alt in ozellikler:
            satir = self._ozellik_satiri(emoji, bas, alt)
            v.addWidget(satir)
            v.addSpacing(20)

        v.addStretch()

        # Footer
        ft = QLabel("© 2026 ByTeach — Tüm hakları saklıdır")
        ft.setStyleSheet(
            "font-size: 11px; color: rgba(255,255,255,0.55); background: transparent;"
        )
        v.addWidget(ft)

    def _ozellik_satiri(self, emoji, bas, alt):
        w = QWidget()
        h = QHBoxLayout(w)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(14)

        ic = QLabel(emoji)
        ic.setFixedSize(40, 40)
        ic.setAlignment(Qt.AlignCenter)
        ic.setStyleSheet(
            "background: rgba(255,255,255,0.18); border-radius: 12px; "
            "font-size: 18px;"
        )
        h.addWidget(ic)

        v = QVBoxLayout()
        v.setSpacing(2)
        b = QLabel(bas)
        b.setStyleSheet(
            "font-size: 14px; font-weight: 700; color: white; background: transparent;"
        )
        v.addWidget(b)
        a = QLabel(alt)
        a.setStyleSheet(
            "font-size: 12px; color: rgba(255,255,255,0.78); background: transparent;"
        )
        v.addWidget(a)
        h.addLayout(v, 1)

        return w

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        # gradient arka plan
        g = QLinearGradient(0, 0, self.width(), self.height())
        g.setColorAt(0, QColor("#4338ca"))
        g.setColorAt(0.6, QColor("#6d28d9"))
        g.setColorAt(1, QColor("#9333ea"))
        p.fillRect(self.rect(), g)

        # dekor
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(255, 255, 255, 24))
        p.drawEllipse(self.width() - 200, -100, 400, 400)
        p.setBrush(QColor(255, 255, 255, 14))
        p.drawEllipse(-150, self.height() - 200, 320, 320)


# ═════════════════════════════════════════════════════════════════════════
#  GİRİŞ FORMU
# ═════════════════════════════════════════════════════════════════════════
class GirisForm(QWidget):
    def __init__(self, kullanici_servisi, parent_dialog):
        super().__init__()
        self.kul = kullanici_servisi
        self.parent_dialog = parent_dialog

        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(14)

        bas = QLabel("Tekrar Hoş Geldiniz")
        bas.setStyleSheet("font-size: 26px; font-weight: 800; background: transparent;")
        v.addWidget(bas)

        alt = QLabel("Hesabınıza giriş yaparak öğrenmeye devam edin.")
        alt.setProperty("muted", True)
        v.addWidget(alt)

        v.addSpacing(12)

        v.addWidget(self._etiket("Kullanıcı Adı veya E-posta"))
        self.kul_input = QLineEdit()
        self.kul_input.setPlaceholderText("ornek_kullanici")
        v.addWidget(self.kul_input)

        v.addWidget(self._etiket("Şifre"))
        self.sifre_input = QLineEdit()
        self.sifre_input.setEchoMode(QLineEdit.Password)
        self.sifre_input.setPlaceholderText("••••••••")
        v.addWidget(self.sifre_input)

        v.addSpacing(8)

        # Demo butonları
        dm = QFrame()
        dm.setProperty("card", True)
        dml = QVBoxLayout(dm)
        dml.setContentsMargins(14, 12, 14, 12)
        dml.setSpacing(8)
        dmb = QLabel("⚡  Demo Hesaplar")
        dmb.setStyleSheet("font-size: 12px; font-weight: 700; background: transparent;")
        dml.addWidget(dmb)

        dem_row = QHBoxLayout()
        dem_row.setSpacing(6)
        for k, etiket in [("admin", "🛡️ Admin"),
                           ("ahmet", "🎓 Eğitmen"),
                           ("ayse", "📖 Öğrenci")]:
            btn = QPushButton(etiket)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, kk=k: self._demo_doldur(kk))
            dem_row.addWidget(btn)
        dml.addLayout(dem_row)
        v.addWidget(dm)

        v.addSpacing(6)

        self.giris_btn = QPushButton("Giriş Yap")
        self.giris_btn.setProperty("primary", True)
        self.giris_btn.setMinimumHeight(46)
        self.giris_btn.setCursor(Qt.PointingHandCursor)
        self.giris_btn.clicked.connect(self._giris)
        v.addWidget(self.giris_btn)

        # Enter ile gönder
        self.sifre_input.returnPressed.connect(self._giris)
        self.kul_input.returnPressed.connect(self._giris)

        v.addStretch()

    def _etiket(self, m: str) -> QLabel:
        l = QLabel(m)
        l.setStyleSheet("font-size: 12px; font-weight: 600; background: transparent;")
        return l

    def _demo_doldur(self, kim: str):
        eslesme = {
            "admin": ("admin", "admin123"),
            "ahmet": ("ahmet", "ahmet123"),
            "ayse":  ("ayse",  "ayse123"),
        }
        k, s = eslesme[kim]
        self.kul_input.setText(k)
        self.sifre_input.setText(s)

    def _giris(self):
        ku = self.kul_input.text().strip()
        sf = self.sifre_input.text()
        if not ku or not sf:
            ToastYoneticisi.goster(self.parent_dialog,
                "Lütfen kullanıcı adı ve şifrenizi girin.", "uyari")
            return

        sonuc = self.kul.giris(ku, sf)
        if not sonuc:
            ToastYoneticisi.goster(self.parent_dialog,
                "Kullanıcı adı veya şifre hatalı.", "hata")
            return

        ToastYoneticisi.goster(self.parent_dialog,
            f"Hoş geldin, {sonuc.get('ad', '')}!", "basari")
        self.parent_dialog.aktif_kullanici = sonuc
        QTimer.singleShot(450, self.parent_dialog.accept)


# ═════════════════════════════════════════════════════════════════════════
#  KAYIT FORMU
# ═════════════════════════════════════════════════════════════════════════
class KayitForm(QWidget):
    def __init__(self, kullanici_servisi, logger, parent_dialog):
        super().__init__()
        self.kul = kullanici_servisi
        self.logger = logger
        self.parent_dialog = parent_dialog

        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(10)

        bas = QLabel("Hemen Aramıza Katıl")
        bas.setStyleSheet("font-size: 26px; font-weight: 800; background: transparent;")
        v.addWidget(bas)

        alt = QLabel("Birkaç saniyede ücretsiz hesap oluşturun.")
        alt.setProperty("muted", True)
        v.addWidget(alt)

        v.addSpacing(8)

        ad_row = QHBoxLayout()
        ad_row.setSpacing(8)
        ad_v = QVBoxLayout()
        ad_v.addWidget(self._etiket("Ad"))
        self.ad = QLineEdit(); self.ad.setPlaceholderText("Adınız")
        ad_v.addWidget(self.ad)
        ad_row.addLayout(ad_v)

        s_v = QVBoxLayout()
        s_v.addWidget(self._etiket("Soyad"))
        self.soyad = QLineEdit(); self.soyad.setPlaceholderText("Soyadınız")
        s_v.addWidget(self.soyad)
        ad_row.addLayout(s_v)
        v.addLayout(ad_row)

        v.addWidget(self._etiket("Kullanıcı Adı"))
        self.ku = QLineEdit(); self.ku.setPlaceholderText("benzersiz_kullanici")
        v.addWidget(self.ku)

        v.addWidget(self._etiket("E-posta"))
        self.ep = QLineEdit(); self.ep.setPlaceholderText("ornek@mail.com")
        v.addWidget(self.ep)

        v.addWidget(self._etiket("Şifre (en az 6 karakter)"))
        self.sf = QLineEdit(); self.sf.setEchoMode(QLineEdit.Password)
        self.sf.setPlaceholderText("••••••••")
        v.addWidget(self.sf)

        v.addWidget(self._etiket("Hesap Türü"))
        rol_row = QHBoxLayout()
        rol_row.setSpacing(8)
        self.rol_btn = QButtonGroup(self)
        self.ogrenci_rb = QRadioButton(" 📖   Öğrenciyim")
        self.egitmen_rb = QRadioButton(" 🎓   Eğitmenim")
        self.ogrenci_rb.setChecked(True)
        self.rol_btn.addButton(self.ogrenci_rb, 0)
        self.rol_btn.addButton(self.egitmen_rb, 1)
        for rb in (self.ogrenci_rb, self.egitmen_rb):
            rb.setStyleSheet("""
                QRadioButton {
                    background: rgba(99,102,241,0.06);
                    border: 1.5px solid #2a2e3a;
                    border-radius: 10px;
                    padding: 12px 14px;
                    font-size: 13px;
                }
                QRadioButton:checked {
                    border-color: #6366f1;
                    background: rgba(99,102,241,0.15);
                }
                QRadioButton::indicator { width: 0; height: 0; }
            """)
            rol_row.addWidget(rb)
        v.addLayout(rol_row)

        v.addSpacing(10)

        self.kayit_btn = QPushButton("Hesap Oluştur")
        self.kayit_btn.setProperty("primary", True)
        self.kayit_btn.setMinimumHeight(46)
        self.kayit_btn.setCursor(Qt.PointingHandCursor)
        self.kayit_btn.clicked.connect(self._kaydol)
        v.addWidget(self.kayit_btn)

        v.addStretch()

    def _etiket(self, m: str) -> QLabel:
        l = QLabel(m)
        l.setStyleSheet("font-size: 12px; font-weight: 600; background: transparent;")
        return l

    def _kaydol(self):
        ad = self.ad.text().strip()
        soyad = self.soyad.text().strip()
        ku = self.ku.text().strip()
        ep = self.ep.text().strip()
        sf = self.sf.text()
        rol = "egitmen" if self.egitmen_rb.isChecked() else "ogrenci"

        if not all([ad, soyad, ku, ep, sf]):
            ToastYoneticisi.goster(self.parent_dialog,
                "Lütfen tüm alanları doldurun.", "uyari")
            return

        if "@" not in ep or "." not in ep:
            ToastYoneticisi.goster(self.parent_dialog,
                "Geçerli bir e-posta adresi girin.", "uyari")
            return

        sonuc = self.kul.kaydol(ad, soyad, ku, ep, sf, rol)
        if not sonuc["basarili"]:
            ToastYoneticisi.goster(self.parent_dialog,
                sonuc.get("mesaj", "Kayıt başarısız."), "hata")
            return

        self.logger.info("auth", f"Kayıt: {ku} ({rol})", kullanici_id=sonuc["id"])
        ToastYoneticisi.goster(self.parent_dialog,
            "Kayıt başarılı! Otomatik giriş yapılıyor...", "basari")

        # Otomatik giriş
        kul_dict = self.kul.giris(ku, sf)
        if kul_dict:
            self.parent_dialog.aktif_kullanici = kul_dict
            QTimer.singleShot(700, self.parent_dialog.accept)


# ═════════════════════════════════════════════════════════════════════════
#  GİRİŞ DİYALOĞU (split-screen)
# ═════════════════════════════════════════════════════════════════════════
class GirisDialog(QDialog):
    def __init__(self, kullanici_servisi, logger, parent=None):
        super().__init__(parent)
        self.aktif_kullanici = None
        self.kul = kullanici_servisi
        self.logger = logger

        self.setWindowTitle("ByTeach · Giriş")
        self.setMinimumSize(900, 620)
        self.setStyleSheet(theme.get_qss(dark=True))

        ana = QHBoxLayout(self)
        ana.setContentsMargins(0, 0, 0, 0)
        ana.setSpacing(0)

        # Sol: hero
        ana.addWidget(HeroPanel(), 1)

        # Sağ: form alanı
        sag = QFrame()
        sag.setObjectName("RootBg")
        sl = QVBoxLayout(sag)
        sl.setContentsMargins(46, 36, 46, 36)
        sl.setSpacing(20)

        # Sekmeler
        sekme_row = QHBoxLayout()
        sekme_row.setSpacing(0)
        self.sekme_giris = self._sekme_btn("Giriş Yap", True)
        self.sekme_kayit = self._sekme_btn("Kayıt Ol",  False)
        self.sekme_giris.clicked.connect(lambda: self._sekme_degistir(0))
        self.sekme_kayit.clicked.connect(lambda: self._sekme_degistir(1))
        sekme_row.addWidget(self.sekme_giris)
        sekme_row.addWidget(self.sekme_kayit)
        sekme_row.addStretch()
        sl.addLayout(sekme_row)

        # Stacked formlar
        self.stack = QStackedWidget()
        self.stack.addWidget(GirisForm(kullanici_servisi, self))
        self.stack.addWidget(KayitForm(kullanici_servisi, logger, self))
        sl.addWidget(self.stack, 1)

        ana.addWidget(sag, 1)

    def _sekme_btn(self, etiket: str, aktif: bool) -> QPushButton:
        b = QPushButton(etiket)
        b.setCursor(Qt.PointingHandCursor)
        b.setMinimumHeight(38)
        b.setMinimumWidth(120)
        self._sekme_stil(b, aktif)
        return b

    def _sekme_stil(self, b: QPushButton, aktif: bool):
        if aktif:
            b.setStyleSheet("""
                QPushButton {
                    background: transparent; border: none;
                    color: #6366f1; font-weight: 700; font-size: 14px;
                    padding-bottom: 4px;
                    border-bottom: 2.5px solid #6366f1;
                }""")
        else:
            b.setStyleSheet("""
                QPushButton {
                    background: transparent; border: none;
                    color: #9aa0ad; font-weight: 500; font-size: 14px;
                    padding-bottom: 4px;
                }
                QPushButton:hover { color: #e7e9ee; }""")

    def _sekme_degistir(self, idx: int):
        self.stack.setCurrentIndex(idx)
        self._sekme_stil(self.sekme_giris, idx == 0)
        self._sekme_stil(self.sekme_kayit, idx == 1)
