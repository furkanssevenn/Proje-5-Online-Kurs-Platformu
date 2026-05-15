"""
═══════════════════════════════════════════════════════════════════════════
  MODERN WIDGET KÜTÜPHANESİ
═══════════════════════════════════════════════════════════════════════════
  Avatar, kart, gradient kapak, yıldız puanlama, toast, stat card,
  arama kutusu, gradient banner, animasyonlu ikon butonları, vb.
"""
from PyQt5.QtCore import (Qt, QSize, QPropertyAnimation, QEasingCurve,
                          QPoint, QRect, QTimer, pyqtSignal,
                          QParallelAnimationGroup, pyqtProperty)
from PyQt5.QtGui import (QPainter, QColor, QLinearGradient, QBrush, QPen,
                         QFont, QPainterPath, QFontMetrics, QPixmap,
                         QRadialGradient, QPolygon)
from PyQt5.QtWidgets import (QWidget, QFrame, QLabel, QPushButton,
                             QVBoxLayout, QHBoxLayout, QLineEdit,
                             QGraphicsDropShadowEffect, QSizePolicy,
                             QStackedLayout, QProgressBar)


# ═════════════════════════════════════════════════════════════════════════
#  AVATAR — Gradient circle with initials
# ═════════════════════════════════════════════════════════════════════════
class Avatar(QWidget):
    def __init__(self, ad: str = "?", soyad: str = "",
                 renk: str = "#6366f1", boyut: int = 40, parent=None):
        super().__init__(parent)
        self.harf = ((ad[:1] if ad else "") + (soyad[:1] if soyad else "")).upper() or "?"
        self.renk = QColor(renk)
        self.setFixedSize(boyut, boyut)

    def setData(self, ad: str, soyad: str, renk: str):
        self.harf = ((ad[:1] if ad else "") + (soyad[:1] if soyad else "")).upper() or "?"
        self.renk = QColor(renk)
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(1, 1, -1, -1)

        grad = QLinearGradient(0, 0, 0, self.height())
        c1 = self.renk
        c2 = self.renk.darker(125)
        grad.setColorAt(0, c1)
        grad.setColorAt(1, c2)
        p.setBrush(QBrush(grad))
        p.setPen(Qt.NoPen)
        p.drawEllipse(rect)

        p.setPen(QColor("white"))
        f = QFont("Inter", int(self.height() * 0.38), QFont.Bold)
        p.setFont(f)
        p.drawText(rect, Qt.AlignCenter, self.harf)


# ═════════════════════════════════════════════════════════════════════════
#  GRADIENT BANNER (kurs kapakları için)
# ═════════════════════════════════════════════════════════════════════════
class GradientBanner(QWidget):
    def __init__(self, renkler: str = "#6366f1,#8b5cf6",
                 yazi: str = "", emoji: str = "📚",
                 yukseklik: int = 130, parent=None):
        super().__init__(parent)
        self.renkler = renkler.split(",")
        self.yazi = yazi
        self.emoji = emoji
        self.setFixedHeight(yukseklik)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 14, 14)
        p.setClipPath(path)

        g = QLinearGradient(0, 0, self.width(), self.height())
        for i, r in enumerate(self.renkler):
            g.setColorAt(i / max(1, len(self.renkler) - 1), QColor(r.strip()))
        p.fillRect(self.rect(), g)

        # dekoratif daire
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(255, 255, 255, 22))
        p.drawEllipse(self.width() - 100, -40, 180, 180)
        p.setBrush(QColor(255, 255, 255, 14))
        p.drawEllipse(-30, self.height() - 60, 120, 120)

        # emoji
        p.setPen(QColor("white"))
        f = QFont("Inter", 38)
        p.setFont(f)
        p.drawText(self.rect().adjusted(20, 0, 0, 0), Qt.AlignVCenter | Qt.AlignLeft, self.emoji)

        if self.yazi:
            f = QFont("Inter", 14, QFont.Bold)
            p.setFont(f)
            r = self.rect().adjusted(80, 0, -16, 0)
            p.setPen(QColor(255, 255, 255, 220))
            p.drawText(r, Qt.AlignVCenter | Qt.AlignLeft, self.yazi)


