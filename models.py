"""
╔══════════════════════════════════════════════════════════════╗
║           ONLINE KURS PLATFORMU - VERİ MODELLERİ            ║
╠══════════════════════════════════════════════════════════════╣
║  3 Ana Sınıf     : Kurs, Egitmen, Ogrenci                    ║
║  2 Yardımcı Sınıf: Veritabani, IstatistikYoneticisi          ║
║  Veri Yapıları   : Liste (list), Sözlük (dict)               ║
║  Veritabanı      : SQLite3                                   ║
║  Dosya           : models.py                                 ║
╚══════════════════════════════════════════════════════════════╝
"""

import sqlite3                              # SQLite veritabanı kütüphanesi
from typing import List, Dict, Optional      # Tip belirtme araçları
from datetime import datetime                # Tarih ve saat işlemleri


# ══════════════════════════════════════════════════════════════
#  YARDIMCI SINIF 1: VERİTABANI YÖNETİCİSİ
# ══════════════════════════════════════════════════════════════

class Veritabani:
    """
    SQLite veritabanı bağlantı yöneticisi.

    Bu sınıf veritabanı dosyasına bağlanır, gerekli tabloları oluşturur
    ve bağlantıyı kapatma işlemlerini yönetir.

    Özellikler:
        db_path (str)     : Veritabanı dosya yolu
        conn (Connection) : SQLite bağlantı nesnesi
        cursor (Cursor)   : SQL sorgu çalıştırma nesnesi

    Metodlar:
        baglanti_kur()      : Veritabanına bağlantı kurar
        tablolari_olustur() : Tüm tabloları oluşturur
        kapat()             : Bağlantıyı kapatır
    """

    def __init__(self, db_path: str = "kurs_platformu.db"):
        """Veritabanı nesnesini başlatır ve bağlantı kurar."""
        self.db_path = db_path
        self.baglanti_kur()
        self.tablolari_olustur()

    def baglanti_kur(self) -> sqlite3.Connection:
        """
        SQLite veritabanına bağlantı kurar.
        row_factory sayesinde sorgu sonuçları sözlük gibi erişilebilir olur.

        NOT: WAL modu ve busy_timeout etkinleştirilir. Bu sayede aynı dosyaya
        birden fazla bağlantı açıldığında (örn. KVT + Veritabani birlikte)
        'database is locked' hataları önlenir. Exe olarak paketlendiğinde
        kritik önemdedir.
        """
        # timeout=30: bağlantı kurulumunda 30 saniyeye kadar bekle
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=30.0)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

        # Eşzamanlılık ve performans PRAGMA'ları
        try:
            self.cursor.execute("PRAGMA journal_mode=WAL")   # Yazma-okuma eşzamanlı
            self.cursor.execute("PRAGMA busy_timeout=5000")  # 5sn kilit beklemesi
            self.cursor.execute("PRAGMA synchronous=NORMAL") # Hız + güvenlik dengesi
        except sqlite3.Error:
            pass  # Pragmalar başarısız olursa bile uygulama çalışmaya devam etmeli

        return self.conn

    def tablolari_olustur(self):
        """
        Veritabanındaki tüm tabloları oluşturur.

        Tablolar:
            1. egitmenler  - Eğitmen bilgileri
            2. kurslar     - Kurs bilgileri (eğitmen ile bire-çok ilişkili)
            3. ogrenciler  - Öğrenci bilgileri
            4. kayitlar    - Öğrenci-Kurs çoka-çok ilişki tablosu
        """
        self.cursor.executescript("""
            -- Eğitmenler tablosu
            CREATE TABLE IF NOT EXISTS egitmenler (
                egitmen_id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad TEXT NOT NULL,
                soyad TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                uzmanlik TEXT NOT NULL,
                biyografi TEXT DEFAULT '',
                kayit_tarihi TEXT DEFAULT (datetime('now'))
            );

            -- Kurslar tablosu (eğitmen ile ilişkili)
            CREATE TABLE IF NOT EXISTS kurslar (
                kurs_id INTEGER PRIMARY KEY AUTOINCREMENT,
                kurs_adi TEXT NOT NULL,
                aciklama TEXT DEFAULT '',
                egitmen_id INTEGER NOT NULL,
                kontenjan INTEGER DEFAULT 30,
                kayitli_ogrenci_sayisi INTEGER DEFAULT 0,
                kategori TEXT DEFAULT 'Genel',
                seviye TEXT DEFAULT 'Başlangıç',
                gun TEXT DEFAULT '',
                baslangic_saati TEXT DEFAULT '',
                bitis_saati TEXT DEFAULT '',
                format TEXT DEFAULT 'Canlı',
                platform TEXT DEFAULT 'ByTeach Live',
                ders_linki TEXT DEFAULT '',
                durum TEXT DEFAULT 'Aktif',
                olusturma_tarihi TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (egitmen_id) REFERENCES egitmenler(egitmen_id)
            );

            -- Öğrenciler tablosu
            CREATE TABLE IF NOT EXISTS ogrenciler (
                ogrenci_id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad TEXT NOT NULL,
                soyad TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                telefon TEXT DEFAULT '',
                kayit_tarihi TEXT DEFAULT (datetime('now'))
            );

            -- Kayıtlar tablosu (öğrenci-kurs çoka-çok ilişki)
            CREATE TABLE IF NOT EXISTS kayitlar (
                kayit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                ogrenci_id INTEGER NOT NULL,
                kurs_id INTEGER NOT NULL,
                kayit_tarihi TEXT DEFAULT (datetime('now')),
                durum TEXT DEFAULT 'Aktif',
                ilerleme INTEGER DEFAULT 0,
                FOREIGN KEY (ogrenci_id) REFERENCES ogrenciler(ogrenci_id),
                FOREIGN KEY (kurs_id) REFERENCES kurslar(kurs_id),
                UNIQUE(ogrenci_id, kurs_id)
            );
        """)
        self.conn.commit()

    def kapat(self):
        """Veritabanı bağlantısını güvenli şekilde kapatır."""
        self.conn.close()


