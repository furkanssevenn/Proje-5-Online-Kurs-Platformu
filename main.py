"""
═══════════════════════════════════════════════════════════════════════════
  ONLINE KURS PLATFORMU — Ultra Profesyonel PyQt5 Sürümü
  Giriş Noktası (main.py)
═══════════════════════════════════════════════════════════════════════════

  Çalıştırma:
      python main.py

  Demo Hesaplar (ilk açılışta otomatik oluşturulur):
      🛡️  admin   / admin123
      🎓  ahmet   / ahmet123
      📖  ayse    / ayse123
"""
import logging
import os
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QApplication

from models import (Veritabani, Kullanici, Egitmen, Ogrenci, Kurs, Yorum,
                    Favori, Bildirim, Logger, IstatistikYoneticisi)


# ═════════════════════════════════════════════════════════════════════════
#  LOG YAPILANDIRMASI (dosya + konsol)
# ═════════════════════════════════════════════════════════════════════════
def _log_kur():
    os.makedirs("logs", exist_ok=True)
    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=fmt,
        handlers=[
            logging.FileHandler("logs/app.log", encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


# ═════════════════════════════════════════════════════════════════════════
#  DEMO VERİSİ (sadece ilk açılışta)
# ═════════════════════════════════════════════════════════════════════════
def seed_demo_verisi(services):
    c = services["vt"].baglanti.cursor()
    c.execute("SELECT COUNT(*) FROM kullanicilar")
    if c.fetchone()[0] > 0:
        return  # zaten yüklü

    log = logging.getLogger("seed")
    log.info("Demo verisi oluşturuluyor...")

    kul = services["kul"]

    # Yöneticileri oluştur
    kul.kaydol("Sistem", "Yöneticisi", "admin",
               "admin@kurspace.tr", "admin123", "admin",
               biyografi="Platform yöneticisi.")

    # Eğitmen 1 — Ahmet
    r = kul.kaydol("Ahmet", "Yılmaz", "ahmet",
                   "ahmet@kurspace.tr", "ahmet123", "egitmen",
                   biyografi="10+ yıllık yazılım geliştirme tecrübesi. Python ve modern web stack'leri.")
    # Uzmanlık güncelle
    eg = services["egitmen"].kullanici_id_ile_bul(r["id"])
    if eg:
        services["egitmen"].guncelle(eg["id"],
            uzmanlik="Python, Django, Web Geliştirme")

    # Eğitmen 2 — Zeynep
    r2 = kul.kaydol("Zeynep", "Demir", "zeynep",
                    "zeynep@kurspace.tr", "zeynep123", "egitmen",
                    biyografi="Veri bilimi ve makine öğrenmesi araştırmacısı.")
    eg2 = services["egitmen"].kullanici_id_ile_bul(r2["id"])
    if eg2:
        services["egitmen"].guncelle(eg2["id"],
            uzmanlik="Veri Bilimi, Pandas, ML")

    # Eğitmen 3 — Mehmet
    r3 = kul.kaydol("Mehmet", "Kaya", "mehmet",
                    "mehmet@kurspace.tr", "mehmet123", "egitmen",
                    biyografi="UI/UX tasarımcı ve frontend developer.")
    eg3 = services["egitmen"].kullanici_id_ile_bul(r3["id"])
    if eg3:
        services["egitmen"].guncelle(eg3["id"],
            uzmanlik="React, UI/UX Tasarım")

    # Öğrenciler
    kul.kaydol("Ayşe", "Şahin", "ayse",
               "ayse@kurspace.tr", "ayse123", "ogrenci")
    kul.kaydol("Burak", "Çelik", "burak",
               "burak@kurspace.tr", "burak123", "ogrenci")

    # Demo kurslar
    kurs = services["kurs"]
    demo_kurslar = [
        ("Sıfırdan Python Programlama", eg["id"], 50,
         "En temel kavramlardan ileri seviye konseptlere kadar Python öğrenin. "
         "Veri yapıları, OOP, dosya işlemleri ve daha fazlası.",
         "Programlama", "Başlangıç", 0),
        ("Django ile Web Geliştirme", eg["id"], 40,
         "Django framework ile tam donanımlı web uygulamaları geliştirin. "
         "ORM, view'lar, template'ler ve REST API'ler dahil.",
         "Web Geliştirme", "Orta", 199),
        ("Pandas ve NumPy ile Veri Analizi", eg2["id"], 35,
         "Veri bilimi yolculuğunuzu Pandas ve NumPy ile başlatın. "
         "Gerçek dünya veri setleriyle hands-on uygulamalar.",
         "Veri Bilimi", "Orta", 0),
        ("Makine Öğrenmesine Giriş", eg2["id"], 30,
         "Scikit-learn ile sınıflandırma, regresyon ve clustering algoritmaları. "
         "Teori + pratik uygulamalar.",
         "Veri Bilimi", "İleri", 299),
        ("Modern React.js", eg3["id"], 60,
         "Hooks, Context API, Redux ve modern React ekosistemi. "
         "Production-ready uygulamalar geliştirme.",
         "Web Geliştirme", "Orta", 249),
        ("UI/UX Tasarım Temelleri", eg3["id"], 45,
         "Figma ile pratikten geçmiş kullanıcı deneyimi tasarımı. "
         "Renk teorisi, typography ve modern tasarım prensipleri.",
         "Tasarım", "Başlangıç", 149),
        ("Algoritmalar ve Veri Yapıları", eg["id"], 25,
         "Big-O analizi, sıralama, arama, ağaç ve grafik algoritmaları. "
         "Mülakat hazırlığı için ideal.",
         "Programlama", "İleri", 0),
    ]
    for ad, eg_id, kont, ack, kat, sev, fyt in demo_kurslar:
        kurs.ekle(ad, eg_id, kont, aciklama=ack,
                  kategori=kat, seviye=sev, fiyat=fyt)

    # Demo bildirimi
    services["bildirim"].toplu_gonder(
        "🎉 Hoş geldiniz!",
        "ByTeach ailesine katıldığınız için teşekkürler. Kurslarımıza göz atmaya başlayabilirsiniz.",
        "basari", rol=None)

    services["logger"].info("system", "Demo verisi yüklendi")
    log.info("Demo verisi yüklendi: 6 kullanıcı, 7 kurs.")


# ═════════════════════════════════════════════════════════════════════════
#  SERVİSLERİ HAZIRLA
# ═════════════════════════════════════════════════════════════════════════
def servisleri_kur(db_yolu: str) -> dict:
    vt = Veritabani(db_yolu)
    return {
        "vt":         vt,
        "kul":        Kullanici(vt),
        "egitmen":    Egitmen(vt),
        "ogrenci":    Ogrenci(vt),
        "kurs":       Kurs(vt),
        "yorum":      Yorum(vt),
        "favori":     Favori(vt),
        "bildirim":   Bildirim(vt),
        "logger":     Logger(vt),
        "istatistik": IstatistikYoneticisi(vt),
    }


# ═════════════════════════════════════════════════════════════════════════
#  ANA DÖNGÜ
# ═════════════════════════════════════════════════════════════════════════
def main():
    _log_kur()
    log = logging.getLogger("main")

    os.makedirs("data", exist_ok=True)
    db_yolu = os.path.join("data", "kurs_platformu.db")

    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("ByTeach")
    app.setApplicationDisplayName("ByTeach · Online Kurs Platformu")
    app.setOrganizationName("ByTeach")

    # Varsayılan font
    f = QFont("Inter")
    f.setStyleStrategy(QFont.PreferAntialias)
    app.setFont(f)

    # ───── SPLASH EKRANI ─────
    from PyQt5.QtWidgets import QSplashScreen
    from PyQt5.QtGui import QPixmap, QPainter, QColor
    import time

    pixmap = QPixmap(500, 300)
    pixmap.fill(Qt.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QColor("#1e1e2d"))
    painter.setPen(Qt.NoPen)
    painter.drawRoundedRect(pixmap.rect(), 16, 16)
    
    painter.setFont(QFont("Inter", 40, QFont.Bold))
    painter.setPen(QColor("#6366f1"))
    painter.drawText(pixmap.rect(), Qt.AlignCenter, "ByTeach")
    
    painter.setFont(QFont("Inter", 12))
    painter.setPen(QColor("#94a3b8"))
    painter.drawText(0, 0, 500, 220, Qt.AlignBottom | Qt.AlignHCenter, "Ultra Profesyonel Online Kurs Platformu")
    
    painter.setFont(QFont("Inter", 10))
    painter.setPen(QColor("#64748b"))
    painter.drawText(0, 0, 500, 260, Qt.AlignBottom | Qt.AlignHCenter, "Sistem başlatılıyor...")
    
    painter.end()

    splash = QSplashScreen(pixmap, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
    splash.setAttribute(Qt.WA_TranslucentBackground)
    splash.show()
    app.processEvents()
    
    time.sleep(1.0)  # Sistemin açılış hissiyatını artırmak için kısa bir gecikme

    # Servisleri kur + seed
    services = servisleri_kur(db_yolu)
    seed_demo_verisi(services)
    
    splash.close()

    # Re-login destekli ana döngü
    while True:
        # ───── GİRİŞ EKRANI ─────
        from views.login_view import GirisDialog
        dlg = GirisDialog(services["kul"], services["logger"])
        sonuc = dlg.exec_()

        if sonuc != dlg.Accepted or not dlg.aktif_kullanici:
            log.info("Çıkış yapıldı.")
            break

        kullanici = dlg.aktif_kullanici
        services["logger"].info("auth",
            f"Giriş: {kullanici['kullanici_adi']}",
            kullanici_id=kullanici["id"])
        log.info(f"Oturum açıldı: {kullanici['kullanici_adi']} ({kullanici['rol']})")

        # ───── ANA PENCERE ─────
        from views.main_window import MainWindow
        win = MainWindow(services["vt"], kullanici, services)
        win.show()

        # 99 = "logout" (kullanıcı çıkış yaptı, login'e dön)
        # 0 / başka = uygulamadan tamamen çık
        cikis_kodu = app.exec_()
        try:
            win.deleteLater()
        except Exception:
            pass

        if cikis_kodu != 99:
            log.info(f"Uygulama kapatıldı (kod {cikis_kodu}).")
            break

        log.info("Logout — yeniden login ekranına dönülüyor.")

    services["vt"].kapat()
    sys.exit(0)


if __name__ == "__main__":
    main()