# ═════════════════════════════════════════════════════════════════════════
#  STAT CARD — büyük renkli kart, ikon + değer + etiket
# ═════════════════════════════════════════════════════════════════════════
class StatCard(QFrame):
    def __init__(self, baslik: str, deger: str, emoji: str = "📊",
                 renk: str = "#6366f1,#8b5cf6", parent=None):
        super().__init__(parent)
        self._renkler = renk.split(",")
        self.setFixedHeight(115)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(2)

        emoji_lbl = QLabel(emoji)
        emoji_lbl.setStyleSheet("font-size: 24px; background: transparent;")
        lay.addWidget(emoji_lbl)

        self.deger_lbl = QLabel(deger)
        self.deger_lbl.setStyleSheet(
            "font-size: 28px; font-weight: 800; color: white; background: transparent;"
        )
        lay.addWidget(self.deger_lbl)

        bas_lbl = QLabel(baslik)
        bas_lbl.setStyleSheet(
            "font-size: 12px; color: rgba(255,255,255,0.85); background: transparent;"
        )
        lay.addWidget(bas_lbl)

    def setDeger(self, v: str):
        self.deger_lbl.setText(v)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 14, 14)
        p.setClipPath(path)

        g = QLinearGradient(0, 0, self.width(), self.height())
        for i, r in enumerate(self._renkler):
            g.setColorAt(i / max(1, len(self._renkler) - 1), QColor(r.strip()))
        p.fillRect(self.rect(), g)

        # parlama
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(255, 255, 255, 25))
        p.drawEllipse(self.width() - 60, -40, 130, 130)


# ═════════════════════════════════════════════════════════════════════════
#  STAR RATING — interaktif yıldız widget'ı
# ═════════════════════════════════════════════════════════════════════════
class StarRating(QWidget):
    degisti = pyqtSignal(int)

    def __init__(self, puan: float = 0, max_puan: int = 5,
                 boyut: int = 22, etkilesimli: bool = True, parent=None):
        super().__init__(parent)
        self._puan = float(puan)
        self.max_puan = max_puan
        self.boyut = boyut
        self.etkilesimli = etkilesimli
        self.setFixedHeight(boyut + 4)
        self.setMinimumWidth((boyut + 4) * max_puan)
        if etkilesimli:
            self.setCursor(Qt.PointingHandCursor)

    def puan(self) -> float:
        return self._puan

    def setPuan(self, p: float):
        self._puan = max(0, min(self.max_puan, float(p)))
        self.update()

    def mousePressEvent(self, e):
        if not self.etkilesimli:
            return
        x = e.pos().x()
        secilen = max(1, min(self.max_puan,
                             int(x / (self.boyut + 4)) + 1))
        self._puan = secilen
        self.update()
        self.degisti.emit(secilen)

    def _yildiz_path(self, x, y, r) -> QPainterPath:
        import math
        path = QPainterPath()
        for i in range(10):
            ang = math.pi / 2 + i * math.pi / 5
            rr = r if i % 2 == 0 else r * 0.45
            px = x + math.cos(ang) * rr
            py = y - math.sin(ang) * rr
            (path.moveTo if i == 0 else path.lineTo)(px, py)
        path.closeSubpath()
        return path

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        for i in range(self.max_puan):
            cx = (self.boyut + 4) * i + self.boyut / 2 + 2
            cy = self.height() / 2
            path = self._yildiz_path(cx, cy, self.boyut / 2.2)
            doluluk = max(0, min(1, self._puan - i))

            # arkaplan (boş)
            p.setPen(QPen(QColor("#d1d5db"), 1))
            p.setBrush(QColor("#374151"))
            p.drawPath(path)

            # dolu
            if doluluk > 0:
                p.save()
                p.setClipRect(QRect(int(cx - self.boyut / 2),
                                    0,
                                    int(doluluk * self.boyut),
                                    self.height()))
                p.setPen(Qt.NoPen)
                grad = QLinearGradient(0, 0, 0, self.height())
                grad.setColorAt(0, QColor("#fbbf24"))
                grad.setColorAt(1, QColor("#f59e0b"))
                p.setBrush(QBrush(grad))
                p.drawPath(path)
                p.restore()


# ═════════════════════════════════════════════════════════════════════════
#  SEARCH BAR — sol tarafta arama ikonu olan input
# ═════════════════════════════════════════════════════════════════════════
class SearchBar(QWidget):
    aramaDegisti = pyqtSignal(str)

    def __init__(self, placeholder: str = "Ara...", parent=None):
        super().__init__(parent)
        self.setFixedHeight(42)

        self.input = QLineEdit(self)
        self.input.setPlaceholderText(placeholder)
        self.input.setProperty("search", True)
        self.input.textChanged.connect(self._gecikmeli)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.input)

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(
            lambda: self.aramaDegisti.emit(self.input.text())
        )

        self.icon_lbl = QLabel("🔍", self.input)
        self.icon_lbl.setStyleSheet(
            "background: transparent; font-size: 14px; color: #9aa0ad;"
        )
        self.icon_lbl.move(12, 12)

    def _gecikmeli(self, _):
        self._timer.start(220)

    def text(self) -> str:
        return self.input.text()


