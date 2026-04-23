"""
╔═══════════════════════════════════════════════════════════════════════════╗
║              ByTeach v10.0 — Çevrimiçi Öğrenme Platformu                 ║
╠═══════════════════════════════════════════════════════════════════════════╣
║  ✦ Tamamen yeniden tasarlanmış arayüz — koyu mor/mavi tema              ║
║  ✦ Yeniden çizilmiş harita, kartlar, grafikler                          ║
║                                                                          ║
║  pip install PyQt5 pyttsx3 Pillow                                       ║
║  python app.py                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

import sys, hashlib, sqlite3, random, math, csv, os, threading
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from models import Veritabani, Egitmen, Kurs, Ogrenci, IstatistikYoneticisi

_QLabel = QLabel
class QLabel(_QLabel):
    def setStyleSheet(s, style):
        if "background" not in style: style = "background:transparent;" + style
        super().setStyleSheet(style)

# ══════════════════════════════════════════════════════════════════
#  RENK PALETİ — Yeni mor/mavi derin tema
# ══════════════════════════════════════════════════════════════════
class C:
    # Arka plan tonları - Slate/Dark
    BG     = "#0f172a"    # Slate 900
    BG2    = "#1e293b"    # Slate 800
    BG3    = "#020617"    # Slate 950
    CARD   = "#1e293b"    # Slate 800
    CARD2  = "#334155"    # Slate 700
    CARD3  = "#475569"    # Slate 600
    HOVER  = "#334155"
    BORDER = "#334155"
    BORDER2= "#475569"

    # Metin
    TEXT   = "#f1f5f9"    # Slate 100
    TEXT2  = "#cbd5e1"    # Slate 300
    TEXT3  = "#94a3b8"    # Slate 400

    # Vurgu renkleri (Softer)
    PRI    = "#6366f1"    # Indigo
    PRI2   = "#818cf8"
    BLU    = "#0ea5e9"    # Sky
    BLU2   = "#38bdf8"
    GOLD   = "#8b5cf6"    # Violet
    GOLD2  = "#a78bfa"
    CYAN   = "#06b6d4"    # Cyan
    GREEN  = "#14b8a6"    # Teal
    YELLOW = "#eab308"    # Yellow
    RED    = "#f43f5e"    # Rose
    PINK   = "#d946ef"
    ORANGE = "#f97316"

    # Seven için
    AI     = "#6366f1"
    AI2    = "#818cf8"
    AI3    = "#a5b4fc"

KR = {"Programlama":"#6366f1","Veri Bilimi":"#0ea5e9","Web Geliştirme":"#8b5cf6",
      "Yapay Zeka":"#d946ef","Mobil":"#14b8a6","Siber Güvenlik":"#f43f5e"}

YER = [
    {"ad":"Kadıköy Merkez","tip":"Ana Kampüs","renk":"#3b82f6","x":.68,"y":.62},
    {"ad":"Beşiktaş Şube","tip":"Teknoloji Lab","renk":"#0ea5e9","x":.44,"y":.38},
    {"ad":"Maslak Teknopark","tip":"YZ Merkezi","renk":"#6366f1","x":.50,"y":.18},
    {"ad":"Ataşehir Dijital","tip":"Uzaktan Eğitim","renk":"#8b5cf6","x":.78,"y":.52},
    {"ad":"Beyoğlu Sanat","tip":"Tasarım Stüdyo","renk":"#64748b","x":.38,"y":.44},
]

LOG = []
def log(m, r=None):
    LOG.insert(0, {"m": m, "t": datetime.now().strftime("%H:%M"), "r": r or C.TEXT2})
    if len(LOG) > 20: LOG.pop()


GUN_SIRASI = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]


def ders_programi_yazisi(kurs):
    gun = kurs.get("gun") or "Program yakında"
    bas = kurs.get("baslangic_saati") or "--:--"
    bit = kurs.get("bitis_saati") or "--:--"
    return f"{gun} • {bas} - {bit}"


def ders_platform_yazisi(kurs):
    format_adi = kurs.get("format") or "Canlı"
    platform = kurs.get("platform") or "ByTeach Live"
    return f"{format_adi} • {platform}"


def yaklasan_dersler(kurslar, limit=4):
    sirali = sorted(
        kurslar,
        key=lambda k: (
            GUN_SIRASI.index(k.get("gun")) if k.get("gun") in GUN_SIRASI else len(GUN_SIRASI),
            k.get("baslangic_saati") or "99:99",
            k.get("kurs_adi", "")
        )
    )
    return sirali[:limit]


# ══════════════════════════════════════════════════════════════════
#  YARDIMCI BİLEŞENLER
# ══════════════════════════════════════════════════════════════════
class Toast(QLabel):
    def __init__(s, p, m, r=None):
        super().__init__(m, p); r = r or C.GREEN
        s.setStyleSheet(f"background:{C.CARD2};color:{r};border:none;"
            f"border-radius:14px;padding:14px 28px;font-size:13px;font-weight:bold;border:none;")
        s.setAlignment(Qt.AlignCenter); s.adjustSize()
        s.move(p.width()//2 - s.width()//2, 20); s.show()
        s.ef = QGraphicsOpacityEffect(s); s.setGraphicsEffect(s.ef)
        a = QPropertyAnimation(s.ef, b"opacity"); a.setDuration(2800)
        a.setStartValue(1.0); a.setEndValue(0.0); a.finished.connect(s.deleteLater)
        s._a = a; QTimer.singleShot(1500, a.start)

class Halka(QWidget):
    def __init__(s, pct=0, renk=C.PRI, boy=120, kal=11):
        super().__init__(); s.pct = pct; s.renk = renk; s.kal = kal; s.setFixedSize(boy, boy)
    def paintEvent(s, e):
        p = QPainter(s); p.setRenderHint(QPainter.Antialiasing)
        k = s.kal; r = QRectF(k, k, s.width()-2*k, s.height()-2*k)
        p.setPen(QPen(QColor(C.CARD3), k, Qt.SolidLine, Qt.RoundCap)); p.drawArc(r, 0, 360*16)
        if s.pct > 0:
            g = QConicalGradient(s.width()/2, s.height()/2, 90)
            g.setColorAt(0, QColor(s.renk)); g.setColorAt(0.5, QColor(s.renk+"bb"))
            g.setColorAt(1, QColor(s.renk+"44"))
            p.setPen(QPen(QBrush(g), k, Qt.SolidLine, Qt.RoundCap))
            p.drawArc(r, 90*16, int(-s.pct/100*360*16))
        p.setPen(QPen(QColor(C.TEXT))); p.setFont(QFont("Consolas", 15, QFont.Bold))
        p.drawText(s.rect(), Qt.AlignCenter, f"%{s.pct}"); p.end()

class CubukGrafik(QWidget):
    def __init__(s, veri=None):
        super().__init__(); s.veri = veri or {}; s.setFixedHeight(170)
        s._ap = 0; s._t = QTimer(); s._t.timeout.connect(s._tk); s._t.start(20)
    def _tk(s):
        if s._ap < 100: s._ap += 3; s.update()
        else: s._t.stop()
    def paintEvent(s, e):
        if not s.veri: return
        p = QPainter(s); p.setRenderHint(QPainter.Antialiasing)
        w, h = s.width(), s.height()
        items = list(s.veri.items()); n = len(items)
        if n == 0: return
        mx = max(v for _, v in items) or 1
        bw = max(22, min(44, (w-50)//(n*2)))
        gap = max(8, min(20, (w-n*bw)//(n+1)))
        path = QPainterPath(); path.addRoundedRect(0, 0, w, h, 14, 14)
        bg = QLinearGradient(0, 0, 0, h); bg.setColorAt(0, QColor(C.CARD2)); bg.setColorAt(1, QColor(C.CARD))
        p.fillPath(path, QBrush(bg))
        p.setPen(Qt.NoPen); p.drawPath(path)
        bottom = h - 30
        # Yatay grid çizgileri
        p.setPen(QPen(QColor(C.BORDER2, ), 0.5, Qt.DashLine))
        for i in range(1, 4):
            y = bottom - int((bottom - 20) * i / 4)
            p.drawLine(15, y, w - 15, y)
        for i, (kat, sayi) in enumerate(items):
            x = gap + (bw + gap) * i
            bh = int((sayi/mx)*(bottom-25)*(min(s._ap,100)/100))
            clr = QColor(KR.get(kat, C.GOLD))
            # Gradient çubuk
            rect = QRectF(x, bottom-bh, bw, bh)
            g = QLinearGradient(x, bottom-bh, x, bottom)
            g.setColorAt(0, clr)
            g.setColorAt(1, QColor(clr.red(), clr.green(), clr.blue(), 80))
            rp = QPainterPath(); rp.addRoundedRect(rect, 6, 6)
            p.fillPath(rp, QBrush(g))
            # Üst glow
            gg = QRadialGradient(x + bw/2, bottom-bh, bw)
            gg.setColorAt(0, QColor(clr.red(), clr.green(), clr.blue(), 70))
            gg.setColorAt(1, QColor(0, 0, 0, 0))
            p.fillPath(rp, QBrush(gg))
            # Sayı
            p.setPen(QPen(clr)); p.setFont(QFont("Consolas", 10, QFont.Bold))
            p.drawText(QRect(x, bottom-bh-16, bw, 14), Qt.AlignCenter, str(sayi))
            # Etiket
            p.setPen(QPen(QColor(C.TEXT2))); p.setFont(QFont("Segoe UI", 7))
            kisa = kat[:7]+"." if len(kat) > 8 else kat
            p.drawText(QRect(x-6, bottom+4, bw+12, 18), Qt.AlignCenter, kisa)
        p.end()


# ══════════════════════════════════════════════════════════════════
#  İSTANBUL HARİTASI — Gelişmiş gerçekçi çizim
# ══════════════════════════════════════════════════════════════════
class Harita(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(300)
        self._ph = 0
        self._t = QTimer()
        self._t.timeout.connect(self._tk)
        self._t.start(50)

    def _tk(self):
        self._ph += 0.04
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        # Arka plan
        path = QPainterPath()
        path.addRoundedRect(0, 0, w, h, 18, 18)
        p.fillPath(path, QBrush(QColor(C.CARD)))
        p.setPen(Qt.NoPen); p.drawPath(path)
        p.setClipPath(path)

        # ── Grid Dokusu ──
        p.setPen(QPen(QColor(C.BORDER), 1))
        for i in range(0, w, 40): p.drawLine(i, 0, i, h)
        for i in range(0, h, 40): p.drawLine(0, i, w, i)

        # ── Deniz / Su yolları (Basit çizgiler) ──
        bos = QPainterPath()
        bos.moveTo(w * 0.45, 0)
        bos.cubicTo(w * 0.50, h * 0.3, w * 0.40, h * 0.6, w * 0.55, h)
        
        p.setPen(QPen(QColor(C.PRI), 40, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.setOpacity(0.1)
        p.drawPath(bos)
        p.setOpacity(1.0)
        
        p.setPen(QPen(QColor(C.PRI), 2, Qt.DashLine))
        p.drawPath(bos)

        # ── Yaka etiketleri ──
        p.setPen(QPen(QColor(C.TEXT3)))
        p.setFont(QFont("Segoe UI", 12, QFont.Bold))
        p.drawText(QRectF(w*0.15, h*0.50, 140, 24), Qt.AlignLeft, "AVRUPA")
        p.drawText(QRectF(w*0.75, h*0.48, 140, 24), Qt.AlignLeft, "ASYA")

        # ── Bağlantı hatları ──
        p.setPen(QPen(QColor(C.BORDER2), 2, Qt.DotLine))
        for i in range(len(YER)-1):
            x1, y1 = int(w*YER[i]["x"]), int(h*YER[i]["y"])
            x2, y2 = int(w*YER[i+1]["x"]), int(h*YER[i+1]["y"])
            p.drawLine(x1, y1, x2, y2)

        # ── Yerleşke noktaları ──
        for idx, yer in enumerate(YER):
            cx, cy = int(w*yer["x"]), int(h*yer["y"])
            clr = QColor(yer["renk"])
            pulse = 0.4 + 0.6 * math.sin(self._ph + idx * 1.2)
            
            # Glow
            r2 = 15
            alpha = int(80 * pulse)
            glow = QRadialGradient(cx, cy, r2)
            glow.setColorAt(0, QColor(clr.red(), clr.green(), clr.blue(), alpha))
            glow.setColorAt(1, QColor(0, 0, 0, 0))
            p.setBrush(QBrush(glow))
            p.setPen(Qt.NoPen)
            p.drawEllipse(cx-r2, cy-r2, r2*2, r2*2)
            
            # Nokta
            p.setBrush(QBrush(clr))
            p.setPen(QPen(QColor(C.BG), 3))
            p.drawEllipse(cx-7, cy-7, 14, 14)

        # ── Etiketler ──
        for idx, yer in enumerate(YER):
            cx, cy = int(w*yer["x"]), int(h*yer["y"])
            sag = cx < w * 0.6
            lx = cx + 24 if sag else cx - 144
            ly = cy - 20
            
            # Bağlantı çizgisi
            p.setPen(QPen(QColor(C.BORDER2), 1.5))
            if sag:
                p.drawLine(cx + 10, cy, lx, ly + 20)
            else:
                p.drawLine(cx - 10, cy, lx + 120, ly + 20)
                
            # Kutu
            box = QPainterPath()
            box.addRoundedRect(lx, ly, 120, 40, 6, 6)
            p.setBrush(QBrush(QColor(C.CARD2)))
            p.setPen(QPen(QColor(C.BORDER2), 1))
            p.drawPath(box)
            
            # Renk indikatörü
            p.setBrush(QBrush(QColor(yer["renk"])))
            p.setPen(Qt.NoPen)
            p.drawEllipse(lx + 8, ly + 16, 8, 8)
            
            # Yazılar
            p.setPen(QPen(QColor(C.TEXT)))
            p.setFont(QFont("Segoe UI", 8, QFont.Bold))
            p.drawText(lx + 22, ly + 18, yer["ad"])
            p.setPen(QPen(QColor(C.TEXT2)))
            p.setFont(QFont("Segoe UI", 7))
            p.drawText(lx + 22, ly + 32, yer["tip"])

        p.end()


# ══════════════════════════════════════════════════════════════════
#  İSTATİSTİK KARTI + CANLI SAAT
# ══════════════════════════════════════════════════════════════════
class StatK(QFrame):
    def __init__(s, baslik, deger, renk, ikon):
        super().__init__(); s._r = renk; s.setFixedHeight(118)
        s.setStyleSheet("background:transparent;border:none;")
        l = QVBoxLayout(s); l.setContentsMargins(20, 14, 20, 14); l.setSpacing(2)
        row = QHBoxLayout()
        ic = QLabel(ikon); ic.setStyleSheet(f"font-size:22px;background:{renk}15;border-radius:8px;padding:4px 8px;")
        row.addWidget(ic); row.addStretch()
        l.addLayout(row)
        tl = QLabel(baslik.upper())
        tl.setStyleSheet(f"font-size:9px;color:{C.TEXT3};font-weight:bold;letter-spacing:2px;background:transparent;")
        l.addWidget(tl)
        s.vl = QLabel("0")
        s.vl.setStyleSheet(f"font-size:36px;font-weight:bold;color:{C.TEXT};"
            f"font-family:'Consolas';background:transparent;letter-spacing:-2px;")
        l.addWidget(s.vl); s._h = deger; s._c = 0; l.addStretch()
        s._t = QTimer(); s._t.timeout.connect(s._tick); s._t.start(30)
    def _tick(s):
        if s._c < s._h:
            s._c += max(1, (s._h - s._c) // 5)
            s.vl.setText(str(min(s._c, s._h)))
        else: s._t.stop()
    def paintEvent(s, ev):
        p = QPainter(s); p.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath(); path.addRoundedRect(0, 0, s.width(), s.height(), 16, 16)
        g = QLinearGradient(0, 0, s.width(), s.height())
        g.setColorAt(0, QColor(C.CARD2)); g.setColorAt(1, QColor(C.CARD))
        p.fillPath(path, QBrush(g))
        p.setPen(Qt.NoPen); p.drawPath(path)
        # Renkli üst şerit
        bar = QPainterPath(); bar.addRoundedRect(0, 0, s.width(), 3, 1, 1)
        bg = QLinearGradient(0, 0, s.width(), 0)
        bg.setColorAt(0, QColor(s._r)); bg.setColorAt(0.6, QColor("transparent"))
        p.fillPath(bar, QBrush(bg)); p.end()

class CanliSaat(QWidget):
    def __init__(s):
        super().__init__(); s.setFixedHeight(64)
        s._t = QTimer(); s._t.timeout.connect(s.update); s._t.start(1000)
    def paintEvent(s, e):
        p = QPainter(s); p.setRenderHint(QPainter.Antialiasing)
        now = datetime.now()
        path = QPainterPath(); path.addRoundedRect(0, 0, s.width(), s.height(), 12, 12)
        p.fillPath(path, QBrush(QColor(C.CARD2)))
        p.setPen(Qt.NoPen); p.drawPath(path)
        p.setPen(QPen(QColor(C.PRI2))); p.setFont(QFont("Segoe UI", 18, QFont.Bold))
        p.drawText(QRect(12, 8, s.width(), 30), Qt.AlignLeft | Qt.AlignVCenter, now.strftime("%H:%M:%S"))
        gunler = ["Pazartesi","Salı","Çarşamba","Perşembe","Cuma","Cumartesi","Pazar"]
        p.setPen(QPen(QColor(C.TEXT3))); p.setFont(QFont("Segoe UI", 8))
        p.drawText(QRect(12, 38, s.width(), 20), Qt.AlignLeft | Qt.AlignVCenter,
            f"{now.strftime('%d.%m.%Y')} · {gunler[now.weekday()]}"); p.end()


# ── Düğme yardımcıları ──
def btn_primary(t, w=None, h=42):
    b = QPushButton(t); b.setCursor(Qt.PointingHandCursor); b.setFixedHeight(h)
    if w: b.setFixedWidth(w)
    b.setStyleSheet(f"QPushButton{{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            f"stop:0 {C.PRI},stop:1 {C.PRI2});color:#020617;border:none;border-radius:11px;"
        f"padding:0 22px;font-size:12px;font-weight:bold;}}"
            f"QPushButton:hover{{background:{C.PRI2};}}")
    return b
def btn_gold(t, w=None, h=42):
    b = QPushButton(t); b.setCursor(Qt.PointingHandCursor); b.setFixedHeight(h)
    if w: b.setFixedWidth(w)
    b.setStyleSheet(f"QPushButton{{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,"
        f"stop:0 {C.BLU},stop:1 {C.BLU2});color:#020617;border:none;border-radius:11px;"
        f"padding:0 22px;font-size:12px;font-weight:bold;}}"
        f"QPushButton:hover{{background:{C.BLU2};}}")
    return b
def btn_ghost(t):
    b = QPushButton(t); b.setCursor(Qt.PointingHandCursor); b.setFixedHeight(34)
    b.setStyleSheet(f"QPushButton{{background:{C.CARD2};color:{C.TEXT2};border:none;"
        f"border-radius:9px;padding:0 14px;font-size:11px;}}"
            f"QPushButton:hover{{color:{C.TEXT};background:{C.HOVER};}}")
    return b
def btn_danger(t):
    b = QPushButton(t); b.setCursor(Qt.PointingHandCursor); b.setFixedSize(50, 28)
    b.setStyleSheet(f"QPushButton{{background:{C.RED}15;color:{C.RED};border:none;"
        f"border-radius:7px;font-size:11px;font-weight:bold;}}"
        f"QPushButton:hover{{background:{C.RED}30;}}")
    return b
def btn_acc(t, clr=C.PRI, h=28):
    b = QPushButton(t); b.setCursor(Qt.PointingHandCursor); b.setFixedSize(60, h)
    b.setStyleSheet(f"QPushButton{{background:{clr}15;color:{clr};border:none;"
        f"border-radius:9px;font-size:11px;font-weight:bold;}}"
        f"QPushButton:hover{{background:{clr}25;}}")
    return b
def lbl_t(t, s=24):
    l = QLabel(t); l.setStyleSheet(f"font-size:{s}px;font-weight:bold;color:{C.TEXT};"); return l
def lbl_k(t):
    l = QLabel(t.upper()); l.setStyleSheet(f"font-size:9px;color:{C.PRI2};font-weight:bold;letter-spacing:3px;"); return l


# ══════════════════════════════════════════════════════════════════
#  KVT + GİRİŞ EKRANI
# ══════════════════════════════════════════════════════════════════
class KVT:
    """
    Kullanıcı veritabanı yöneticisi (giriş/üye olma için).

    ÖNEMLİ: Bu sınıf artık Veritabani ile AYNI SQLite bağlantısını paylaşır.
    Daha önce iki ayrı bağlantı açılıyordu; bu exe ortamında Windows'ta
    'database is locked' hatalarına yol açıyordu. Artık tek bağlantı kullanılır.
    """
    def __init__(s, conn_or_path):
        # Geriye uyumluluk: ister doğrudan bağlantı ister yol kabul et
        if isinstance(conn_or_path, sqlite3.Connection):
            s.c = conn_or_path
            s._kendi_baglantisi = False
        else:
            # Eski çağırım biçimi (yol verilirse) - yine de çalışsın
            s.c = sqlite3.connect(conn_or_path, check_same_thread=False, timeout=30.0)
            s.c.row_factory = sqlite3.Row
            try:
                s.c.execute("PRAGMA journal_mode=WAL")
                s.c.execute("PRAGMA busy_timeout=5000")
            except sqlite3.Error:
                pass
            s._kendi_baglantisi = True

        # Kullanıcılar tablosunu oluştur (yoksa)
        s.c.execute("CREATE TABLE IF NOT EXISTS kullanicilar(id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "ad TEXT,soyad TEXT,email TEXT UNIQUE,sifre TEXT)")
        s.c.commit()

    def h(s, p): return hashlib.sha256(p.encode()).hexdigest()

    def kayit(s, a, sy, e, p):
        try:
            s.c.execute("INSERT INTO kullanicilar(ad,soyad,email,sifre) VALUES(?,?,?,?)",
                (a, sy, e, s.h(p)))
            s.c.commit()
            return True, "OK"
        except sqlite3.IntegrityError:
            return False, "Bu e-posta zaten kayıtlı."
        except sqlite3.OperationalError as err:
            # Kilit, dosya izin hatası vb. — kullanıcıya anlamlı mesaj
            return False, f"Veritabanı meşgul veya erişilemiyor. Lütfen uygulamayı yeniden başlatın.\n\nDetay: {str(err)}"
        except Exception as err:
            return False, f"Kayıt hatası: {str(err)}"

    def giris(s, e, p):
        try:
            r = s.c.execute("SELECT * FROM kullanicilar WHERE email=? AND sifre=?",
                (e, s.h(p))).fetchone()
            if r: return True, {"id": r["id"], "ad": r["ad"], "soyad": r["soyad"], "email": r["email"]}
            return False, "E-posta veya şifre hatalı."
        except Exception as err:
            return False, f"Giriş hatası: {str(err)}"

class GirisEkrani(QWidget):
    def __init__(s, kvt, ok):
        super().__init__(); s.kvt = kvt; s.ok_cb = ok
        s.setObjectName("girisEkrani")
        s.setStyleSheet(f"QWidget#girisEkrani {{ background:qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            f"stop:0 #0f172a, stop:0.5 #1e293b, stop:1 #020617); }}")
        root = QVBoxLayout(s); root.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setFixedSize(850, 520)
        card.setStyleSheet(f"QFrame{{background:{C.BG2};border:none;border-radius:24px;}}")
        shadow = QGraphicsDropShadowEffect(s); shadow.setBlurRadius(50); shadow.setColor(QColor(0,0,0, 200)); shadow.setOffset(0, 15); card.setGraphicsEffect(shadow)

        cl = QHBoxLayout(card); cl.setContentsMargins(0,0,0,0); cl.setSpacing(0)

        # SOL - mor degrade, marka
        left = QWidget()
        left.setObjectName("girisLeft")
        left.setStyleSheet(f"QWidget#girisLeft {{ background:qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            f"stop:0 #1e293b,stop:0.5 #0f172a,stop:1 #020617);border-top-left-radius:24px;border-bottom-left-radius:24px; }}")
        ll = QVBoxLayout(left); ll.setContentsMargins(54,40,54,40); ll.setAlignment(Qt.AlignVCenter)

        d = QFrame(); d.setFixedSize(46, 3)
        d.setStyleSheet(f"background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f"stop:0 {C.PRI},stop:1 {C.BLU});border:none;border-radius:1px;")
        ll.addWidget(d); ll.addSpacing(14)

        lg = QLabel("ByTeach")
        lg.setStyleSheet(f"font-size:50px;font-weight:bold;color:{C.TEXT};letter-spacing:-2px;")
        ll.addWidget(lg)

        sb = QLabel("ÇEVRİMİÇİ ÖĞRENME PLATFORMU")
        sb.setStyleSheet(f"font-size:10px;color:{C.PRI2};letter-spacing:6px;font-weight:bold;")
        ll.addWidget(sb)
        ll.addSpacing(24)

        dc = QLabel("Canlı ders akışını, eğitmen programlarını ve öğrencileri\ntek merkezden yönetin.")
        dc.setStyleSheet(f"font-size:14px;color:{C.TEXT2};line-height:24px;")
        ll.addWidget(dc)
        ll.addSpacing(22)

        for ic, tx, clr in [
            ("✦", "Seven — doğal konuşan asistan", C.PRI),
            ("◈", "Canlı ders programları ve oturum kartları", C.GOLD),
            ("◆", "Eğitmen, öğrenci ve kontenjan yönetimi", C.BLU),
            ("❖", "Hızlı analizler ve veri sorgulama", C.CYAN)]:
            r = QHBoxLayout(); r.setSpacing(10)
            i = QLabel(ic); i.setFixedWidth(16)
            i.setStyleSheet(f"font-size:12px;color:{clr};font-weight:bold;")
            r.addWidget(i)
            t = QLabel(tx); t.setStyleSheet(f"font-size:12px;color:{C.TEXT2};")
            r.addWidget(t); r.addStretch()
            ll.addLayout(r)
        ll.addSpacing(26)
        ft = QLabel("© 2025 ByTeach · Tüm hakları saklıdır")
        ft.setStyleSheet(f"font-size:10px;color:{C.TEXT3};")
        ll.addWidget(ft)

        cl.addWidget(left, stretch=1)

        # SAĞ - form
        right = QWidget(); right.setStyleSheet("background:transparent;")
        rl = QVBoxLayout(right); rl.setAlignment(Qt.AlignCenter)
        ctn = QWidget(); ctn.setFixedWidth(360)
        s.stack = QStackedWidget()
        cl_form = QVBoxLayout(ctn); cl_form.setContentsMargins(0,0,0,0); cl_form.addWidget(s.stack)
        s.stack.addWidget(s._lf()); s.stack.addWidget(s._rf())
        rl.addWidget(ctn, alignment=Qt.AlignCenter)
        cl.addWidget(right, stretch=1)

        root.addWidget(card)

    def _lf(s):
        w = QWidget(); l = QVBoxLayout(w); l.setSpacing(12); l.setAlignment(Qt.AlignTop)
        l.addSpacing(10); l.addWidget(lbl_k("Hoş geldiniz")); l.addWidget(lbl_t("Giriş Yapın", 32))
        l.addSpacing(16)
        for attr, ph, lb, ec in [("ge","ornek@mail.com","E-POSTA",0),("gs","••••••••","ŞİFRE",1)]:
            fl = QLabel(lb); fl.setStyleSheet(f"font-size:9px;color:{C.TEXT3};font-weight:bold;letter-spacing:1px;"); l.addWidget(fl)
            inp = QLineEdit(); inp.setPlaceholderText(ph); inp.setFixedHeight(44)
            inp.setStyleSheet(f"QLineEdit{{background:{C.CARD};color:{C.TEXT};border:1px solid {C.BORDER};border-radius:11px;padding:0 14px;font-size:12px;}}QLineEdit:focus{{border:1px solid {C.PRI};}}")
            if ec: inp.setEchoMode(QLineEdit.Password)
            setattr(s, attr, inp); l.addWidget(inp)
        s.ge.returnPressed.connect(s._dl)
        s.gs.returnPressed.connect(s._dl)
        l.addSpacing(8); bg = btn_primary("Giriş Yap →"); bg.clicked.connect(s._dl); l.addWidget(bg)
        s.gm = QLabel(""); s.gm.setStyleSheet(f"font-size:11px;color:{C.RED};"); s.gm.setWordWrap(True); l.addWidget(s.gm)
        l.addSpacing(16)
        sep = QFrame(); sep.setFixedHeight(1); sep.setStyleSheet(f"background:transparent;"); l.addWidget(sep)
        l.addSpacing(10)
        sw = QPushButton("Hesabınız yok mu? Üye olun →"); sw.setCursor(Qt.PointingHandCursor)
        sw.setStyleSheet(f"QPushButton{{background:none;border:none;color:{C.PRI};font-size:12px;text-align:center;font-weight:bold;}}")
        sw.clicked.connect(lambda: [s.stack.setCurrentIndex(1), s.gm.clear(), s.rm.clear()]); l.addWidget(sw)
        l.addStretch(); return w

    def _rf(s):
        w = QWidget(); l = QVBoxLayout(w); l.setSpacing(10); l.setAlignment(Qt.AlignTop)
        l.addSpacing(10); l.addWidget(lbl_k("Yeni hesap")); l.addWidget(lbl_t("Üye Olun", 32))
        l.addSpacing(8)
        for attr, ph, lb, ec in [("ra","Adınız","AD",0),("rs","Soyadınız","SOYAD",0),
            ("re","ornek@mail.com","E-POSTA",0),("rp","En az 4 karakter","ŞİFRE",1)]:
            fl = QLabel(lb); fl.setStyleSheet(f"font-size:9px;color:{C.TEXT3};font-weight:bold;letter-spacing:1px;"); l.addWidget(fl)
            inp = QLineEdit(); inp.setPlaceholderText(ph); inp.setFixedHeight(42)
            inp.setStyleSheet(f"QLineEdit{{background:{C.CARD};color:{C.TEXT};border:1px solid {C.BORDER};border-radius:11px;padding:0 14px;font-size:12px;}}QLineEdit:focus{{border:1px solid {C.PRI};}}")
            if ec: inp.setEchoMode(QLineEdit.Password)
            setattr(s, attr, inp); l.addWidget(inp)
        s.re.returnPressed.connect(s._dr)
        s.rp.returnPressed.connect(s._dr)
        l.addSpacing(6); br = btn_primary("Üye Ol →"); br.clicked.connect(s._dr); l.addWidget(br)
        s.rm = QLabel(""); s.rm.setStyleSheet("font-size:11px;"); s.rm.setWordWrap(True); l.addWidget(s.rm)
        l.addSpacing(10)
        sep = QFrame(); sep.setFixedHeight(1); sep.setStyleSheet(f"background:transparent;"); l.addWidget(sep)
        l.addSpacing(6)
        sw = QPushButton("← Giriş sayfasına dön"); sw.setCursor(Qt.PointingHandCursor)
        sw.setStyleSheet(f"QPushButton{{background:none;border:none;color:{C.PRI};font-size:12px;font-weight:bold;}}")
        sw.clicked.connect(lambda: [s.stack.setCurrentIndex(0), s.rm.clear(), s.gm.clear()]); l.addWidget(sw)
        l.addStretch(); return w

    def _dl(s):
        e, p = s.ge.text().strip(), s.gs.text().strip()
        if not e or not p: s.gm.setText("Tüm alanları doldurun."); return
        ok, r = s.kvt.giris(e, p)
        if ok: s.ok_cb(r)
        else: s.gm.setText(r)

    def _dr(s):
        a,sy,e,p = s.ra.text().strip(),s.rs.text().strip(),s.re.text().strip(),s.rp.text().strip()
        if not all([a,sy,e,p]):
            s.rm.setText("Lütfen tüm alanları doldurun."); s.rm.setStyleSheet(f"font-size:11px;color:{C.RED};"); return
        if "@" not in e or "." not in e:
            s.rm.setText("Geçerli bir e-posta adresi girin."); s.rm.setStyleSheet(f"font-size:11px;color:{C.RED};"); return
        if len(p) < 4:
            s.rm.setText("Şifreniz en az 4 karakter olmalıdır."); s.rm.setStyleSheet(f"font-size:11px;color:{C.RED};"); return
        ok, msg = s.kvt.kayit(a, sy, e, p)
        if ok:
            s.rm.setText("✓ Kayıt başarılı! Giriş ekranına yönlendiriliyorsunuz..."); s.rm.setStyleSheet(f"font-size:11px;color:{C.GREEN};")
            s.ge.setText(e)
            s.gs.clear()
            s.ra.clear(); s.rs.clear(); s.re.clear(); s.rp.clear()
            QTimer.singleShot(1500, lambda: [s.stack.setCurrentIndex(0), s.rm.clear()])
        else: s.rm.setText(msg); s.rm.setStyleSheet(f"font-size:11px;color:{C.RED};")


# ══════════════════════════════════════════════════════════════════
#  SEVEN YZ PANELİ
# ══════════════════════════════════════════════════════════════════
class Seven(QWidget):
    KB = [
        (["kurs ekle","yeni kurs"],"📚 Kurslar → + Yeni Kurs → Formu doldurun!"),
        (["ders saati","ders programı","canlı ders"],"Kurs detayında gün, saat ve yayın platformunu görebilirsiniz."),
        (["kurs sil"],"Tablodaki Sil düğmesiyle silebilirsiniz."),
        (["kurs detay","kayıtlı öğrenci"],"Detay düğmesiyle öğrenci listesini görebilirsiniz."),
        (["eğitmen ekle","yeni eğitmen"],"🎓 Eğitmenler → + Yeni Eğitmen"),
        (["eğitmen sil"],"⚠️ Aktif kursu olan eğitmen silinemez!"),
        (["eğitmen","hoca"],"Eğitmenler sekmesinde kadroyu yönetin."),
        (["öğrenci"],"Öğrenci detayında profil ve kayıtlı kurslar."),
        (["kayıt"],"Kurs detayından Öğrenci Kaydet ile ekleyin."),
        (["kontenjan","dolu"],"Yeşil=müsait, kırmızı=dolu."),
        (["istatistik","dashboard"],"Kontrol Paneli'nde kartlar, grafikler ve harita."),
        (["veritabanı","sqlite"],"5 tablo: egitmenler, kurslar, ogrenciler, kayitlar, kullanicilar."),
        (["csv","dışa aktar"],"📁 Her sayfada CSV Aktar düğmesi var."),
        (["harita","yerleşke","istanbul","boğaz"],"🗺️ Dashboard'da İstanbul haritası — Boğaz, yakalar."),
        (["merhaba","selam","hey"],"Merhaba, buradayım. İsterseniz ders programlarını, eğitmenleri ya da platform durumunu birlikte kontrol edelim."),
        (["teşekkür","sağol"],"Memnun oldum, başka bir şey gerekirse hemen devam edebiliriz."),
        (["seven","kimsin"],"Ben Seven. Platform içindeki kursları, eğitmenleri ve canlı ders akışını takip etmenize yardımcı oluyorum."),
        (["ne yapabilirsin","yardım"],"Kurs planlama, ders saatleri, öğrenci kayıtları, doluluk ve hızlı özetler konusunda destek olabilirim."),
    ]

    def __init__(s, vtn=None):
        super().__init__(); s.vtn = vtn; s.setFixedSize(320, 520)
        s.setAttribute(Qt.WA_StyledBackground, True)
        s.setObjectName("sevenPanel")
        s.setStyleSheet(f"QWidget#sevenPanel {{ background-color:{C.CARD}; border:1px solid {C.BORDER2}; border-radius:18px; }}")
        
        eff = QGraphicsDropShadowEffect(s)
        eff.setBlurRadius(40); eff.setOffset(0, 10); eff.setColor(QColor(0,0,0, 180))
        s.setGraphicsEffect(eff)
        
        lay = QVBoxLayout(s); lay.setContentsMargins(0, 0, 0, 0); lay.setSpacing(0)

        # Header
        hdr = QWidget(); hdr.setFixedHeight(70)
        hdr.setStyleSheet(f"background:transparent;border:none;border-bottom:1px solid {C.BORDER};")
        hl = QHBoxLayout(hdr); hl.setContentsMargins(20, 0, 20, 0); hl.setSpacing(12)
        
        av = QLabel("✦"); av.setFixedSize(36,36); av.setAlignment(Qt.AlignCenter)
        av.setStyleSheet(f"font-size:18px;color:{C.TEXT};"
            f"background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 {C.PRI},stop:1 {C.BLU});"
            f"border-radius:12px;border:none;font-weight:bold;")
        hl.addWidget(av)
        
        info = QVBoxLayout(); info.setSpacing(2); info.setAlignment(Qt.AlignVCenter)
        nm = QLabel("Seven"); nm.setStyleSheet(f"font-size:15px;font-weight:bold;color:{C.TEXT};border:none;")
        info.addWidget(nm)
        st = QLabel("● Çevrimiçi"); st.setStyleSheet(f"font-size:10px;color:{C.GREEN};font-weight:bold;border:none;")
        info.addWidget(st)
        hl.addLayout(info); hl.addStretch()
        lay.addWidget(hdr)

        # Chat Area
        s._tt = None; s._td = 0
        s.chat = QTextEdit(); s.chat.setReadOnly(True)
        s.chat.setStyleSheet(f"""
            QTextEdit {{ background:transparent; color:{C.TEXT}; border:none; padding:10px 16px; font-size:12px; }}
            QScrollBar:vertical {{ background:transparent; width:4px; }}
            QScrollBar::handle:vertical {{ background:{C.BORDER2}; border-radius:2px; }}
        """)
        s._sm("Merhaba, ben Seven. Kurs, eğitmen veya doluluk oranlarıyla ilgili her türlü veriyi benimle analiz edebilirsiniz.")
        lay.addWidget(s.chat)

        # Quick Actions
        qw = QWidget(); qw.setFixedHeight(46)
        qw.setStyleSheet("background:transparent;border:none;")
        ql = QHBoxLayout(qw); ql.setContentsMargins(16,0,16,0); ql.setSpacing(6)
        for q in ["Dersler", "Özet", "Eğitmen"]:
            qb = QPushButton(q); qb.setCursor(Qt.PointingHandCursor); qb.setFixedHeight(30)
            qb.setStyleSheet(f"QPushButton{{background:{C.CARD2};color:{C.TEXT2};border:none;"
                f"border-radius:15px;padding:0 12px;font-size:11px;font-weight:bold;}}"
                f"QPushButton:hover{{background:{C.HOVER};color:{C.TEXT};}}")
            qb.clicked.connect(lambda ev, t=q: s._qk(t)); ql.addWidget(qb)
        lay.addWidget(qw)

        # Input Area
        iw = QWidget(); iw.setFixedHeight(70)
        iw.setStyleSheet(f"background:transparent;border:none;border-top:1px solid {C.BORDER};")
        il = QHBoxLayout(iw); il.setContentsMargins(16, 15, 16, 15); il.setSpacing(8)
        
        s.inp = QLineEdit(); s.inp.setPlaceholderText("Bana bir şey sorun...")
        s.inp.setFixedHeight(40)
        s.inp.setStyleSheet(f"QLineEdit{{background:{C.CARD};border:1px solid {C.BORDER};"
            f"border-radius:20px;padding:0 16px;color:{C.TEXT};font-size:12px;}}"
            f"QLineEdit:focus{{border:1px solid {C.PRI};}}")
        s.inp.returnPressed.connect(s._send); il.addWidget(s.inp)
        
        sb = QPushButton("↑"); sb.setCursor(Qt.PointingHandCursor); sb.setFixedSize(40, 40)
        sb.setStyleSheet(f"QPushButton{{background:{C.PRI};color:white;border:none;"
            f"border-radius:20px;font-size:16px;font-weight:bold;}}"
            f"QPushButton:hover{{background:{C.PRI2};}}")
        sb.clicked.connect(s._send); il.addWidget(sb)
        lay.addWidget(iw)

    def _qk(s, t): s.inp.setText(t); s._send()
    def _sm(s, h):
        cur = s.chat.toHtml()
        cur += (f'<div style="margin-top:14px;">'
            f'<div style="background:{C.CARD};border:1px solid {C.BORDER};border-radius:0 14px 14px 14px;'
            f'padding:12px 16px;color:{C.TEXT2};font-size:12px;line-height:18px;">{h}</div></div>')
        s.chat.setHtml(cur); s.chat.verticalScrollBar().setValue(s.chat.verticalScrollBar().maximum())
    def _um(s, t):
        cur = s.chat.toHtml()
        cur += (f'<div style="margin-top:14px;text-align:right;">'
            f'<span style="background:{C.PRI};padding:10px 16px;border-radius:14px 14px 0 14px;'
            f'color:white;font-size:12px;display:inline-block;">{t}</span></div>')
        s.chat.setHtml(cur)
    def _send(s):
        q = s.inp.text().strip()
        if not q: return
        s._um(q); s.inp.clear(); ans = s._find(q)
        s._td = 0; s._tt = QTimer(); s._tt.timeout.connect(s._typing); s._tt.start(180)
        QTimer.singleShot(random.randint(350, 700), lambda: s._show(ans))
    def _typing(s):
        s._td = (s._td + 1) % 4
        d = "●" * (s._td + 1) + "○" * (3 - s._td)
        cur = s.chat.toHtml()
        if "svtp" in cur:
            idx = cur.rfind('<div id="svtp"'); cur = cur[:idx] if idx >= 0 else cur
        cur += f'<div id="svtp" style="margin-top:8px;"><span style="color:{C.PRI};font-size:12px;">{d}</span></div>'
        s.chat.setHtml(cur); s.chat.verticalScrollBar().setValue(s.chat.verticalScrollBar().maximum())
    def _show(s, ans):
        if s._tt: s._tt.stop(); s._tt = None
        cur = s.chat.toHtml()
        if "svtp" in cur:
            idx = cur.rfind('<div id="svtp"'); cur = cur[:idx] if idx >= 0 else cur
            s.chat.setHtml(cur)
        s._sm(ans)
    def _find(s, q):
        ql = q.lower()
        if s.vtn:
            st = s.vtn["istatistik"].genel_istatistikler()
            if any(w in ql for w in ["kaç kurs","kurs sayı"]):
                return f"Şu anda platformda <b>{st['toplam_kurs']}</b> aktif kurs görünüyor."
            if any(w in ql for w in ["kaç eğitmen"]):
                return f"Eğitmen kadrosunda toplam <b>{st['toplam_egitmen']}</b> kişi yer alıyor."
            if any(w in ql for w in ["kaç öğrenci"]):
                return f"Sistemde kayıtlı <b>{st['toplam_ogrenci']}</b> öğrenci bulunuyor."
            if any(w in ql for w in ["popüler","en çok"]):
                ks = s.vtn["kurs"].listele()
                if ks:
                    en = max(ks, key=lambda k: k["kayitli_ogrenci_sayisi"])
                    return f"En yoğun kurs şu an <b>{en['kurs_adi']}</b>. Doluluk <b>{en['kayitli_ogrenci_sayisi']}/{en['kontenjan']}</b> seviyesinde."
            if any(w in ql for w in ["bugünkü ders","yaklaşan ders","canlı ders","ders program"]):
                dersler = yaklasan_dersler(s.vtn["kurs"].listele(), 3)
                if dersler:
                    satirlar = [
                        f"• <b>{k['kurs_adi']}</b> — {ders_programi_yazisi(k)}"
                        for k in dersler
                    ]
                    return "Yaklaşan ders akışından öne çıkanlar:<br>" + "<br>".join(satirlar)
            if any(w in ql for w in ["doluluk","oran"]):
                ks = s.vtn["kurs"].listele()
                if ks:
                    tk = sum(k["kontenjan"] for k in ks); ty = sum(k["kayitli_ogrenci_sayisi"] for k in ks)
                    return f"Genel doluluk oranı şu anda <b>%{round(ty/max(tk,1)*100)}</b>."
        bs, ba = 0, None
        for keys, ans in s.KB:
            for key in keys:
                if key in ql and len(key) > bs: bs = len(key); ba = ans
        return ba or "İsterseniz kurslar, eğitmenler, ders programı ya da doluluk hakkında soru sorabilirsiniz."


# ══════════════════════════════════════════════════════════════════
#  SOL MENÜ
# ══════════════════════════════════════════════════════════════════
class SolMenu(QWidget):
    def __init__(s, cb, u, lo):
        super().__init__(); s.cb = cb; s.u = u; s.lo = lo; s.act = 0; s.btns = []
        s.setFixedWidth(230)
        s.setObjectName("solMenu")
        s.setStyleSheet(f"QWidget#solMenu {{ background:{C.BG2};border:none; }}")
        l = QVBoxLayout(s); l.setContentsMargins(14,18,14,14); l.setSpacing(3)

        # Logo
        logo = QLabel("ByTeach")
        logo.setStyleSheet(f"font-size:24px;font-weight:bold;color:{C.TEXT};padding-left:4px;letter-spacing:-1px;")
        l.addWidget(logo)
        subt = QLabel("ÖĞRENME PLATFORMU")
        subt.setStyleSheet(f"font-size:7px;color:{C.PRI2};letter-spacing:4px;font-weight:bold;padding-left:4px;")
        l.addWidget(subt)
        l.addSpacing(14)
        l.addWidget(CanliSaat()); l.addSpacing(16)

        for t, i in [("◆  Kontrol Paneli",0),("◈  Kurslar",1),("❖  Eğitmenler",2),("✧  Öğrenciler",3),("🗺️  Harita",4)]:
            b = QPushButton(t); b.setCursor(Qt.PointingHandCursor); b.setFixedHeight(40)
            b.clicked.connect(lambda c, idx=i: s._s(idx)); s.btns.append(b); l.addWidget(b)
        s._st(); l.addStretch()

        # Kullanıcı kartı
        uf = QFrame(); uf.setStyleSheet(f"QFrame{{background:{C.CARD};border:none;border-radius:11px;}}")
        ul = QVBoxLayout(uf); ul.setContentsMargins(12,10,12,10); ul.setSpacing(2)
        un = QLabel(f"● {s.u['ad']} {s.u['soyad']}"); un.setStyleSheet(f"font-size:12px;color:{C.GREEN};font-weight:bold;border:none;"); ul.addWidget(un)
        ue = QLabel(s.u['email']); ue.setStyleSheet(f"font-size:9px;color:{C.TEXT3};border:none;"); ul.addWidget(ue)
        l.addWidget(uf); l.addSpacing(8)
        bo = btn_ghost("Çıkış Yap"); bo.clicked.connect(s.lo); l.addWidget(bo)

    def _s(s, i): s.act = i; s._st(); s.cb(i)
    def _st(s):
        for i, b in enumerate(s.btns):
            act = i == s.act
            if act:
                b.setStyleSheet(f"QPushButton{{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
                    f"stop:0 {C.PRI}25,stop:1 transparent);"
                    f"color:{C.TEXT};border:none;border-left:3px solid {C.PRI};"
                    f"border-radius:10px;text-align:left;padding-left:14px;font-size:12px;font-weight:bold;}}")
            else:
                b.setStyleSheet(f"QPushButton{{background:transparent;color:{C.TEXT2};"
                    f"border:none;border-radius:10px;text-align:left;padding-left:16px;"
                    f"font-size:12px;font-weight:normal;}}"
                    f"QPushButton:hover{{background:{C.CARD};color:{C.TEXT};}}")


# ══════════════════════════════════════════════════════════════════
#  HAFTALIK TAKVİM BİLEŞENİ
# ══════════════════════════════════════════════════════════════════
class HaftalikTakvim(QWidget):
    def __init__(s, kurslar):
        super().__init__(); s.setMinimumHeight(170)
        l = QHBoxLayout(s); l.setContentsMargins(0,0,0,0); l.setSpacing(8)
        
        prg = {g: [] for g in GUN_SIRASI}
        for k in kurslar:
            g = k.get("gun")
            if g in prg: prg[g].append(k)
        for g in prg: prg[g].sort(key=lambda k: k.get("baslangic_saati") or "99:99")
        
        bugun = datetime.now().weekday()
        for i, gun in enumerate(GUN_SIRASI):
            col = QFrame()
            ib = (i == bugun)
            bc = f"{C.PRI}15" if ib else f"{C.CARD2}"
            oc = C.PRI if ib else C.BORDER
            col.setStyleSheet(f"QFrame{{background:{bc};border:none;border-radius:8px;}}")
            cl = QVBoxLayout(col); cl.setContentsMargins(8,8,8,8); cl.setSpacing(6)
            
            hdr = QLabel(gun.upper()); hdr.setAlignment(Qt.AlignCenter)
            hdr.setStyleSheet(f"font-size:10px;font-weight:bold;color:{C.TEXT if ib else C.TEXT2};border:none;background:transparent;")
            cl.addWidget(hdr)
            sep = QFrame(); sep.setFixedHeight(1)
            sep.setStyleSheet(f"background:transparent;border:none;")
            cl.addWidget(sep)
            
            scr = QScrollArea(); scr.setWidgetResizable(True)
            scr.setStyleSheet("QScrollArea{border:none;background:transparent;}")
            scw = QWidget(); scw.setStyleSheet("background:transparent;")
            sl = QVBoxLayout(scw); sl.setContentsMargins(0,0,0,0); sl.setSpacing(4)
            
            for k in prg[gun]:
                kf = QFrame()
                clr = KR.get(k.get("kategori"), C.PRI)
                kf.setStyleSheet(f"QFrame{{background:{clr}15;border:none;border-radius:4px;}}")
                kfl = QVBoxLayout(kf); kfl.setContentsMargins(6,4,6,4); kfl.setSpacing(2)
                kt = QLabel(k["kurs_adi"])
                kt.setStyleSheet(f"font-size:10px;font-weight:bold;color:{C.TEXT};border:none;background:transparent;")
                kt.setWordWrap(True); kfl.addWidget(kt)
                saat = k.get("baslangic_saati", "")
                if saat:
                    st = QLabel(saat)
                    st.setStyleSheet(f"font-size:9px;color:{clr};font-weight:bold;border:none;background:transparent;")
                    kfl.addWidget(st)
                sl.addWidget(kf)
                
            sl.addStretch(); scr.setWidget(scw); cl.addWidget(scr)
            l.addWidget(col)


# ══════════════════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════════════════
class Dashboard(QScrollArea):
    def __init__(s, vt, user, nav_cb=None):
        super().__init__(); s.vt = vt; s.user = user; s.nav_cb = nav_cb
        s.setWidgetResizable(True); s.setStyleSheet(f"QScrollArea{{background:{C.BG};border:none;}}")
        w = QWidget(); l = QVBoxLayout(w); l.setContentsMargins(30,30,30,30); l.setSpacing(20)

        # Hoş geldin kartı - sade temiz tasarım
        wf = QFrame()
        wf.setStyleSheet(f"QFrame{{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f"stop:0 {C.CARD2},stop:1 {C.CARD});border:none;border-radius:20px;}}")
        eff = QGraphicsDropShadowEffect(s); eff.setBlurRadius(30); eff.setColor(QColor(0,0,0, 100)); eff.setOffset(0,8); wf.setGraphicsEffect(eff)
        wl = QHBoxLayout(wf); wl.setContentsMargins(30,24,30,24)
        # Sol çubuk (mor vurgu)
        accent = QFrame()
        accent.setFixedWidth(4)
        accent.setStyleSheet(f"background:qlineargradient(x1:0,y1:0,x2:0,y2:1,"
            f"stop:0 {C.PRI},stop:1 {C.BLU});border-radius:2px;")
        wl.addWidget(accent)
        wi = QVBoxLayout(); wi.setSpacing(4); wi.setContentsMargins(14,0,0,0)
        h = datetime.now().hour
        sel = "Günaydın" if h < 12 else ("İyi günler" if h < 18 else "İyi akşamlar")
        wi.addWidget(lbl_k("Kontrol Paneli"))
        wt = lbl_t(f"{sel}, {s.user['ad']}! 👋", 24)
        wt.setStyleSheet(wt.styleSheet()+"border:none;background:transparent;"); wi.addWidget(wt)
        wd = QLabel("Platformun güncel durumunu takip edin.")
        wd.setStyleSheet(f"font-size:12px;color:{C.TEXT2};border:none;background:transparent;"); wi.addWidget(wd)
        wl.addLayout(wi); wl.addStretch()
        l.addWidget(wf)

        # İstatistik kartları
        st = s.vt["istatistik"].genel_istatistikler()
        ks = s.vt["kurs"].listele()
        canli_sayisi = sum(1 for k in ks if "canl" in (k.get("format") or "").lower())
        row = QHBoxLayout(); row.setSpacing(12)
        for baslik, deger, renk, ikon in [
            ("Kurs", st["toplam_kurs"], C.GOLD, "📚"),
            ("Eğitmen", st["toplam_egitmen"], C.BLU, "🎓"),
            ("Öğrenci", st["toplam_ogrenci"], C.YELLOW, "👤"),
            ("Canlı Ders", canli_sayisi, C.GREEN, "🟢"),
            ("Kayıt", st["toplam_kayit"], C.PRI, "📋"),
        ]:
            row.addWidget(StatK(baslik, deger, renk, ikon))
        l.addLayout(row)

        # Harita taşındı

        # Alt kısım
        alt = QHBoxLayout(); alt.setSpacing(14)

        # Halka
        hf = QFrame()
        hf.setStyleSheet(f"QFrame{{background:{C.CARD};border:none;border-radius:14px;}}")
        hl = QHBoxLayout(hf); hl.setContentsMargins(22,18,22,18); hl.setSpacing(16)
        tk = sum(k["kontenjan"] for k in ks) if ks else 1
        ty = sum(k["kayitli_ogrenci_sayisi"] for k in ks)
        pct = round(ty/max(tk,1)*100)
        hl.addWidget(Halka(pct, C.PRI if pct < 70 else (C.GOLD if pct < 90 else C.RED)))
        hi = QVBoxLayout()
        hi.addWidget(lbl_k("Doluluk"))
        ht = lbl_t(f"%{pct}", 24); ht.setStyleSheet(ht.styleSheet()+"border:none;"); hi.addWidget(ht)
        hd = QLabel(f"{ty}/{tk} kontenjan")
        hd.setStyleSheet(f"font-size:11px;color:{C.TEXT2};border:none;"); hi.addWidget(hd)
        hi.addStretch(); hl.addLayout(hi)
        alt.addWidget(hf, stretch=1)

        # Çubuk grafik
        cf = QFrame()
        cf.setStyleSheet(f"QFrame{{background:{C.CARD};border:none;border-radius:14px;}}")
        cll = QVBoxLayout(cf); cll.setContentsMargins(16,14,16,14)
        cll.addWidget(lbl_k("Kategori Dağılımı")); cll.addSpacing(4)
        cll.addWidget(CubukGrafik(st.get("kategori_dagilimi", {})))
        alt.addWidget(cf, stretch=2)

        # Hızlı + Aktivite
        qf = QFrame()
        qf.setStyleSheet(f"QFrame{{background:{C.CARD};border:none;border-radius:14px;}}")
        ql = QVBoxLayout(qf); ql.setContentsMargins(16,12,16,12); ql.setSpacing(5)
        ql.addWidget(lbl_k("Hızlı İşlemler"))
        btn_row = QHBoxLayout(); btn_row.setSpacing(8)
        for txt, clr, idx in [("+ Kurs",C.GOLD,1),("+ Eğitmen",C.GREEN,2),("+ Öğrenci",C.YELLOW,3)]:
            qb = btn_acc(txt, clr, 30)
            qb.setFixedWidth(70)
            if s.nav_cb: qb.clicked.connect(lambda c, i=idx: s.nav_cb(i))
            btn_row.addWidget(qb)
        btn_row.addStretch()
        ql.addLayout(btn_row)
        ql.addSpacing(6); ql.addWidget(lbl_k("Son Aktiviteler"))
        for ak in LOG[:4]:
            ar = QHBoxLayout()
            at = QLabel(ak["t"]); at.setStyleSheet(f"font-size:9px;color:{C.TEXT3};border:none;font-family:'Consolas';"); at.setFixedWidth(32); ar.addWidget(at)
            am = QLabel(ak["m"]); am.setStyleSheet(f"font-size:10px;color:{ak['r']};border:none;"); am.setWordWrap(True); ar.addWidget(am)
            ql.addLayout(ar)
        if not LOG:
            na = QLabel("Henüz aktivite yok"); na.setStyleSheet(f"font-size:10px;color:{C.TEXT3};border:none;"); ql.addWidget(na)
        ql.addStretch()
        alt.addWidget(qf, stretch=1)
        l.addLayout(alt)

        # Alt kısım 2: Haftalık Takvim
        tf = QFrame()
        tf.setStyleSheet(f"QFrame{{background:{C.CARD};border:none;border-radius:14px;}}")
        tl = QVBoxLayout(tf); tl.setContentsMargins(16,14,16,14); tl.setSpacing(8)
        tl.addWidget(lbl_k("Haftalık Ders Programı"))
        tl.addWidget(HaftalikTakvim(ks))
        l.addWidget(tf)

        l.addStretch()
        s.setWidget(w)


# ══════════════════════════════════════════════════════════════════
#  KURSLAR + EĞİTMENLER + ÖĞRENCİLER
# ══════════════════════════════════════════════════════════════════
class KurslarP(QWidget):
    def __init__(s, vt, pw=None):
        super().__init__(); s.vt = vt; s.pw = pw
        s.stk = QStackedWidget(); lay = QVBoxLayout(s); lay.setContentsMargins(0,0,0,0); lay.addWidget(s.stk)
        s.lw = QWidget(); s._bl(); s.stk.addWidget(s.lw)
    def _bl(s):
        l = QVBoxLayout(s.lw); l.setContentsMargins(26,22,26,22); l.setSpacing(12)
        top = QHBoxLayout(); left = QVBoxLayout()
        left.addWidget(lbl_k("Kurs Portföyü")); left.addWidget(lbl_t("Kurs Yönetimi"))
        top.addLayout(left); top.addStretch()
        bc = btn_ghost("📁 CSV Aktar"); bc.clicked.connect(s._csv); top.addWidget(bc, alignment=Qt.AlignBottom)
        ba = btn_primary("+ Yeni Kurs"); ba.clicked.connect(s._add); top.addWidget(ba, alignment=Qt.AlignBottom)
        l.addLayout(top)
        s.search = QLineEdit(); s.search.setPlaceholderText("🔍 Kurs, eğitmen veya kategori ara...")
        s.search.setFixedHeight(42); s.search.textChanged.connect(s.refresh); l.addWidget(s.search)
        s.table = QTableWidget(); s.table.setColumnCount(7)
        s.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        s.table.setHorizontalHeaderLabels(["Kurs Adı","Eğitmen","Program","Yayın","Seviye","Doluluk","İşlemler"])
        s.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for c in range(1, 7): s.table.horizontalHeader().setSectionResizeMode(c, QHeaderView.ResizeToContents)
        s.table.verticalHeader().setVisible(False); s.table.setShowGrid(False)
        l.addWidget(s.table); s.refresh()
    def refresh(s):
        q = s.search.text().lower() if hasattr(s,'search') else ""
        data = s.vt["kurs"].listele()
        if q:
            data = [k for k in data if any(
                q in str(deger).lower()
                for deger in [
                    k["kurs_adi"], k.get("egitmen_adi",""), k["kategori"], k["seviye"],
                    k.get("gun",""), k.get("platform",""), k.get("format","")
                ]
            )]
        s.table.setRowCount(len(data))
        for i, k in enumerate(data):
            s.table.setItem(i,0,QTableWidgetItem(k["kurs_adi"]))
            s.table.setItem(i,1,QTableWidgetItem(k.get("egitmen_adi","—")))
            s.table.setItem(i,2,QTableWidgetItem(ders_programi_yazisi(k)))
            s.table.setItem(i,3,QTableWidgetItem(ders_platform_yazisi(k)))
            s.table.setItem(i,4,QTableWidgetItem(f"{k['kategori']} / {k['seviye']}"))
            
            pct = 0 if k['kontenjan'] == 0 else int(k['kayitli_ogrenci_sayisi'] / k['kontenjan'] * 100)
            clr = C.GREEN if pct < 70 else (C.YELLOW if pct < 90 else C.RED)
            pb = QProgressBar(); pb.setFixedHeight(6); pb.setTextVisible(False); pb.setValue(pct)
            pb.setStyleSheet(f"QProgressBar{{background:{C.CARD3};border:none;border-radius:3px;}}QProgressBar::chunk{{background:{clr};border-radius:3px;}}")
            pw = QWidget(); pl = QVBoxLayout(pw); pl.setContentsMargins(6,4,6,4); pl.setSpacing(4)
            pt = QLabel(f"{k['kayitli_ogrenci_sayisi']} / {k['kontenjan']}"); pt.setStyleSheet(f"font-size:10px;color:{C.TEXT2};")
            pl.addWidget(pt, alignment=Qt.AlignCenter); pl.addWidget(pb)
            s.table.setCellWidget(i,5,pw)
            
            actions = QWidget(); al = QHBoxLayout(actions); al.setContentsMargins(4,0,4,0); al.setSpacing(8)
            bd2 = btn_acc("Detay", C.PRI, 28); bd2.clicked.connect(lambda c,kid=k["kurs_id"]: s._det(kid)); al.addWidget(bd2)
            bd = btn_danger("Sil"); bd.clicked.connect(lambda c,kid=k["kurs_id"]: s._del(kid)); al.addWidget(bd)
            s.table.setCellWidget(i,6,actions)
            s.table.setRowHeight(i, 48)
    def _csv(s):
        data = s.vt["kurs"].listele()
        rows = [[
            k["kurs_adi"], k.get("egitmen_adi",""), ders_programi_yazisi(k),
            ders_platform_yazisi(k), k["kategori"], k["seviye"],
            f"{k['kayitli_ogrenci_sayisi']}/{k['kontenjan']}"
        ] for k in data]
        try:
            with open("kurslar.csv",'w',newline='',encoding='utf-8-sig') as f:
                w=csv.writer(f);w.writerow(["Kurs","Eğitmen","Program","Yayın","Kategori","Seviye","Kontenjan"]);[w.writerow(r) for r in rows]
            if s.pw: Toast(s.pw,"✓ CSV aktarıldı",C.GREEN)
        except: pass
    def _det(s, kid):
        k = s.vt["kurs"].getir(kid)
        if not k: return
        if s.stk.count() > 1: old = s.stk.widget(1); s.stk.removeWidget(old); old.deleteLater()
        dw = QScrollArea(); dw.setWidgetResizable(True); dw.setStyleSheet(f"QScrollArea{{background:{C.BG};border:none;}}")
        ct = QWidget(); dl = QVBoxLayout(ct); dl.setContentsMargins(26,22,26,22); dl.setSpacing(12)
        back = btn_ghost("← Kurslara dön"); back.clicked.connect(lambda: s.stk.setCurrentIndex(0)); dl.addWidget(back, alignment=Qt.AlignLeft)
        kf = QFrame(); kf.setStyleSheet(f"QFrame{{background:{C.CARD};border:none;border-radius:14px;}}")
        kfl = QVBoxLayout(kf); kfl.setContentsMargins(22,18,22,18)
        kfl.addWidget(lbl_k("Kurs Detayı"))
        kt = lbl_t(k["kurs_adi"], 24); kt.setStyleSheet(kt.styleSheet()+"border:none;"); kfl.addWidget(kt)
        kd = QLabel(f"{k.get('aciklama','')} • {k.get('egitmen_adi','—')} • {k['kategori']}/{k['seviye']}")
        kd.setStyleSheet(f"font-size:12px;color:{C.TEXT2};border:none;"); kd.setWordWrap(True); kfl.addWidget(kd)
        prog = QLabel(f"Haftalık plan: {ders_programi_yazisi(k)}")
        prog.setStyleSheet(f"font-size:12px;color:{C.CYAN};font-weight:bold;border:none;")
        kfl.addWidget(prog)
        mode = QLabel(f"Yayın: {ders_platform_yazisi(k)}")
        mode.setStyleSheet(f"font-size:11px;color:{C.TEXT2};border:none;")
        kfl.addWidget(mode)
        if k.get("ders_linki"):
            link = QLabel(f"Ders bağlantısı: {k['ders_linki']}")
            link.setTextInteractionFlags(Qt.TextSelectableByMouse)
            link.setStyleSheet(f"font-size:11px;color:{C.PRI2};border:none;")
            kfl.addWidget(link)
        pct = round(k["kayitli_ogrenci_sayisi"]/max(k["kontenjan"],1)*100)
        clr = C.GREEN if pct < 70 else (C.YELLOW if pct < 90 else C.RED)
        pl = QLabel(f"Kontenjan: {k['kayitli_ogrenci_sayisi']}/{k['kontenjan']} (%{pct})")
        pl.setStyleSheet(f"font-size:12px;color:{clr};font-weight:bold;border:none;font-family:'Consolas';"); kfl.addWidget(pl)
        bar = QFrame(); bar.setFixedHeight(6)
        bar.setStyleSheet(f"background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {clr},"
            f"stop:{min(pct/100,1)} {clr},stop:{min(pct/100+0.005,1)} {C.CARD3},"
            f"stop:1 {C.CARD3});border-radius:3px;border:none;"); kfl.addWidget(bar)
        dl.addWidget(kf)
        ef = QFrame()
        ef.setStyleSheet(f"QFrame{{background:{C.CARD};border:none;border-radius:14px;}}")
        efl = QVBoxLayout(ef); efl.setContentsMargins(18,16,18,16); efl.setSpacing(6)
        efl.addWidget(lbl_k("Eğitmen Profili"))
        en = QLabel(f"{k.get('egitmen_adi','—')} • {k.get('egitmen_uzmanlik','')}")
        en.setStyleSheet(f"font-size:13px;font-weight:bold;color:{C.TEXT};border:none;")
        efl.addWidget(en)
        eb = QLabel(k.get("egitmen_biyografi") or "Bu eğitmen için kısa profil bilgisi henüz eklenmedi.")
        eb.setWordWrap(True)
        eb.setStyleSheet(f"font-size:11px;color:{C.TEXT2};border:none;")
        efl.addWidget(eb)
        dl.addWidget(ef)
        ogr = s.vt["kurs"].kayitli_ogrenciler(kid)
        hdr = QHBoxLayout(); ht = lbl_t(f"Kayıtlı Öğrenciler ({len(ogr)})", 18); hdr.addWidget(ht); hdr.addStretch()
        if k["kayitli_ogrenci_sayisi"] < k["kontenjan"]:
            bk = btn_primary("+ Öğrenci Kaydet"); bk.clicked.connect(lambda: s._kayit(kid)); hdr.addWidget(bk)
        dl.addLayout(hdr)
        if ogr:
            ot = QTableWidget(); ot.setColumnCount(3); ot.setHorizontalHeaderLabels(["Ad Soyad","E-posta","Telefon"])
            ot.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
            for c in range(1, 3): ot.horizontalHeader().setSectionResizeMode(c, QHeaderView.ResizeToContents)
            ot.verticalHeader().setVisible(False); ot.setShowGrid(False)
            ot.setRowCount(len(ogr))
            for i, o in enumerate(ogr):
                ot.setItem(i,0,QTableWidgetItem(f"{o['ad']} {o['soyad']}"))
                ot.setItem(i,1,QTableWidgetItem(o['email']))
                ot.setItem(i,2,QTableWidgetItem(o.get('telefon','—'))); ot.setRowHeight(i, 38)
            dl.addWidget(ot)
        else:
            el = QLabel("Henüz öğrenci yok."); el.setStyleSheet(f"font-size:12px;color:{C.TEXT3};padding:16px;"); el.setAlignment(Qt.AlignCenter); dl.addWidget(el)
        dl.addStretch(); dw.setWidget(ct); s.stk.addWidget(dw); s.stk.setCurrentIndex(1)
    def _kayit(s, kid):
        kayitli = [o["ogrenci_id"] for o in s.vt["kurs"].kayitli_ogrenciler(kid)]
        uygun = [o for o in s.vt["ogrenci"].listele() if o["ogrenci_id"] not in kayitli]
        if not uygun: QMessageBox.information(s,"Bilgi","Tüm öğrenciler kayıtlı."); return
        d = QDialog(s); d.setWindowTitle("Öğrenci Kaydet"); d.setFixedWidth(380)
        d.setStyleSheet(f"QDialog{{background:{C.CARD};color:{C.TEXT};}}")
        fl = QVBoxLayout(d); fl.setContentsMargins(22,22,22,22); fl.setSpacing(10)
        fl.addWidget(lbl_t("Öğrenci Seçin", 18))
        cmb = QComboBox()
        for o in uygun: cmb.addItem(f"{o['ad']} {o['soyad']}", o['ogrenci_id'])
        fl.addWidget(cmb)
        b = btn_primary("Kaydet"); b.clicked.connect(lambda: s._ky(d, kid, cmb.currentData())); fl.addWidget(b); d.exec_()
    def _ky(s, d, kid, oid):
        r = s.vt["kurs"].ogrenci_kaydet(kid, oid)
        if r["basarili"]: d.accept(); log("Öğrenci kaydedildi", C.GREEN); s._det(kid)
        else: QMessageBox.warning(s,"Hata",r["mesaj"])
    def _add(s):
        d = QDialog(s); d.setWindowTitle("Yeni Kurs"); d.setFixedWidth(420)
        d.setStyleSheet(f"QDialog{{background:{C.CARD};color:{C.TEXT};}}")
        f = QFormLayout(d); f.setSpacing(10); f.setContentsMargins(24,24,24,24)
        ta = QLineEdit(); ta.setPlaceholderText("Kurs adı")
        tc = QLineEdit(); tc.setPlaceholderText("Açıklama")
        ce = QComboBox()
        for e in s.vt["egitmen"].listele(): ce.addItem(f"{e['ad']} {e['soyad']}", e['egitmen_id'])
        tk = QLineEdit("30"); ck = QComboBox()
        for k in ["Programlama","Veri Bilimi","Web Geliştirme","Yapay Zeka","Mobil","Siber Güvenlik"]: ck.addItem(k)
        cs = QComboBox()
        for sv in ["Başlangıç","Orta","İleri"]: cs.addItem(sv)
        cg = QComboBox()
        for gun in GUN_SIRASI: cg.addItem(gun)
        tbs = QLineEdit("19:00"); tbs.setInputMask("99:99")
        tbt = QLineEdit("20:30"); tbt.setInputMask("99:99")
        cfm = QComboBox()
        for secenek in ["Canlı", "Canlı + Kayıt", "Video Kurs"]: cfm.addItem(secenek)
        tpl = QLineEdit("ByTeach Live")
        tln = QLineEdit(); tln.setPlaceholderText("https://...")
        f.addRow("Kurs:",ta); f.addRow("Açıklama:",tc); f.addRow("Eğitmen:",ce)
        f.addRow("Kontenjan:",tk); f.addRow("Kategori:",ck); f.addRow("Seviye:",cs)
        f.addRow("Gün:",cg); f.addRow("Başlangıç:",tbs); f.addRow("Bitiş:",tbt)
        f.addRow("Format:",cfm); f.addRow("Platform:",tpl); f.addRow("Ders linki:",tln)
        b = btn_primary("Oluştur")
        b.clicked.connect(lambda: s._sv(
            d, ta.text(), tc.text(), ce.currentData(), tk.text(), ck.currentText(),
            cs.currentText(), cg.currentText(), tbs.text(), tbt.text(),
            cfm.currentText(), tpl.text(), tln.text()
        ))
        f.addRow(b); d.exec_()
    def _sv(s, d, ad, ac, eid, kon, kat, sev, gun, bas, bit, fmt, platform, link):
        if not ad or not eid: QMessageBox.warning(s,"Hata","Kurs adı ve eğitmen gerekli."); return
        s.vt["kurs"].ekle(
            ad, eid, int(kon or 30), ac, kat, sev,
            gun=gun, baslangic_saati=bas, bitis_saati=bit,
            format=fmt, platform=platform.strip() or "ByTeach Live",
            ders_linki=link.strip()
        )
        d.accept(); s.refresh()
        log(f"'{ad}' oluşturuldu", C.GOLD)
        if s.pw: Toast(s.pw, f"✓ '{ad}' oluşturuldu", C.GREEN)
    def _del(s, kid):
        cevap = QMessageBox.question(s, "Onay", "Kursu silmek istediğinize emin misiniz?", QMessageBox.Yes | QMessageBox.No)
        if cevap == QMessageBox.Yes:
            s.vt["kurs"].sil(kid); s.refresh(); log("Kurs silindi", C.RED)


class EgitmenlerP(QWidget):
    def __init__(s, vt, pw=None):
        super().__init__(); s.vt = vt; s.pw = pw
        l = QVBoxLayout(s); l.setContentsMargins(26,22,26,22); l.setSpacing(12)
        top = QHBoxLayout(); left = QVBoxLayout()
        left.addWidget(lbl_k("Akademik Kadro")); left.addWidget(lbl_t("Eğitmen Yönetimi"))
        top.addLayout(left); top.addStretch()
        bc = btn_ghost("📁 CSV Aktar"); bc.clicked.connect(s._csv); top.addWidget(bc, alignment=Qt.AlignBottom)
        ba = btn_primary("+ Yeni Eğitmen"); ba.clicked.connect(s._add); top.addWidget(ba, alignment=Qt.AlignBottom)
        l.addLayout(top)
        s.search = QLineEdit(); s.search.setPlaceholderText("🔍 Eğitmen ara..."); s.search.setFixedHeight(42)
        s.search.textChanged.connect(s.refresh); l.addWidget(s.search)
        s.table = QTableWidget(); s.table.setColumnCount(6)
        s.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        s.table.setHorizontalHeaderLabels(["Ad Soyad","E-posta","Uzmanlık","Canlı Program","Biyografi","İşlemler"])
        s.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for c in range(1, 6): s.table.horizontalHeader().setSectionResizeMode(c, QHeaderView.ResizeToContents)
        s.table.verticalHeader().setVisible(False); s.table.setShowGrid(False); l.addWidget(s.table); s.refresh()
    def refresh(s):
        q = s.search.text().lower() if hasattr(s,'search') else ""
        data = s.vt["egitmen"].listele()
        if q: data = [e for e in data if q in f"{e['ad']} {e['soyad']}".lower() or q in e['uzmanlik'].lower()]
        s.table.setRowCount(len(data))
        for i, e in enumerate(data):
            programlar = s.vt["egitmen"].kurslari_getir(e["egitmen_id"])
            ozet = ", ".join(
                f"{k.get('gun','?')} {k.get('baslangic_saati','')}".strip()
                for k in programlar[:2]
            ) or "Plan girilmedi"
            s.table.setItem(i,0,QTableWidgetItem(f"{e['ad']} {e['soyad']}"))
            s.table.setItem(i,1,QTableWidgetItem(e['email']))
            s.table.setItem(i,2,QTableWidgetItem(e['uzmanlik']))
            s.table.setItem(i,3,QTableWidgetItem(ozet))
            s.table.setItem(i,4,QTableWidgetItem(e.get('biyografi','')))
            
            actions = QWidget(); al = QHBoxLayout(actions); al.setContentsMargins(4,0,4,0); al.setSpacing(8)
            bd = btn_danger("Sil"); bd.clicked.connect(lambda c,eid=e["egitmen_id"]: s._del(eid)); al.addWidget(bd)
            s.table.setCellWidget(i,5,actions)
            s.table.setRowHeight(i, 48)
    def _csv(s):
        data = s.vt["egitmen"].listele()
        try:
            with open("egitmenler.csv",'w',newline='',encoding='utf-8-sig') as f:
                w=csv.writer(f);w.writerow(["Ad","E-posta","Uzmanlık","Program","Bio"])
                for e in data:
                    programlar = s.vt["egitmen"].kurslari_getir(e["egitmen_id"])
                    ozet = ", ".join(
                        f"{k.get('gun','?')} {k.get('baslangic_saati','')}".strip()
                        for k in programlar[:2]
                    )
                    w.writerow([f"{e['ad']} {e['soyad']}",e['email'],e['uzmanlik'],ozet,e.get('biyografi','')])
            if s.pw: Toast(s.pw,"✓ CSV aktarıldı",C.GREEN)
        except: pass
    def _add(s):
        d = QDialog(s); d.setWindowTitle("Yeni Eğitmen"); d.setFixedWidth(420)
        d.setStyleSheet(f"QDialog{{background:{C.CARD};color:{C.TEXT};}}")
        f = QFormLayout(d); f.setSpacing(10); f.setContentsMargins(24,24,24,24)
        ta,ts,te,tu = QLineEdit(),QLineEdit(),QLineEdit(),QLineEdit()
        tb = QTextEdit(); tb.setMaximumHeight(60)
        f.addRow("Ad:",ta); f.addRow("Soyad:",ts); f.addRow("E-posta:",te)
        f.addRow("Uzmanlık:",tu); f.addRow("Biyografi:",tb)
        b = btn_primary("Ekle")
        b.clicked.connect(lambda: s._sv(d,ta.text(),ts.text(),te.text(),tu.text(),tb.toPlainText()))
        f.addRow(b); d.exec_()
    def _sv(s, d, a, sy, e, u, b):
        if not all([a,sy,e,u]): QMessageBox.warning(s,"Hata","Tüm alanlar zorunlu."); return
        r = s.vt["egitmen"].ekle(a, sy, e, u, b)
        if not r["basarili"]: QMessageBox.warning(s,"Hata",r["mesaj"]); return
        d.accept(); s.refresh(); log(f"{a} {sy} eklendi", C.GREEN)
        if s.pw: Toast(s.pw, f"✓ Eklendi", C.GREEN)
    def _del(s, eid):
        cevap = QMessageBox.question(s, "Onay", "Eğitmeni silmek istediğinize emin misiniz?", QMessageBox.Yes | QMessageBox.No)
        if cevap == QMessageBox.Yes:
            r = s.vt["egitmen"].sil(eid)
            if not r["basarili"]: QMessageBox.warning(s,"Uyarı",r["mesaj"])
            else: s.refresh(); log("Eğitmen silindi", C.RED)

class OgrencilerP(QWidget):
    def __init__(s, vt, pw=None):
        super().__init__(); s.vt = vt; s.pw = pw
        s.stk = QStackedWidget(); lay = QVBoxLayout(s); lay.setContentsMargins(0,0,0,0); lay.addWidget(s.stk)
        s.lw = QWidget(); s._bl(); s.stk.addWidget(s.lw)
    def _bl(s):
        l = QVBoxLayout(s.lw); l.setContentsMargins(26,22,26,22); l.setSpacing(12)
        top = QHBoxLayout(); left = QVBoxLayout()
        left.addWidget(lbl_k("Öğrenci Veritabanı")); left.addWidget(lbl_t("Öğrenci Yönetimi"))
        top.addLayout(left); top.addStretch()
        bc = btn_ghost("📁 CSV Aktar"); bc.clicked.connect(s._csv); top.addWidget(bc, alignment=Qt.AlignBottom)
        ba = btn_primary("+ Yeni Öğrenci"); ba.clicked.connect(s._add); top.addWidget(ba, alignment=Qt.AlignBottom)
        l.addLayout(top)
        s.search = QLineEdit(); s.search.setPlaceholderText("🔍 Öğrenci ara..."); s.search.setFixedHeight(42)
        s.search.textChanged.connect(s.refresh); l.addWidget(s.search)
        s.table = QTableWidget(); s.table.setColumnCount(5)
        s.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        s.table.setHorizontalHeaderLabels(["Ad Soyad","E-posta","Telefon","Kurs Sayısı","İşlemler"])
        s.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for c in range(1, 5): s.table.horizontalHeader().setSectionResizeMode(c, QHeaderView.ResizeToContents)
        s.table.verticalHeader().setVisible(False); s.table.setShowGrid(False); l.addWidget(s.table); s.refresh()
    def refresh(s):
        q = s.search.text().lower() if hasattr(s,'search') else ""
        data = s.vt["ogrenci"].listele()
        if q: data = [o for o in data if q in f"{o['ad']} {o['soyad']}".lower() or q in o['email'].lower()]
        s.table.setRowCount(len(data))
        for i, o in enumerate(data):
            s.table.setItem(i,0,QTableWidgetItem(f"{o['ad']} {o['soyad']}"))
            s.table.setItem(i,1,QTableWidgetItem(o['email']))
            s.table.setItem(i,2,QTableWidgetItem(o.get('telefon','—')))
            ks = len(s.vt["ogrenci"].kurs_listesi(o['ogrenci_id']))
            ki = QTableWidgetItem(str(ks)); ki.setForeground(QColor(C.PRI2)); s.table.setItem(i,3,ki)
            
            actions = QWidget(); al = QHBoxLayout(actions); al.setContentsMargins(4,0,4,0); al.setSpacing(8)
            bd2 = btn_acc("Detay", C.PRI, 28); bd2.clicked.connect(lambda c,oid=o["ogrenci_id"]: s._det(oid)); al.addWidget(bd2)
            bd = btn_danger("Sil"); bd.clicked.connect(lambda c,oid=o["ogrenci_id"]: s._del(oid)); al.addWidget(bd)
            s.table.setCellWidget(i,4,actions)
            s.table.setRowHeight(i, 48)
    def _csv(s):
        data = s.vt["ogrenci"].listele()
        try:
            with open("ogrenciler.csv",'w',newline='',encoding='utf-8-sig') as f:
                w=csv.writer(f);w.writerow(["Ad","E-posta","Telefon","Kurs"])
                for o in data: w.writerow([f"{o['ad']} {o['soyad']}",o['email'],o.get('telefon',''),str(len(s.vt["ogrenci"].kurs_listesi(o['ogrenci_id'])))])
            if s.pw: Toast(s.pw,"✓ CSV aktarıldı",C.GREEN)
        except: pass
    def _det(s, oid):
        o = s.vt["ogrenci"].getir(oid)
        if not o: return
        if s.stk.count() > 1: old = s.stk.widget(1); s.stk.removeWidget(old); old.deleteLater()
        dw = QScrollArea(); dw.setWidgetResizable(True); dw.setStyleSheet(f"QScrollArea{{background:{C.BG};border:none;}}")
        ct = QWidget(); dl = QVBoxLayout(ct); dl.setContentsMargins(26,22,26,22); dl.setSpacing(12)
        back = btn_ghost("← Öğrencilere dön"); back.clicked.connect(lambda: s.stk.setCurrentIndex(0)); dl.addWidget(back, alignment=Qt.AlignLeft)
        pf = QFrame(); pf.setStyleSheet(f"QFrame{{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            f"stop:0 {C.PRI}10,stop:1 {C.CARD});border:none;border-radius:14px;}}")
        pl = QHBoxLayout(pf); pl.setContentsMargins(22,18,22,18); pl.setSpacing(16)
        av = QLabel(f"{o['ad'][0]}{o['soyad'][0]}"); av.setFixedSize(54,54); av.setAlignment(Qt.AlignCenter)
        av.setStyleSheet(f"font-size:20px;font-weight:bold;color:white;background:qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            f"stop:0 {C.PRI},stop:1 {C.BLU});border-radius:16px;border:none;"); pl.addWidget(av)
        info = QVBoxLayout()
        nt = lbl_t(f"{o['ad']} {o['soyad']}", 22); nt.setStyleSheet(nt.styleSheet()+"border:none;"); info.addWidget(nt)
        nd = QLabel(f"📧 {o['email']}  📱 {o.get('telefon','—')}"); nd.setStyleSheet(f"font-size:12px;color:{C.TEXT2};border:none;"); info.addWidget(nd)
        pl.addLayout(info); pl.addStretch(); dl.addWidget(pf)
        ks = s.vt["ogrenci"].kurs_listesi(oid)
        dl.addWidget(lbl_t(f"Kayıtlı Kurslar ({len(ks)})", 18))
        for k in ks:
            kf = QFrame(); kf.setStyleSheet(f"QFrame{{background:{C.CARD};border:1px solid {C.BORDER2};border-radius:12px;}}")
            kr = QVBoxLayout(kf); kr.setContentsMargins(16,12,16,12); kr.setSpacing(6)
            ust = QHBoxLayout()
            kn = QLabel(f"📚 {k['kurs_adi']}"); kn.setStyleSheet(f"font-size:13px;font-weight:bold;color:{C.TEXT};border:none;"); ust.addWidget(kn)
            ust.addStretch()
            clr = KR.get(k['kategori'], C.GOLD)
            kat = QLabel(k['kategori']); kat.setStyleSheet(f"font-size:10px;color:{clr};background:{clr}15;border:none;border-radius:8px;padding:3px 10px;font-weight:bold;")
            ust.addWidget(kat)
            kr.addLayout(ust)
            md = QLabel(f"{ders_programi_yazisi(k)} • {k.get('egitmen_adi','—')}")
            md.setStyleSheet(f"font-size:10px;color:{C.TEXT2};border:none;")
            kr.addWidget(md)
            dl.addWidget(kf)
        if not ks:
            el = QLabel("Henüz kurs yok."); el.setStyleSheet(f"font-size:11px;color:{C.TEXT3};padding:16px;"); el.setAlignment(Qt.AlignCenter); dl.addWidget(el)
        dl.addStretch(); dw.setWidget(ct); s.stk.addWidget(dw); s.stk.setCurrentIndex(1)
    def _add(s):
        d = QDialog(s); d.setWindowTitle("Yeni Öğrenci"); d.setFixedWidth(420)
        d.setStyleSheet(f"QDialog{{background:{C.CARD};color:{C.TEXT};}}")
        f = QFormLayout(d); f.setSpacing(10); f.setContentsMargins(24,24,24,24)
        ta,ts,te,tt = QLineEdit(),QLineEdit(),QLineEdit(),QLineEdit()
        f.addRow("Ad:",ta); f.addRow("Soyad:",ts); f.addRow("E-posta:",te); f.addRow("Telefon:",tt)
        b = btn_primary("Ekle"); b.clicked.connect(lambda: s._sv(d,ta.text(),ts.text(),te.text(),tt.text())); f.addRow(b); d.exec_()
    def _sv(s, d, a, sy, e, t):
        if not all([a,sy,e]): QMessageBox.warning(s,"Hata","Ad, soyad, e-posta zorunlu."); return
        r = s.vt["ogrenci"].ekle(a, sy, e, t)
        if not r["basarili"]: QMessageBox.warning(s,"Hata",r["mesaj"]); return
        d.accept(); s.refresh(); log(f"{a} {sy} eklendi", C.GREEN)
        if s.pw: Toast(s.pw, f"✓ Eklendi", C.GREEN)
    def _del(s, oid):
        cevap = QMessageBox.question(s, "Onay", "Öğrenciyi silmek istediğinize emin misiniz?", QMessageBox.Yes | QMessageBox.No)
        if cevap == QMessageBox.Yes:
            s.vt["ogrenci"].sil(oid); s.refresh(); log("Öğrenci silindi", C.RED)


class HaritaP(QWidget):
    def __init__(s):
        super().__init__()
        l = QVBoxLayout(s); l.setContentsMargins(26,22,26,22); l.setSpacing(12)
        top = QVBoxLayout()
        top.addWidget(lbl_k("Yerleşkeler")); top.addWidget(lbl_t("Kampüs Haritası"))
        l.addLayout(top)
        h = Harita()
        h.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        l.addWidget(h)

# ══════════════════════════════════════════════════════════════════
#  ANA PENCERE
# ══════════════════════════════════════════════════════════════════
class AnaPencere(QMainWindow):
    STIL = f"""
        QMainWindow{{background:{C.BG};}} QLabel{{color:{C.TEXT};}}
        QLineEdit,QTextEdit,QComboBox{{background:{C.CARD};color:{C.TEXT};border:none;
            border-radius:11px;padding:10px 14px;font-size:13px;}}
        QTableWidget{{background:{C.BG};color:{C.TEXT};border:none;
            font-size:13px;selection-background-color:{C.CARD3};}}
        QTableWidget::item{{padding:6px 12px;border:none;}}
        QHeaderView::section{{background:{C.CARD};color:{C.PRI2};border:none;
            padding:8px 12px;font-size:11px;font-weight:bold;letter-spacing:1px;}}
        QScrollBar:vertical{{background:transparent;width:6px;}}
        QScrollBar::handle:vertical{{background:{C.PRI}40;border-radius:3px;min-height:20px;}}
        QScrollBar::handle:vertical:hover{{background:{C.PRI};}}
        QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{{height:0;}}
        QComboBox::drop-down{{border:none;width:22px;}}
        QComboBox QAbstractItemView{{background:{C.CARD};color:{C.TEXT};border:none;}}
    """
    def __init__(s):
        super().__init__()
        s.setWindowTitle("ByTeach v10.0 — Çevrimiçi Öğrenme Platformu")
        s.setMinimumSize(1340, 820)
        s.showMaximized()
        s.setStyleSheet(s.STIL)

        # Veritabanı yolunu bul (Windows'ta APPDATA, fallback olarak home)
        db_path = s._veritabani_yolu_bul()

        try:
            s.vt = Veritabani(db_path)
            # KVT artık Veritabani ile AYNI bağlantıyı paylaşır - kilit sorununu önler
            s.kvt = KVT(s.vt.conn)
            s.vtn = {"egitmen": Egitmen(s.vt), "kurs": Kurs(s.vt),
                     "ogrenci": Ogrenci(s.vt), "istatistik": IstatistikYoneticisi(s.vt)}
            s._seed()
        except Exception as err:
            QMessageBox.critical(
                None, "Veritabanı Hatası",
                f"Veritabanı başlatılamadı!\n\n"
                f"Konum: {db_path}\n\n"
                f"Hata: {str(err)}\n\n"
                f"Öneriler:\n"
                f"• Uygulamayı yönetici olarak çalıştırmayı deneyin\n"
                f"• Antivirüsünüzün uygulamayı engellemediğinden emin olun\n"
                f"• Yukarıdaki konumda yazma izniniz olduğunu kontrol edin"
            )
            sys.exit(1)

        s.root = QStackedWidget()
        s.setCentralWidget(s.root)
        s.root.addWidget(GirisEkrani(s.kvt, s._on_login))

    @staticmethod
    def _veritabani_yolu_bul():
        """
        Platforma uygun, yazılabilir bir veritabanı konumu bulur.

        Sıralama:
          1. Windows: %APPDATA%\\ByTeach  (en uygun konum)
          2. ~/ByTeachData                (Linux/Mac veya APPDATA yoksa)
          3. Exe'nin bulunduğu klasör     (son çare)
          4. Geçici dizin                  (hiçbir şey olmazsa)

        Her adayda yazma izni test edilir; başarılı olan ilkini kullanır.
        Bu sayede OneDrive yönlendirmesi veya izin sorunları otomatik aşılır.
        """
        adaylar = []

        # 1) Windows: %APPDATA%\ByTeach
        appdata = os.environ.get("APPDATA")
        if appdata:
            adaylar.append(os.path.join(appdata, "ByTeach"))

        # 2) Home dizini
        try:
            home = os.path.expanduser("~")
            if home and home != "~":
                adaylar.append(os.path.join(home, "ByTeachData"))
        except Exception:
            pass

        # 3) Exe veya script klasörü
        try:
            if getattr(sys, "frozen", False):
                adaylar.append(os.path.dirname(sys.executable))
            else:
                adaylar.append(os.path.dirname(os.path.abspath(__file__)))
        except Exception:
            pass

        # Her adayı sırayla dene
        for klasor in adaylar:
            try:
                os.makedirs(klasor, exist_ok=True)
                # Yazma iznini test et
                test_dosyasi = os.path.join(klasor, ".byteach_write_test")
                with open(test_dosyasi, "w", encoding="utf-8") as tf:
                    tf.write("ok")
                os.remove(test_dosyasi)
                return os.path.join(klasor, "kurs_platformu.db")
            except Exception:
                continue

        # 4) Son çare: geçici dizin
        import tempfile
        temp_klasor = os.path.join(tempfile.gettempdir(), "ByTeach")
        os.makedirs(temp_klasor, exist_ok=True)
        return os.path.join(temp_klasor, "kurs_platformu.db")

    def _seed(s):
        if s.vtn["egitmen"].listele(): return
        for e in [("Ahmet","Yılmaz","ahmet@p.com","Python ve Veri Bilimi","10 yıl deneyimli"),
            ("Elif","Kaya","elif@p.com","Web Geliştirme","React uzmanı"),
            ("Mehmet","Demir","mehmet@p.com","Yapay Zeka","Doktora dereceli"),
            ("Zeynep","Arslan","zeynep@p.com","Mobil Uygulama","iOS/Android"),
            ("Can","Öztürk","can@p.com","Siber Güvenlik","Güvenlik uzmanı")]:
            s.vtn["egitmen"].ekle(*e)
        for k in [
            ("Python Programlama",1,35,"Sıfırdan Python","Programlama","Başlangıç","Pazartesi","19:00","20:30","Canlı","ByTeach Live","https://byteach.live/python"),
            ("UI/UX Tasarım Temelleri",2,25,"Figma ile Tasarım","Web Geliştirme","Başlangıç","Pazartesi","14:00","16:00","Canlı","Zoom","https://byteach.live/uiux"),
            ("Veritabanı Sistemleri",1,40,"SQL ve NoSQL","Veri Bilimi","Orta","Salı","09:00","11:30","Canlı + Kayıt","Google Meet","https://byteach.live/db"),
            ("Veri Bilimi Temelleri",1,25,"Pandas NumPy","Veri Bilimi","Orta","Salı","20:00","21:30","Canlı + Kayıt","Zoom","https://byteach.live/veri"),
            ("Siber Güvenliğe Giriş",5,30,"Temel Kavramlar","Siber Güvenlik","Başlangıç","Çarşamba","10:30","12:00","Canlı","ByTeach Live","https://byteach.live/sec101"),
            ("React ile Modern Web",2,30,"Hooks ve state","Web Geliştirme","Orta","Çarşamba","19:30","21:00","Canlı","Google Meet","https://byteach.live/react"),
            ("İleri Java Programlama",1,20,"Spring Boot","Programlama","İleri","Perşembe","13:00","15:00","Canlı","Zoom","https://byteach.live/java"),
            ("Node.js Sunucu",2,20,"REST API","Web Geliştirme","İleri","Perşembe","21:00","22:15","Canlı","ByTeach Live","https://byteach.live/node"),
            ("DevOps ve CI/CD",5,25,"Docker & Jenkins","Siber Güvenlik","Orta","Cuma","09:30","11:00","Canlı + Kayıt","Google Meet","https://byteach.live/devops"),
            ("Makine Öğrenmesi 101",3,30,"ML algoritmaları","Yapay Zeka","Başlangıç","Cuma","19:00","20:20","Video Kurs","ByTeach Academy",""),
            ("C# Kurumsal Mimari",1,30,".NET Core Core","Programlama","Orta","Cumartesi","10:00","12:00","Canlı","Zoom","https://byteach.live/csharp"),
            ("Derin Öğrenme",3,15,"TensorFlow","Yapay Zeka","İleri","Cumartesi","13:00","15:00","Canlı + Kayıt","Zoom","https://byteach.live/dl"),
            ("Etik Sızma Testi",5,20,"Penetrasyon testi","Siber Güvenlik","İleri","Cumartesi","20:00","21:30","Canlı","ByTeach Live","https://byteach.live/security"),
            ("Flutter Mobil",4,25,"Çapraz platform","Mobil","Orta","Pazar","12:00","13:30","Canlı","Google Meet","https://byteach.live/flutter"),
            ("Yapay Zeka Uygulamaları",3,40,"Pratik YZ","Yapay Zeka","İleri","Pazar","18:00","20:00","Canlı + Kayıt","ByTeach Live","https://byteach.live/ai-apps")
        ]:
            s.vtn["kurs"].ekle(*k)
        for o in [("Ali","Veli","ali@m.com","555-01"),("Ayşe","Yıldız","ayse@m.com","555-02"),
            ("Burak","Çelik","burak@m.com","555-03"),("Deniz","Akar","deniz@m.com","555-04"),
            ("Esra","Koç","esra@m.com","555-05"),("Fatih","Şen","fatih@m.com","555-06"),
            ("Gül","Tunç","gul@m.com","555-07"),("Hakan","Bal","hakan@m.com","555-08")]:
            s.vtn["ogrenci"].ekle(*o)
        for oid,kid in [(1,1),(1,3),(2,1),(2,2),(3,3),(3,5),(4,6),(4,7),(5,4),(5,8),(6,1),(6,2),(7,6),(8,5),(1,12),(2,9),(3,11),(4,14),(5,15)]:
            s.vtn["kurs"].ogrenci_kaydet(kid, oid)
        log("Platform başlatıldı", C.GOLD)

    def _on_login(s, user):
        panel = QWidget()
        pl = QHBoxLayout(panel); pl.setContentsMargins(0,0,0,0); pl.setSpacing(0)
        s.menu = SolMenu(s._go, user, s._lo); pl.addWidget(s.menu)
        s.pages = QStackedWidget()
        s.pages.addWidget(Dashboard(s.vtn, user, s._go))
        s.pages.addWidget(KurslarP(s.vtn, s))
        s.pages.addWidget(EgitmenlerP(s.vtn, s))
        s.pages.addWidget(OgrencilerP(s.vtn, s))
        s.pages.addWidget(HaritaP())
        pl.addWidget(s.pages, stretch=1)
        
        s.seven_panel = Seven(s.vtn)
        s.seven_panel.setParent(panel)
        s.seven_panel.setVisible(False)
        
        s.root.addWidget(panel); s.root.setCurrentIndex(1)
        
        s.ai_btn = QPushButton("✦", s)
        s.ai_btn.setCursor(Qt.PointingHandCursor)
        s.ai_btn.setFixedSize(56, 56)
        s.ai_btn.setStyleSheet(f"QPushButton{{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 {C.PRI},stop:1 {C.BLU});"
                               f"color:white;border:none;border-radius:28px;font-weight:bold;font-size:24px;}}"
                               f"QPushButton:hover{{background:{C.PRI2};}}")
        eff = QGraphicsDropShadowEffect(s.ai_btn)
        eff.setBlurRadius(20); eff.setOffset(0, 5); eff.setColor(QColor(0,0,0, 150))
        s.ai_btn.setGraphicsEffect(eff)
        s.ai_btn.clicked.connect(lambda: s.seven_panel.setVisible(not s.seven_panel.isVisible()))
        s.ai_btn.show()
        s._pos_ai_btn()
        
        log(f"{user['ad']} giriş yaptı", C.GREEN)
        Toast(s, f"Hoş geldiniz, {user['ad']}! ✦", C.GOLD)

    def _pos_ai_btn(s):
        if hasattr(s, 'ai_btn') and s.ai_btn:
            btn_x = s.width() - 90
            btn_y = s.height() - 90
            s.ai_btn.move(btn_x, btn_y)
            if hasattr(s, 'seven_panel') and s.seven_panel:
                s.seven_panel.move(btn_x - 320 + 56, btn_y - 520 - 16)

    def resizeEvent(s, ev):
        super().resizeEvent(ev)
        s._pos_ai_btn()

    def _go(s, i):
        s.pages.setCurrentIndex(i)
        w = s.pages.widget(i)
        if hasattr(w, 'refresh'): w.refresh()

    def _lo(s):
        if hasattr(s, 'ai_btn') and s.ai_btn:
            s.ai_btn.deleteLater()
            s.ai_btn = None
        w = s.root.widget(1)
        if w:
            s.root.removeWidget(w)
            w.deleteLater()
        s.root.setCurrentIndex(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    p = QPalette()
    for role, color in [(QPalette.Window,C.BG),(QPalette.WindowText,C.TEXT),(QPalette.Base,C.CARD),
        (QPalette.Text,C.TEXT),(QPalette.Button,C.CARD),(QPalette.ButtonText,C.TEXT),(QPalette.Highlight,C.PRI)]:
        p.setColor(role, QColor(color))
    app.setPalette(p)
    app.setStyleSheet("QLabel { background: transparent; }")
    win = AnaPencere()
    win.show()
    print("═" * 62)
    print("  ByTeach v10.0 — Yeni Gelişmiş Tema")
    print("═" * 62)
    sys.exit(app.exec_())