# ══════════════════════════════════════════════════════════════
#  ANA SINIF 1: EĞİTMEN
# ══════════════════════════════════════════════════════════════

class Egitmen:
    """
    Eğitmen sınıfı - Platformdaki eğitmenleri yönetir.

    Özellikler:
        ad (str), soyad (str), email (str), uzmanlik (str), biyografi (str)

    Metodlar:
        ekle()           - Yeni eğitmen kaydı oluşturur
        getir()          - Eğitmen bilgilerini getirir
        listele()        - Tüm eğitmenleri listeler
        guncelle()       - Eğitmen bilgilerini günceller
        sil()            - Eğitmeni siler (aktif kursu varsa engellenir)
        kurslari_getir() - Eğitmenin verdiği kursları listeler
    """

    def __init__(self, db: Veritabani):
        """Eğitmen yöneticisini başlatır."""
        self.db = db

    def ekle(self, ad: str, soyad: str, email: str, uzmanlik: str, biyografi: str = "") -> Dict:
        """Yeni eğitmen kaydı oluşturur. E-posta benzersiz olmalıdır."""
        try:
            self.db.cursor.execute(
                "INSERT INTO egitmenler (ad, soyad, email, uzmanlik, biyografi) VALUES (?, ?, ?, ?, ?)",
                (ad, soyad, email, uzmanlik, biyografi)
            )
            self.db.conn.commit()
            return {"basarili": True, "egitmen_id": self.db.cursor.lastrowid,
                    "mesaj": f"{ad} {soyad} eğitmen olarak eklendi."}
        except sqlite3.IntegrityError:
            return {"basarili": False, "mesaj": "Bu e-posta adresi zaten kayıtlı."}

    def getir(self, egitmen_id: int) -> Optional[Dict]:
        """Belirli bir eğitmenin bilgilerini getirir."""
        self.db.cursor.execute("SELECT * FROM egitmenler WHERE egitmen_id = ?", (egitmen_id,))
        satir = self.db.cursor.fetchone()
        return dict(satir) if satir else None

    def listele(self) -> List[Dict]:
        """Tüm eğitmenleri ada göre sıralı listeler."""
        self.db.cursor.execute("SELECT * FROM egitmenler ORDER BY ad")
        return [dict(satir) for satir in self.db.cursor.fetchall()]

    def guncelle(self, egitmen_id: int, **kwargs) -> Dict:
        """Eğitmen bilgilerini günceller. Geçerli alanlar: ad, soyad, email, uzmanlik, biyografi"""
        alanlar, degerler = [], []
        for anahtar, deger in kwargs.items():
            if anahtar in ("ad", "soyad", "email", "uzmanlik", "biyografi"):
                alanlar.append(f"{anahtar} = ?")
                degerler.append(deger)
        if not alanlar:
            return {"basarili": False, "mesaj": "Güncellenecek alan bulunamadı."}
        degerler.append(egitmen_id)
        self.db.cursor.execute(f"UPDATE egitmenler SET {', '.join(alanlar)} WHERE egitmen_id = ?", degerler)
        self.db.conn.commit()
        return {"basarili": True, "mesaj": "Eğitmen bilgileri güncellendi."}

    def sil(self, egitmen_id: int) -> Dict:
        """Eğitmeni siler. Aktif kursu varsa silme engellenir."""
        self.db.cursor.execute("SELECT COUNT(*) as sayi FROM kurslar WHERE egitmen_id = ?", (egitmen_id,))
        if self.db.cursor.fetchone()["sayi"] > 0:
            return {"basarili": False, "mesaj": "Bu eğitmenin aktif kursları var. Önce kursları silin."}
        self.db.cursor.execute("DELETE FROM egitmenler WHERE egitmen_id = ?", (egitmen_id,))
        self.db.conn.commit()
        return {"basarili": True, "mesaj": "Eğitmen silindi."}

    def kurslari_getir(self, egitmen_id: int) -> List[Dict]:
        """Eğitmenin verdiği tüm kursları listeler."""
        self.db.cursor.execute("SELECT * FROM kurslar WHERE egitmen_id = ?", (egitmen_id,))
        return [dict(satir) for satir in self.db.cursor.fetchall()]