# ═════════════════════════════════════════════════════════════════════════
#  TOAST — sağ alt köşeden kayan bildirim
# ═════════════════════════════════════════════════════════════════════════
class Toast(QFrame):
    RENKLER = {
        "basari":  ("#10b981", "✓"),
        "hata":    ("#ef4444", "✕"),
        "uyari":   ("#f59e0b", "!"),
        "bilgi":   ("#3b82f6", "i"),
    }

    def __init__(self, mesaj: str, tip: str = "bilgi", parent=None,
                 sure_ms: int = 3000):
        super().__init__(parent, Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        renk, sembol = self.RENKLER.get(tip, self.RENKLER["bilgi"])

        kart = QFrame(self)
        kart.setStyleSheet(f"""
            QFrame {{
                background-color: #1a1d27;
                border: 1px solid #2a2e3a;
                border-radius: 12px;
            }}
        """)
        sg = QGraphicsDropShadowEffect()
        sg.setBlurRadius(30)
        sg.setOffset(0, 6)
        sg.setColor(QColor(0, 0, 0, 110))
        kart.setGraphicsEffect(sg)

        h = QHBoxLayout(kart)
        h.setContentsMargins(14, 12, 18, 12)
        h.setSpacing(12)

        # Renkli yuvarlak ikon
        ikon = QLabel(sembol)
        ikon.setFixedSize(28, 28)
        ikon.setAlignment(Qt.AlignCenter)
        ikon.setStyleSheet(f"""
            background: {renk};
            color: white;
            border-radius: 14px;
            font-weight: 800;
            font-size: 13px;
        """)
        h.addWidget(ikon)

        lbl = QLabel(mesaj)
        lbl.setStyleSheet("color: #e7e9ee; font-size: 13px; background: transparent;")
        lbl.setWordWrap(True)
        h.addWidget(lbl, 1)

        ana = QVBoxLayout(self)
        ana.setContentsMargins(0, 0, 0, 0)
        ana.addWidget(kart)

        self.adjustSize()
        self.resize(max(280, self.sizeHint().width()), self.sizeHint().height())

        QTimer.singleShot(sure_ms, self._kapat)

    def goster_at(self, x: int, y: int):
        self.move(x, y + 30)
        self.setWindowOpacity(0)
        self.show()

        # fade-in + slide-up paralel
        opa = QPropertyAnimation(self, b"windowOpacity")
        opa.setDuration(220)
        opa.setStartValue(0.0)
        opa.setEndValue(1.0)

        pos = QPropertyAnimation(self, b"pos")
        pos.setDuration(280)
        pos.setStartValue(QPoint(x, y + 30))
        pos.setEndValue(QPoint(x, y))
        pos.setEasingCurve(QEasingCurve.OutCubic)

        self._anim = QParallelAnimationGroup(self)
        self._anim.addAnimation(opa)
        self._anim.addAnimation(pos)
        self._anim.start()

    def _kapat(self):
        opa = QPropertyAnimation(self, b"windowOpacity")
        opa.setDuration(220)
        opa.setStartValue(self.windowOpacity())
        opa.setEndValue(0.0)
        opa.finished.connect(self.close)
        opa.start()
        self._fade = opa


class ToastYoneticisi:
    """Aktif toast'ları üst üste değil, üst üste dizmeden yöneten singleton-vari sınıf."""
    _aktif = []

    @classmethod
    def goster(cls, parent_window, mesaj: str, tip: str = "bilgi", sure_ms: int = 3000):
        t = Toast(mesaj, tip, sure_ms=sure_ms)
        cls._aktif.append(t)

        # Ana pencerenin sağ-alt köşesi
        if parent_window:
            tl = parent_window.geometry().bottomRight()
            x = tl.x() - t.width() - 24
            y_base = tl.y() - t.height() - 24
        else:
            from PyQt5.QtWidgets import QApplication
            scr = QApplication.primaryScreen().geometry()
            x = scr.right() - t.width() - 24
            y_base = scr.bottom() - t.height() - 24

        # diğer aktif toast'lar varsa yukarı kay
        offset = sum(o.height() + 8 for o in cls._aktif[:-1] if o.isVisible())
        t.goster_at(x, y_base - offset)

        # kapanınca listeden çıkar
        def temizle():
            try:
                cls._aktif.remove(t)
            except ValueError:
                pass
        t.destroyed.connect(temizle)


# ═════════════════════════════════════════════════════════════════════════
#  ICON BUTTON — yuvarlak küçük buton (bell, dark-mode toggle vs)
# ═════════════════════════════════════════════════════════════════════════
class IconButton(QPushButton):
    def __init__(self, sembol: str = "🔔", boyut: int = 38,
                 ipucu: str = "", parent=None):
        super().__init__("", parent)
        self.setFixedSize(boyut, boyut)
        self.setProperty("icon", True)
        self.setCursor(Qt.PointingHandCursor)
        if ipucu:
            self.setToolTip(ipucu)

        self._lbl = QLabel(sembol, self)
        self._lbl.setAlignment(Qt.AlignCenter)
        self._lbl.setStyleSheet("font-family: 'Segoe UI Emoji', 'Apple Color Emoji', sans-serif; font-size: 16px; background: transparent; border: none;")
        self._lbl.setAttribute(Qt.WA_TransparentForMouseEvents)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._lbl)

    def setSembol(self, s: str):
        self._lbl.setText(s)


