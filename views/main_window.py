"""
═══════════════════════════════════════════════════════════════════════════
  ANA PENCERE — Sidebar + üst bar + stacked content
═══════════════════════════════════════════════════════════════════════════
"""
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QStackedWidget, QFrame, QLabel, QPushButton,
                             QSizePolicy, QApplication, QMessageBox)

from widgets.sidebar import Sidebar
from widgets.modern import (BadgeButton, IconButton, Avatar,
                            SearchBar, ToastYoneticisi)
import theme


class TopBar(QFrame):
    """Üst bar — sayfa başlığı, arama, bildirim/profil ikonları, dark mode."""

    aramaDegisti     = pyqtSignal(str)
    bildirimTiklandi = pyqtSignal()
    temaToggle       = pyqtSignal()
    aramaIstendi     = pyqtSignal()

    def __init__(self, kullanici: dict, parent=None):
        super().__init__(parent)
        self.setObjectName("TopBar")
        self.setFixedHeight(68)

        h = QHBoxLayout(self)
        h.setContentsMargins(28, 12, 24, 12)
        h.setSpacing(16)

        # Sayfa başlığı
        bas_v = QVBoxLayout()
        bas_v.setSpacing(1)
        self.baslik = QLabel("Ana Sayfa")
        self.baslik.setStyleSheet("font-size: 18px; font-weight: 700; background: transparent;")
        bas_v.addWidget(self.baslik)
        self.alt_baslik = QLabel("")
        self.alt_baslik.setProperty("dim", True)
        bas_v.addWidget(self.alt_baslik)
        h.addLayout(bas_v)

        h.addStretch()

        # Arama (kompakt)
        self.search = SearchBar("Kurs ara...")
        self.search.setMinimumWidth(280)
        self.search.aramaDegisti.connect(self.aramaDegisti.emit)
        h.addWidget(self.search)

        # Tema toggle
        self.tema_btn = IconButton("🌙", 38, "Tema değiştir")
        self.tema_btn.clicked.connect(self.temaToggle.emit)
        h.addWidget(self.tema_btn)

        # Bildirim
        self.bildirim_btn = BadgeButton("🔔", 38)
        self.bildirim_btn.setToolTip("Bildirimler")
        self.bildirim_btn.clicked.connect(self.bildirimTiklandi.emit)
        h.addWidget(self.bildirim_btn)

        # Avatar (kullanıcı bilgisi)
        self.avatar = Avatar(
            kullanici.get("ad", "?"),
            kullanici.get("soyad", ""),
            kullanici.get("avatar_renk") or "#6366f1",
            36,
        )
        h.addWidget(self.avatar)

    def setBaslik(self, b: str, alt: str = ""):
        self.baslik.setText(b)
        self.alt_baslik.setText(alt)
        self.alt_baslik.setVisible(bool(alt))

    def setBildirimSayisi(self, s: int):
        self.bildirim_btn.setSayi(s)

    def setTemaIkon(self, dark: bool):
        self.tema_btn.setSembol("🌙" if dark else "☀️")