# ══════════════════════════════════════════════════════════════
#  ANA SINIF 2: KURS
# ══════════════════════════════════════════════════════════════

class Kurs:
    """
    Kurs sınıfı - Platformdaki kursları yönetir.

    Özellikler:
        kurs_adi (str), aciklama (str), egitmen_id (int),
        kontenjan (int), kategori (str), seviye (str)

    Metodlar:
        ekle()               - Yeni kurs oluşturur
        getir()              - Kurs detaylarını getirir
        listele()            - Kursları listeler (filtreleme destekli)
        ogrenci_kaydet()     - Öğrenciyi kursa kaydeder
        ogrenci_cikar()      - Öğrenciyi kurstan çıkarır
        kayitli_ogrenciler() - Kursa kayıtlı öğrencileri listeler
        guncelle()           - Kurs bilgilerini günceller
        sil()                - Kursu siler
    """

    def __init__(self, db: Veritabani):
        """Kurs yöneticisini başlatır."""
        self.db = db

    def ekle(self, kurs_adi: str, egitmen_id: int, kontenjan: int = 30,
             aciklama: str = "", kategori: str = "Genel", seviye: str = "Başlangıç",
             gun: str = "", baslangic_saati: str = "", bitis_saati: str = "",
             format: str = "Canlı", platform: str = "ByTeach Live", ders_linki: str = "") -> Dict:
        """Yeni kurs oluşturur."""
        try:
            self.db.cursor.execute(
                """INSERT INTO kurslar (kurs_adi, aciklama, egitmen_id, kontenjan, kategori, seviye, gun, baslangic_saati, bitis_saati, format, platform, ders_linki)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (kurs_adi, aciklama, egitmen_id, kontenjan, kategori, seviye, gun, baslangic_saati, bitis_saati, format, platform, ders_linki)
            )
            self.db.conn.commit()
            return {"basarili": True, "kurs_id": self.db.cursor.lastrowid,
                    "mesaj": f"'{kurs_adi}' kursu oluşturuldu."}
        except Exception as hata:
            return {"basarili": False, "mesaj": str(hata)}

    def getir(self, kurs_id: int) -> Optional[Dict]:
        """Kurs detaylarını eğitmen bilgileriyle birlikte getirir."""
        self.db.cursor.execute("""
            SELECT k.*, e.ad || ' ' || e.soyad AS egitmen_adi, e.uzmanlik AS egitmen_uzmanlik
            FROM kurslar k
            JOIN egitmenler e ON k.egitmen_id = e.egitmen_id
            WHERE k.kurs_id = ?
        """, (kurs_id,))
        satir = self.db.cursor.fetchone()
        return dict(satir) if satir else None

    def listele(self, kategori: str = None, seviye: str = None) -> List[Dict]:
        """Kursları listeler. Kategori ve seviyeye göre filtreleme yapılabilir."""
        sorgu = """
            SELECT k.*, e.ad || ' ' || e.soyad AS egitmen_adi
            FROM kurslar k JOIN egitmenler e ON k.egitmen_id = e.egitmen_id WHERE 1=1
        """
        parametreler = []
        if kategori:
            sorgu += " AND k.kategori = ?"
            parametreler.append(kategori)
        if seviye:
            sorgu += " AND k.seviye = ?"
            parametreler.append(seviye)
        sorgu += " ORDER BY k.kurs_adi"
        self.db.cursor.execute(sorgu, parametreler)
        return [dict(satir) for satir in self.db.cursor.fetchall()]

    def ogrenci_kaydet(self, kurs_id: int, ogrenci_id: int) -> Dict:
        """
        Öğrenciyi kursa kaydeder.
        Kontroller: Kurs var mı? Kontenjan dolu mu? Zaten kayıtlı mı?
        """
        kurs = self.getir(kurs_id)
        if not kurs:
            return {"basarili": False, "mesaj": "Kurs bulunamadı."}
        if kurs["kayitli_ogrenci_sayisi"] >= kurs["kontenjan"]:
            return {"basarili": False, "mesaj": "Kurs kontenjanı dolu."}
        try:
            self.db.cursor.execute("INSERT INTO kayitlar (ogrenci_id, kurs_id) VALUES (?, ?)", (ogrenci_id, kurs_id))
            self.db.cursor.execute("UPDATE kurslar SET kayitli_ogrenci_sayisi = kayitli_ogrenci_sayisi + 1 WHERE kurs_id = ?", (kurs_id,))
            self.db.conn.commit()
            return {"basarili": True, "mesaj": "Öğrenci kursa kaydedildi."}
        except sqlite3.IntegrityError:
            return {"basarili": False, "mesaj": "Öğrenci zaten bu kursa kayıtlı."}

    def ogrenci_cikar(self, kurs_id: int, ogrenci_id: int) -> Dict:
        """Öğrenciyi kurstan çıkarır ve kayıtlı sayısını günceller."""
        self.db.cursor.execute("DELETE FROM kayitlar WHERE ogrenci_id = ? AND kurs_id = ?", (ogrenci_id, kurs_id))
        if self.db.cursor.rowcount > 0:
            self.db.cursor.execute("UPDATE kurslar SET kayitli_ogrenci_sayisi = kayitli_ogrenci_sayisi - 1 WHERE kurs_id = ?", (kurs_id,))
            self.db.conn.commit()
            return {"basarili": True, "mesaj": "Öğrenci kurstan çıkarıldı."}
        return {"basarili": False, "mesaj": "Kayıt bulunamadı."}

    def kayitli_ogrenciler(self, kurs_id: int) -> List[Dict]:
        """Kursa kayıtlı tüm öğrencileri listeler."""
        self.db.cursor.execute("""
            SELECT o.*, ky.kayit_tarihi AS kurs_kayit_tarihi, ky.ilerleme
            FROM ogrenciler o JOIN kayitlar ky ON o.ogrenci_id = ky.ogrenci_id
            WHERE ky.kurs_id = ? ORDER BY o.ad
        """, (kurs_id,))
        return [dict(satir) for satir in self.db.cursor.fetchall()]

    def guncelle(self, kurs_id: int, **kwargs) -> Dict:
        """Kurs bilgilerini günceller."""
        alanlar, degerler = [], []
        for anahtar, deger in kwargs.items():
            if anahtar in ("kurs_adi", "aciklama", "kontenjan", "kategori", "seviye", "durum", "gun", "baslangic_saati", "bitis_saati", "format", "platform", "ders_linki"):
                alanlar.append(f"{anahtar} = ?")
                degerler.append(deger)
        if not alanlar:
            return {"basarili": False, "mesaj": "Güncellenecek alan bulunamadı."}
        degerler.append(kurs_id)
        self.db.cursor.execute(f"UPDATE kurslar SET {', '.join(alanlar)} WHERE kurs_id = ?", degerler)
        self.db.conn.commit()
        return {"basarili": True, "mesaj": "Kurs bilgileri güncellendi."}

    def sil(self, kurs_id: int) -> Dict:
        """Kursu ve ilgili tüm kayıtları siler."""
        self.db.cursor.execute("DELETE FROM kayitlar WHERE kurs_id = ?", (kurs_id,))
        self.db.cursor.execute("DELETE FROM kurslar WHERE kurs_id = ?", (kurs_id,))
        self.db.conn.commit()
        return {"basarili": True, "mesaj": "Kurs ve ilgili kayıtlar silindi."}


# ══════════════════════════════════════════════════════════════
#  ANA SINIF 3: ÖĞRENCİ
# ══════════════════════════════════════════════════════════════

class Ogrenci:
    """
    Öğrenci sınıfı - Platformdaki öğrencileri yönetir.

    Özellikler:
        ad (str), soyad (str), email (str), telefon (str)

    Metodlar:
        ekle()         - Yeni öğrenci kaydı oluşturur
        getir()        - Öğrenci bilgilerini getirir
        listele()      - Tüm öğrencileri listeler
        kurs_listesi() - Öğrencinin kayıtlı olduğu kursları listeler
        guncelle()     - Öğrenci bilgilerini günceller
        sil()          - Öğrenciyi ve kurs kayıtlarını siler
    """

    def __init__(self, db: Veritabani):
        """Öğrenci yöneticisini başlatır."""
        self.db = db

    def ekle(self, ad: str, soyad: str, email: str, telefon: str = "") -> Dict:
        """Yeni öğrenci kaydı oluşturur. E-posta benzersiz olmalıdır."""
        try:
            self.db.cursor.execute(
                "INSERT INTO ogrenciler (ad, soyad, email, telefon) VALUES (?, ?, ?, ?)",
                (ad, soyad, email, telefon)
            )
            self.db.conn.commit()
            return {"basarili": True, "ogrenci_id": self.db.cursor.lastrowid,
                    "mesaj": f"{ad} {soyad} öğrenci olarak eklendi."}
        except sqlite3.IntegrityError:
            return {"basarili": False, "mesaj": "Bu e-posta adresi zaten kayıtlı."}

    def getir(self, ogrenci_id: int) -> Optional[Dict]:
        """Belirli bir öğrencinin bilgilerini getirir."""
        self.db.cursor.execute("SELECT * FROM ogrenciler WHERE ogrenci_id = ?", (ogrenci_id,))
        satir = self.db.cursor.fetchone()
        return dict(satir) if satir else None

    def listele(self) -> List[Dict]:
        """Tüm öğrencileri ada göre sıralı listeler."""
        self.db.cursor.execute("SELECT * FROM ogrenciler ORDER BY ad")
        return [dict(satir) for satir in self.db.cursor.fetchall()]

    def kurs_listesi(self, ogrenci_id: int) -> List[Dict]:
        """Öğrencinin kayıtlı olduğu tüm kursları eğitmen bilgileriyle listeler."""
        self.db.cursor.execute("""
            SELECT k.*, e.ad || ' ' || e.soyad AS egitmen_adi,
                   ky.kayit_tarihi AS kurs_kayit_tarihi, ky.ilerleme
            FROM kurslar k
            JOIN kayitlar ky ON k.kurs_id = ky.kurs_id
            JOIN egitmenler e ON k.egitmen_id = e.egitmen_id
            WHERE ky.ogrenci_id = ?
            ORDER BY ky.kayit_tarihi DESC
        """, (ogrenci_id,))
        return [dict(satir) for satir in self.db.cursor.fetchall()]

    def guncelle(self, ogrenci_id: int, **kwargs) -> Dict:
        """Öğrenci bilgilerini günceller. Geçerli alanlar: ad, soyad, email, telefon"""
        alanlar, degerler = [], []
        for anahtar, deger in kwargs.items():
            if anahtar in ("ad", "soyad", "email", "telefon"):
                alanlar.append(f"{anahtar} = ?")
                degerler.append(deger)
        if not alanlar:
            return {"basarili": False, "mesaj": "Güncellenecek alan bulunamadı."}
        degerler.append(ogrenci_id)
        self.db.cursor.execute(f"UPDATE ogrenciler SET {', '.join(alanlar)} WHERE ogrenci_id = ?", degerler)
        self.db.conn.commit()
        return {"basarili": True, "mesaj": "Öğrenci bilgileri güncellendi."}

    def sil(self, ogrenci_id: int) -> Dict:
        """Öğrenciyi ve tüm kurs kayıtlarını siler."""
        self.db.cursor.execute("DELETE FROM kayitlar WHERE ogrenci_id = ?", (ogrenci_id,))
        self.db.cursor.execute("DELETE FROM ogrenciler WHERE ogrenci_id = ?", (ogrenci_id,))
        self.db.conn.commit()
        return {"basarili": True, "mesaj": "Öğrenci ve ilgili kayıtlar silindi."}


# ══════════════════════════════════════════════════════════════
#  YARDIMCI SINIF 2: İSTATİSTİK YÖNETİCİSİ
# ══════════════════════════════════════════════════════════════

class IstatistikYoneticisi:
    """
    Platform geneli istatistikleri hesaplar.

    Metodlar:
        genel_istatistikler() - Toplam sayılar ve dağılımları döndürür
    """

    def __init__(self, db: Veritabani):
        """İstatistik yöneticisini başlatır."""
        self.db = db

    def genel_istatistikler(self) -> Dict:
        """
        Platform genelindeki istatistikleri hesaplar ve döndürür.

        Döndürür:
            dict: toplam_egitmen, toplam_kurs, toplam_ogrenci,
                  toplam_kayit, kategori_dagilimi, seviye_dagilimi
        """
        istatistikler = {}

        self.db.cursor.execute("SELECT COUNT(*) AS sayi FROM egitmenler")
        istatistikler["toplam_egitmen"] = self.db.cursor.fetchone()["sayi"]

        self.db.cursor.execute("SELECT COUNT(*) AS sayi FROM kurslar")
        istatistikler["toplam_kurs"] = self.db.cursor.fetchone()["sayi"]

        self.db.cursor.execute("SELECT COUNT(*) AS sayi FROM ogrenciler")
        istatistikler["toplam_ogrenci"] = self.db.cursor.fetchone()["sayi"]

        self.db.cursor.execute("SELECT COUNT(*) AS sayi FROM kayitlar")
        istatistikler["toplam_kayit"] = self.db.cursor.fetchone()["sayi"]

        self.db.cursor.execute("SELECT kategori, COUNT(*) AS sayi FROM kurslar GROUP BY kategori")
        istatistikler["kategori_dagilimi"] = {s["kategori"]: s["sayi"] for s in self.db.cursor.fetchall()}

        self.db.cursor.execute("SELECT seviye, COUNT(*) AS sayi FROM kurslar GROUP BY seviye")
        istatistikler["seviye_dagilimi"] = {s["seviye"]: s["sayi"] for s in self.db.cursor.fetchall()}

        return istatistikler