class BadgeButton(IconButton):
    """Üzerine küçük kırmızı sayı badge'i basan bildirim ikonu."""
    def __init__(self, sembol: str = "🔔", boyut: int = 38, parent=None):
        super().__init__(sembol, boyut, parent=parent)
        self._sayi = 0
        self._badge_lbl = QLabel(self)
        self._badge_lbl.setAttribute(Qt.WA_TransparentForMouseEvents)
        self._badge_lbl.setGeometry(self.width() - 18, 4, 16, 16)
        self._badge_lbl.setAlignment(Qt.AlignCenter)
        self._badge_lbl.setStyleSheet("background: #ef4444; color: white; border-radius: 8px; font-family: Inter, sans-serif; font-size: 9px; font-weight: 800; border: none;")
        self._badge_lbl.hide()

    def setSayi(self, s: int):
        self._sayi = s
        if s > 0:
            self._badge_lbl.setText("9+" if s > 9 else str(s))
            self._badge_lbl.show()
        else:
            self._badge_lbl.hide()


# ═════════════════════════════════════════════════════════════════════════
#  PROGRESS RING — yuvarlak ilerleme göstergesi
# ═════════════════════════════════════════════════════════════════════════
class ProgressRing(QWidget):
    def __init__(self, yuzde: int = 0, boyut: int = 60,
                 renk: str = "#6366f1", parent=None):
        super().__init__(parent)
        self._yuzde = yuzde
        self._renk = QColor(renk)
        self.setFixedSize(boyut, boyut)

    def setYuzde(self, y: int):
        self._yuzde = max(0, min(100, int(y)))
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = self.rect().adjusted(4, 4, -4, -4)
        kalin = 5
        # zemin halka
        p.setPen(QPen(QColor(80, 80, 100, 70), kalin, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(r, 0, 360 * 16)
        # dolu halka
        p.setPen(QPen(self._renk, kalin, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(r, 90 * 16, -int(self._yuzde * 360 / 100) * 16)
        # metin
        p.setPen(QColor("white") if self.window().property("dark") else QColor("#111"))
        f = QFont("Inter", int(self.height() / 4.5), QFont.Bold)
        p.setFont(f)
        p.drawText(self.rect(), Qt.AlignCenter, f"%{self._yuzde}")


# ═════════════════════════════════════════════════════════════════════════
#  COURSE CARD — bir kursu hover/click edilebilir kart olarak gösterir
# ═════════════════════════════════════════════════════════════════════════
class CourseCard(QFrame):
    tiklandi = pyqtSignal(int)

    KATEGORI_EMOJI = {
        "Programlama":  "💻",
        "Web Geliştirme": "🌐",
        "Veri Bilimi":  "📊",
        "Tasarım":      "🎨",
        "Genel":        "📚",
    }

    def __init__(self, kurs: dict, parent=None):
        super().__init__(parent)
        self.kurs = kurs
        self.setProperty("card", True)
        self.setProperty("cardHover", True)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(330)
        self.setMaximumHeight(380)
        self.setMinimumWidth(260)

        emoji = self.KATEGORI_EMOJI.get(kurs.get("kategori", ""), "📚")
        kapak_renk = kurs.get("kapak_renk") or "#6366f1,#8b5cf6"

        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)

        # Kapak banner
        banner = GradientBanner(kapak_renk, "", emoji, 120)
        v.addWidget(banner)

        # İçerik
        ic = QWidget()
        ic_lay = QVBoxLayout(ic)
        ic_lay.setContentsMargins(16, 14, 16, 14)
        ic_lay.setSpacing(8)

        # Üst chip'ler
        chip_row = QHBoxLayout()
        chip_row.setSpacing(6)
        kat = QLabel(kurs.get("kategori", "Genel"))
        kat.setProperty("chip", True)
        kat.setProperty("chipBrand", True)
        chip_row.addWidget(kat)
        sev = QLabel(kurs.get("seviye", "Başlangıç"))
        sev.setProperty("chip", True)
        sev.setProperty("chipInfo", True)
        chip_row.addWidget(sev)
        chip_row.addStretch()
        if (kurs.get("fiyat") or 0) <= 0:
            uc = QLabel("ÜCRETSİZ")
            uc.setProperty("chip", True)
            uc.setProperty("chipSuccess", True)
            chip_row.addWidget(uc)
        ic_lay.addLayout(chip_row)

        # Başlık
        baslik = QLabel(kurs["ad"])
        baslik.setStyleSheet("font-size: 16px; font-weight: 700; background: transparent;")
        baslik.setWordWrap(True)
        ic_lay.addWidget(baslik)

        # Eğitmen
        eg = QLabel(f"👤 {kurs.get('egitmen_ad','')} {kurs.get('egitmen_soyad','')}".strip())
        eg.setProperty("muted", True)
        eg.setStyleSheet("font-size: 12px; background: transparent;")
        ic_lay.addWidget(eg)

        # Açıklama
        if kurs.get("aciklama"):
            ac = QLabel(kurs["aciklama"])
            ac.setProperty("muted", True)
            ac.setStyleSheet("font-size: 12px; background: transparent;")
            ac.setWordWrap(True)
            ac.setMaximumHeight(34)
            ic_lay.addWidget(ac)

        ic_lay.addStretch()

        # Alt: yıldız + fiyat
        alt = QHBoxLayout()
        alt.setSpacing(8)
        rating = StarRating(kurs.get("ort_puan") or 0, boyut=14, etkilesimli=False)
        alt.addWidget(rating)
        ys = QLabel(f"({kurs.get('yorum_sayisi') or 0})")
        ys.setProperty("dim", True)
        alt.addWidget(ys)
        alt.addStretch()
        kayit = QLabel(f"👥 {kurs.get('kayit_sayisi', 0)}")
        kayit.setProperty("muted", True)
        kayit.setStyleSheet("font-size: 12px; background: transparent;")
        alt.addWidget(kayit)
        ic_lay.addLayout(alt)

        v.addWidget(ic, 1)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.tiklandi.emit(self.kurs["id"])


# ═════════════════════════════════════════════════════════════════════════
#  SECTION HEADER
# ═════════════════════════════════════════════════════════════════════════
class SectionHeader(QWidget):
    def __init__(self, baslik: str, alt_baslik: str = "", parent=None):
        super().__init__(parent)
        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(2)
        b = QLabel(baslik)
        b.setProperty("pageTitle", True)
        v.addWidget(b)
        if alt_baslik:
            a = QLabel(alt_baslik)
            a.setProperty("muted", True)
            v.addWidget(a)


# ═════════════════════════════════════════════════════════════════════════
#  HELPER — Kart oluşturucu
# ═════════════════════════════════════════════════════════════════════════
def kart_olustur(*cocuklar, padding: tuple = (18, 18, 18, 18),
                 spacing: int = 12) -> QFrame:
    f = QFrame()
    f.setProperty("card", True)
    v = QVBoxLayout(f)
    v.setContentsMargins(*padding)
    v.setSpacing(spacing)
    for c in cocuklar:
        if isinstance(c, QWidget):
            v.addWidget(c)
        elif hasattr(c, "addWidget"):  # layout
            v.addLayout(c)
    return f

# ═════════════════════════════════════════════════════════════════════════
#  HELPER — Layout Temizleyici (Nested widgetları siler)
# ═════════════════════════════════════════════════════════════════════════
def temizle_layout(layout):
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                child_layout = item.layout()
                if child_layout is not None:
                    temizle_layout(child_layout)
                    child_layout.deleteLater()