class MainWindow(QMainWindow):
    def __init__(self, vt, kullanici: dict, services: dict):
        super().__init__()
        self.vt = vt
        self.kullanici = kullanici
        self.services = services
        self.dark = True

        self.setWindowTitle(f"ByTeach · {kullanici.get('ad','')} {kullanici.get('soyad','')}")
        self.setMinimumSize(1180, 750)
        self.resize(1320, 820)
        self.setStyleSheet(theme.get_qss(dark=True))
        self.setProperty("dark", True)

        # ───── Merkez widget ─────
        merkez = QWidget()
        merkez.setObjectName("RootBg")
        ana = QHBoxLayout(merkez)
        ana.setContentsMargins(0, 0, 0, 0)
        ana.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar(kullanici)
        self.sidebar.sayfaSecildi.connect(self.sayfayaGec)
        self.sidebar.cikisIstendi.connect(self.cikisYap)
        self.sidebar.profilIstendi.connect(lambda: self.sayfayaGec("profil"))
        ana.addWidget(self.sidebar)

        # Sağ taraf: top bar + stacked content
        sag = QWidget()
        sag_v = QVBoxLayout(sag)
        sag_v.setContentsMargins(0, 0, 0, 0)
        sag_v.setSpacing(0)

        self.top = TopBar(kullanici)
        self.top.bildirimTiklandi.connect(lambda: self.sayfayaGec("bildirimler"))
        self.top.temaToggle.connect(self._tema_degistir)
        sag_v.addWidget(self.top)

        # Stacked içerik
        self.stack = QStackedWidget()
        sag_v.addWidget(self.stack, 1)

        ana.addWidget(sag, 1)
        self.setCentralWidget(merkez)

        # ───── Sayfaları yarat ─────
        self._sayfalar = {}
        self._sayfa_olustur()

        # Açılış sayfası
        self.sayfayaGec("anasayfa")

        # Bildirim sayısını güncelle
        self.bildirim_sayisini_guncelle()

    # ─── Sayfa oluşturma ────────────────────────────────────────────────
    def _sayfa_olustur(self):
        from views.home_view import HomeView
        from views.courses_view import CoursesView
        from views.course_detail_view import CourseDetailView
        from views.student_dashboard import StudentDashboard
        from views.instructor_dashboard import InstructorDashboard
        from views.admin_view import (AdminView, AdminUsersView,
                                       AdminInstructorsView, AdminLogsView,
                                       AdminCoursesView, AdminCommentsView)
        from views.profile_view import ProfileView
        from views.notifications_view import NotificationsView

        self._sayfalar["anasayfa"]     = HomeView(self.vt, self.kullanici, self.services, self)
        self._sayfalar["kurslar"]      = CoursesView(self.vt, self.kullanici, self.services, self)
        self._sayfalar["kurs_detay"]   = CourseDetailView(self.vt, self.kullanici, self.services, self)
        self._sayfalar["dashboard"]    = StudentDashboard(self.vt, self.kullanici, self.services, self)
        self._sayfalar["egitmen"]      = InstructorDashboard(self.vt, self.kullanici, self.services, self)
        self._sayfalar["admin"]        = AdminView(self.vt, self.kullanici, self.services, self)
        self._sayfalar["admin_kullanicilar"] = AdminUsersView(self.vt, self.kullanici, self.services, self)
        self._sayfalar["admin_egitmenler"]   = AdminInstructorsView(self.vt, self.kullanici, self.services, self)
        self._sayfalar["admin_kurslar"]      = AdminCoursesView(self.vt, self.kullanici, self.services, self)
        self._sayfalar["admin_yorumlar"]     = AdminCommentsView(self.vt, self.kullanici, self.services, self)
        self._sayfalar["admin_loglar"]       = AdminLogsView(self.vt, self.kullanici, self.services, self)
        self._sayfalar["profil"]       = ProfileView(self.vt, self.kullanici, self.services, self)
        self._sayfalar["bildirimler"]  = NotificationsView(self.vt, self.kullanici, self.services, self)
        # favoriler sayfası -> dashboard'a yönlendiriyoruz (favori sekmesi var)
        self._sayfalar["favoriler"]    = self._sayfalar["dashboard"]

        for s in self._sayfalar.values():
            if s.parent() != self.stack and s not in [self.stack.widget(i) for i in range(self.stack.count())]:
                self.stack.addWidget(s)

    # ─── Sayfa geçişi ────────────────────────────────────────────────────
    def sayfayaGec(self, anahtar: str, **kw):
        sayfa = self._sayfalar.get(anahtar)
        if sayfa is None:
            return

        # Yenile (eğer destekleniyorsa)
        if hasattr(sayfa, "yenile"):
            sayfa.yenile(**kw)

        self.stack.setCurrentWidget(sayfa)
        self.sidebar.setActive(anahtar if anahtar in self.sidebar._butonlar else "")

        # Top bar başlığı
        basliklar = {
            "anasayfa":      ("Ana Sayfa", "Hoş geldin, öğrenmeye devam et."),
            "kurslar":       ("Tüm Kurslar", "Sana uygun olanı keşfet."),
            "kurs_detay":    ("Kurs Detayı", ""),
            "dashboard":     ("Panelim", "Öğrenme yolculuğun"),
            "egitmen":       ("Eğitmen Panelim", "Kurslarını yönet"),
            "admin":         ("Admin Paneli", "Tüm sistemi kontrol et"),
            "admin_kullanicilar": ("Kullanıcı Yönetimi", ""),
            "admin_egitmenler":   ("Eğitmen Yönetimi", ""),
            "admin_kurslar":      ("Kurs Yönetimi", "Tüm kursları yönet"),
            "admin_yorumlar":     ("Yorum Moderasyonu", "Uygunsuz yorumları temizle"),
            "admin_loglar":  ("Sistem Logları", "Audit & güvenlik"),
            "profil":        ("Profilim", "Hesap bilgilerin"),
            "bildirimler":   ("Bildirimler", "Sistem mesajları"),
        }
        b, alt = basliklar.get(anahtar, (anahtar.title(), ""))
        self.top.setBaslik(b, alt)

    # ─── Tema değiştir ──────────────────────────────────────────────────
    def _tema_degistir(self):
        self.dark = not self.dark
        self.setProperty("dark", self.dark)
        qss_str = theme.get_qss(dark=self.dark)
        self.setStyleSheet(qss_str)
        QApplication.instance().setStyleSheet(qss_str)
        self.top.setTemaIkon(self.dark)
        # Tüm sayfaları ve widget'ları zorla repaint/repolish et
        for w in self.findChildren(QWidget):
            w.style().unpolish(w)
            w.style().polish(w)
            w.update()
        ToastYoneticisi.goster(self,
            f"{'Karanlık' if self.dark else 'Aydınlık'} mod aktif", "bilgi", 1800)

    # ─── Bildirim sayısı ────────────────────────────────────────────────
    def bildirim_sayisini_guncelle(self):
        bs = self.services["bildirim"].kullanici_bildirimleri(
            self.kullanici["id"], sadece_okunmamis=True)
        self.top.setBildirimSayisi(len(bs))

    # ─── Çıkış ──────────────────────────────────────────────────────────
    def cikisYap(self):
        # Onaylı çıkış
        m = QMessageBox(self)
        m.setWindowTitle("Çıkış")
        m.setText("Çıkış yapmak istediğinize emin misiniz?")
        m.setIcon(QMessageBox.Question)
        evet = m.addButton("Evet, çıkış yap", QMessageBox.YesRole)
        m.addButton("Vazgeç", QMessageBox.NoRole)
        m.exec_()
        if m.clickedButton() == evet:
            self.services["logger"].info("auth",
                f"Çıkış: {self.kullanici['kullanici_adi']}",
                kullanici_id=self.kullanici["id"])
            self.close()
            QApplication.instance().exit(99)  # custom code -> tekrar login
