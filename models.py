"""
═══════════════════════════════════════════════════════════════════════════
  ONLINE KURS PLATFORMU — VERİ KATMANI (models.py)
  Ultra Profesyonel Masaüstü Sürümü · PyQt5
═══════════════════════════════════════════════════════════════════════════

  • SQLite tabanlı, dosya-temelli veritabanı
  • Tam Türkçe sınıf API'si (test.py uyumluluğu korunmuştur)
  • PBKDF2-SHA256 (100.000 iterasyon) parola hashleme + per-user salt
  • RBAC: admin / egitmen / ogrenci
  • Audit log (sistem_loglari)
  • Bildirim, favori, yorum, ilerleme takibi
"""
from __future__ import annotations

import hashlib
import os
import secrets
import sqlite3
from datetime import datetime
from typing import Optional


# ═════════════════════════════════════════════════════════════════════════
#  VERİTABANI
# ═════════════════════════════════════════════════════════════════════════
class Veritabani:
    """SQLite bağlantısını yönetir, şemayı kurar."""

    SEMA = """
    CREATE TABLE IF NOT EXISTS kullanicilar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kullanici_adi TEXT UNIQUE NOT NULL,
        eposta        TEXT UNIQUE NOT NULL,
        sifre_hash    TEXT NOT NULL,
        sifre_tuz     TEXT NOT NULL,
        ad            TEXT,
        soyad         TEXT,
        rol           TEXT NOT NULL DEFAULT 'ogrenci'
                       CHECK(rol IN ('admin','egitmen','ogrenci')),
        biyografi     TEXT,
        avatar_renk   TEXT,
        aktif         INTEGER DEFAULT 1,
        kayit_tarihi  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        son_giris     TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS egitmenler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kullanici_id  INTEGER UNIQUE,
        ad            TEXT NOT NULL,
        soyad         TEXT NOT NULL,
        eposta        TEXT UNIQUE NOT NULL,
        uzmanlik      TEXT,
        biyografi     TEXT,
        kayit_tarihi  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(kullanici_id) REFERENCES kullanicilar(id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS ogrenciler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kullanici_id  INTEGER UNIQUE,
        ad            TEXT NOT NULL,
        soyad         TEXT NOT NULL,
        eposta        TEXT UNIQUE NOT NULL,
        kayit_tarihi  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(kullanici_id) REFERENCES kullanicilar(id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS kurslar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ad            TEXT NOT NULL,
        aciklama      TEXT,
        egitmen_id    INTEGER NOT NULL,
        kategori      TEXT DEFAULT 'Genel',
        seviye        TEXT DEFAULT 'Başlangıç'
                       CHECK(seviye IN ('Başlangıç','Orta','İleri')),
        kontenjan     INTEGER DEFAULT 30,
        fiyat         REAL DEFAULT 0,
        kapak_renk    TEXT,
        yayinda       INTEGER DEFAULT 1,
        olusturulma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(egitmen_id) REFERENCES egitmenler(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS kayitlar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kurs_id       INTEGER NOT NULL,
        ogrenci_id    INTEGER NOT NULL,
        ilerleme      INTEGER DEFAULT 0 CHECK(ilerleme BETWEEN 0 AND 100),
        kayit_tarihi  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(kurs_id, ogrenci_id),
        FOREIGN KEY(kurs_id)    REFERENCES kurslar(id)    ON DELETE CASCADE,
        FOREIGN KEY(ogrenci_id) REFERENCES ogrenciler(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS bolumler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kurs_id  INTEGER NOT NULL,
        ad       TEXT NOT NULL,
        sira     INTEGER DEFAULT 0,
        FOREIGN KEY(kurs_id) REFERENCES kurslar(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS dersler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bolum_id  INTEGER NOT NULL,
        ad        TEXT NOT NULL,
        icerik    TEXT,
        sure_dk   INTEGER DEFAULT 10,
        sira      INTEGER DEFAULT 0,
        FOREIGN KEY(bolum_id) REFERENCES bolumler(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS yorumlar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kurs_id      INTEGER NOT NULL,
        kullanici_id INTEGER NOT NULL,
        puan         INTEGER NOT NULL CHECK(puan BETWEEN 1 AND 5),
        mesaj        TEXT,
        tarih        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(kurs_id)      REFERENCES kurslar(id)     ON DELETE CASCADE,
        FOREIGN KEY(kullanici_id) REFERENCES kullanicilar(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS favoriler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kurs_id      INTEGER NOT NULL,
        kullanici_id INTEGER NOT NULL,
        tarih        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(kurs_id, kullanici_id),
        FOREIGN KEY(kurs_id)      REFERENCES kurslar(id)      ON DELETE CASCADE,
        FOREIGN KEY(kullanici_id) REFERENCES kullanicilar(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS bildirimler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kullanici_id INTEGER NOT NULL,
        baslik       TEXT NOT NULL,
        mesaj        TEXT,
        tip          TEXT DEFAULT 'bilgi'
                      CHECK(tip IN ('bilgi','basari','uyari','hata')),
        okundu       INTEGER DEFAULT 0,
        tarih        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(kullanici_id) REFERENCES kullanicilar(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS sistem_loglari (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        seviye       TEXT NOT NULL,
        kaynak       TEXT NOT NULL,
        mesaj        TEXT NOT NULL,
        kullanici_id INTEGER,
        ip           TEXT,
        tarih        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    def __init__(self, db_yolu: str = "data/kurs_platformu.db"):
        self.db_yolu = db_yolu
        if db_yolu != ":memory:":
            os.makedirs(os.path.dirname(os.path.abspath(db_yolu)) or ".", exist_ok=True)
        self.baglanti = sqlite3.connect(db_yolu, check_same_thread=False)
        self.baglanti.row_factory = sqlite3.Row
        self.baglanti.execute("PRAGMA foreign_keys = ON")
        self._sema_olustur()

    def _sema_olustur(self):
        self.baglanti.executescript(self.SEMA)
        self.baglanti.commit()

    def kapat(self):
        try:
            self.baglanti.close()
        except Exception:
            pass


# ═════════════════════════════════════════════════════════════════════════
#  KULLANICI (auth)
# ═════════════════════════════════════════════════════════════════════════
class Kullanici:
    AVATAR_RENKLERI = [
        "#6366f1", "#8b5cf6", "#ec4899", "#f43f5e",
        "#ef4444", "#f97316", "#eab308", "#22c55e",
        "#10b981", "#14b8a6", "#06b6d4", "#3b82f6",
    ]

    def __init__(self, vt: Veritabani):
        self.vt = vt

    @staticmethod
    def _hashle(sifre: str, tuz: str) -> str:
        return hashlib.pbkdf2_hmac(
            "sha256", sifre.encode("utf-8"), tuz.encode("utf-8"), 100_000
        ).hex()

    @classmethod
    def _renk_sec(cls, kullanici_adi: str) -> str:
        i = sum(ord(c) for c in kullanici_adi) % len(cls.AVATAR_RENKLERI)
        return cls.AVATAR_RENKLERI[i]

    def kaydol(self, ad: str, soyad: str, kullanici_adi: str,
               eposta: str, sifre: str, rol: str = "ogrenci",
               biyografi: str = "") -> dict:
        if len(sifre) < 6:
            return {"basarili": False, "mesaj": "Şifre en az 6 karakter olmalı."}
        if rol not in ("admin", "egitmen", "ogrenci"):
            return {"basarili": False, "mesaj": "Geçersiz rol."}

        tuz = secrets.token_hex(16)
        sifre_hash = self._hashle(sifre, tuz)
        renk = self._renk_sec(kullanici_adi)
        c = self.vt.baglanti.cursor()
        try:
            c.execute("""INSERT INTO kullanicilar
                (kullanici_adi, eposta, sifre_hash, sifre_tuz,
                 ad, soyad, rol, biyografi, avatar_renk)
                VALUES (?,?,?,?,?,?,?,?,?)""",
                (kullanici_adi, eposta.lower(), sifre_hash, tuz,
                 ad, soyad, rol, biyografi, renk))
            uid = c.lastrowid

            # Role bağlı eğitmen/öğrenci satırı
            if rol == "egitmen":
                c.execute("""INSERT INTO egitmenler
                    (kullanici_id, ad, soyad, eposta, uzmanlik)
                    VALUES (?,?,?,?,?)""",
                    (uid, ad, soyad, eposta.lower(), "Henüz belirtilmedi"))
            elif rol == "ogrenci":
                c.execute("""INSERT INTO ogrenciler
                    (kullanici_id, ad, soyad, eposta) VALUES (?,?,?,?)""",
                    (uid, ad, soyad, eposta.lower()))

            self.vt.baglanti.commit()
            return {"basarili": True, "id": uid, "mesaj": "Kayıt başarılı."}
        except sqlite3.IntegrityError as e:
            mesaj = "Kullanıcı adı veya e-posta zaten kullanılıyor." \
                if "UNIQUE" in str(e) else f"Hata: {e}"
            return {"basarili": False, "mesaj": mesaj}

    def giris(self, kullanici_adi_veya_eposta: str,
              sifre: str) -> Optional[dict]:
        c = self.vt.baglanti.cursor()
        c.execute("""SELECT * FROM kullanicilar
                     WHERE (kullanici_adi = ? OR eposta = ?) AND aktif = 1""",
                  (kullanici_adi_veya_eposta,
                   kullanici_adi_veya_eposta.lower()))
        row = c.fetchone()
        if not row or self._hashle(sifre, row["sifre_tuz"]) != row["sifre_hash"]:
            return None
        c.execute("UPDATE kullanicilar SET son_giris = CURRENT_TIMESTAMP WHERE id = ?",
                  (row["id"],))
        self.vt.baglanti.commit()
        return dict(row)

    def getir(self, id_: int) -> Optional[dict]:
        c = self.vt.baglanti.cursor()
        c.execute("SELECT * FROM kullanicilar WHERE id = ?", (id_,))
        r = c.fetchone()
        return dict(r) if r else None

    def listele(self, rol: Optional[str] = None) -> list:
        c = self.vt.baglanti.cursor()
        if rol:
            c.execute("SELECT * FROM kullanicilar WHERE rol = ? "
                      "ORDER BY kayit_tarihi DESC", (rol,))
        else:
            c.execute("SELECT * FROM kullanicilar ORDER BY kayit_tarihi DESC")
        return [dict(r) for r in c.fetchall()]

    def guncelle(self, id_: int, **alanlar) -> dict:
        izinli = {"ad", "soyad", "biyografi", "aktif", "rol"}
        guncellenecek = {k: v for k, v in alanlar.items() if k in izinli}
        if not guncellenecek:
            return {"basarili": False, "mesaj": "Güncellenecek alan yok."}
        sql = "UPDATE kullanicilar SET " + \
              ", ".join(f"{k} = ?" for k in guncellenecek) + " WHERE id = ?"
        c = self.vt.baglanti.cursor()
        c.execute(sql, (*guncellenecek.values(), id_))
        self.vt.baglanti.commit()
        return {"basarili": True}

    def sifre_degistir(self, id_: int, eski: str, yeni: str) -> dict:
        if len(yeni) < 6:
            return {"basarili": False, "mesaj": "Yeni şifre en az 6 karakter olmalı."}
        c = self.vt.baglanti.cursor()
        c.execute("SELECT sifre_hash, sifre_tuz FROM kullanicilar WHERE id = ?", (id_,))
        r = c.fetchone()
        if not r:
            return {"basarili": False, "mesaj": "Kullanıcı bulunamadı."}
        if self._hashle(eski, r["sifre_tuz"]) != r["sifre_hash"]:
            return {"basarili": False, "mesaj": "Mevcut şifre hatalı."}
        yeni_tuz = secrets.token_hex(16)
        yeni_hash = self._hashle(yeni, yeni_tuz)
        c.execute("UPDATE kullanicilar SET sifre_hash = ?, sifre_tuz = ? WHERE id = ?",
                  (yeni_hash, yeni_tuz, id_))
        self.vt.baglanti.commit()
        return {"basarili": True, "mesaj": "Şifre değiştirildi."}

    def sil(self, id_: int) -> dict:
        c = self.vt.baglanti.cursor()
        c.execute("DELETE FROM kullanicilar WHERE id = ?", (id_,))
        self.vt.baglanti.commit()
        return {"basarili": c.rowcount > 0}


# ═════════════════════════════════════════════════════════════════════════
#  EĞİTMEN
# ═════════════════════════════════════════════════════════════════════════
class Egitmen:
    def __init__(self, vt: Veritabani):
        self.vt = vt

    def ekle(self, ad: str, soyad: str, eposta: str,
             uzmanlik: str = "", biyografi: str = "",
             kullanici_id: Optional[int] = None) -> dict:
        c = self.vt.baglanti.cursor()
        try:
            c.execute("""INSERT INTO egitmenler
                (kullanici_id, ad, soyad, eposta, uzmanlik, biyografi)
                VALUES (?,?,?,?,?,?)""",
                (kullanici_id, ad, soyad, eposta.lower(), uzmanlik, biyografi))
            self.vt.baglanti.commit()
            return {"basarili": True, "id": c.lastrowid}
        except sqlite3.IntegrityError as e:
            return {"basarili": False, "mesaj": f"Bu e-posta zaten kayıtlı: {e}"}

    def getir(self, id_: int) -> Optional[dict]:
        c = self.vt.baglanti.cursor()
        c.execute("SELECT * FROM egitmenler WHERE id = ?", (id_,))
        r = c.fetchone()
        return dict(r) if r else None

    def listele(self) -> list:
        c = self.vt.baglanti.cursor()
        c.execute("SELECT * FROM egitmenler ORDER BY ad, soyad")
        return [dict(r) for r in c.fetchall()]

    def guncelle(self, id_: int, **alanlar) -> dict:
        izinli = {"ad", "soyad", "eposta", "uzmanlik", "biyografi"}
        guncellenecek = {k: v for k, v in alanlar.items() if k in izinli}
        if not guncellenecek:
            return {"basarili": False, "mesaj": "Güncellenecek alan yok."}
        sql = "UPDATE egitmenler SET " + \
              ", ".join(f"{k} = ?" for k in guncellenecek) + " WHERE id = ?"
        c = self.vt.baglanti.cursor()
        c.execute(sql, (*guncellenecek.values(), id_))
        self.vt.baglanti.commit()
        return {"basarili": True}

    def sil(self, id_: int) -> dict:
        c = self.vt.baglanti.cursor()
        c.execute("DELETE FROM egitmenler WHERE id = ?", (id_,))
        self.vt.baglanti.commit()
        return {"basarili": c.rowcount > 0}

    def kullanici_id_ile_bul(self, kullanici_id: int) -> Optional[dict]:
        c = self.vt.baglanti.cursor()
        c.execute("SELECT * FROM egitmenler WHERE kullanici_id = ?", (kullanici_id,))
        r = c.fetchone()
        return dict(r) if r else None


# ═════════════════════════════════════════════════════════════════════════
#  ÖĞRENCİ
# ═════════════════════════════════════════════════════════════════════════
class Ogrenci:
    def __init__(self, vt: Veritabani):
        self.vt = vt

    def ekle(self, ad: str, soyad: str, eposta: str,
             kullanici_id: Optional[int] = None) -> dict:
        c = self.vt.baglanti.cursor()
        try:
            c.execute("""INSERT INTO ogrenciler
                (kullanici_id, ad, soyad, eposta) VALUES (?,?,?,?)""",
                (kullanici_id, ad, soyad, eposta.lower()))
            self.vt.baglanti.commit()
            return {"basarili": True, "id": c.lastrowid}
        except sqlite3.IntegrityError as e:
            return {"basarili": False, "mesaj": f"E-posta kayıtlı: {e}"}

    def getir(self, id_: int) -> Optional[dict]:
        c = self.vt.baglanti.cursor()
        c.execute("SELECT * FROM ogrenciler WHERE id = ?", (id_,))
        r = c.fetchone()
        return dict(r) if r else None

    def listele(self) -> list:
        c = self.vt.baglanti.cursor()
        c.execute("SELECT * FROM ogrenciler ORDER BY ad, soyad")
        return [dict(r) for r in c.fetchall()]

    def kullanici_id_ile_bul(self, kullanici_id: int) -> Optional[dict]:
        c = self.vt.baglanti.cursor()
        c.execute("SELECT * FROM ogrenciler WHERE kullanici_id = ?", (kullanici_id,))
        r = c.fetchone()
        return dict(r) if r else None

    def kurs_listesi(self, ogrenci_id: int) -> list:
        c = self.vt.baglanti.cursor()
        c.execute("""
            SELECT k.*, ka.ilerleme, ka.kayit_tarihi as kayit_zamani,
                   (ka.ilerleme >= 100) as tamamlandi,
                   e.ad as egitmen_ad, e.soyad as egitmen_soyad
            FROM kayitlar ka
            JOIN kurslar k  ON ka.kurs_id = k.id
            JOIN egitmenler e ON k.egitmen_id = e.id
            WHERE ka.ogrenci_id = ?
            ORDER BY ka.kayit_tarihi DESC
        """, (ogrenci_id,))
        return [dict(r) for r in c.fetchall()]

    def sil(self, id_: int) -> dict:
        c = self.vt.baglanti.cursor()
        c.execute("DELETE FROM ogrenciler WHERE id = ?", (id_,))
        self.vt.baglanti.commit()
        return {"basarili": c.rowcount > 0}


# ═════════════════════════════════════════════════════════════════════════
#  KURS
# ═════════════════════════════════════════════════════════════════════════
class Kurs:
    KAPAK_RENKLERI = [
        "#6366f1,#8b5cf6", "#ec4899,#f43f5e", "#f97316,#eab308",
        "#22c55e,#14b8a6", "#06b6d4,#3b82f6", "#8b5cf6,#ec4899",
        "#10b981,#06b6d4", "#f43f5e,#f97316",
    ]

    def __init__(self, vt: Veritabani):
        self.vt = vt

    def _kapak_renk_sec(self, ad: str) -> str:
        i = sum(ord(c) for c in ad) % len(self.KAPAK_RENKLERI)
        return self.KAPAK_RENKLERI[i]

    def ekle(self, ad: str, egitmen_id: int, kontenjan: int = 30,
             aciklama: str = "", kategori: str = "Genel",
             seviye: str = "Başlangıç", fiyat: float = 0,
             yayinda: int = 1) -> dict:
        c = self.vt.baglanti.cursor()
        c.execute("SELECT 1 FROM egitmenler WHERE id = ?", (egitmen_id,))
        if not c.fetchone():
            return {"basarili": False, "mesaj": "Eğitmen bulunamadı."}

        kapak = self._kapak_renk_sec(ad)
        c.execute("""INSERT INTO kurslar
            (ad, aciklama, egitmen_id, kategori, seviye,
             kontenjan, fiyat, kapak_renk, yayinda)
            VALUES (?,?,?,?,?,?,?,?,?)""",
            (ad, aciklama, egitmen_id, kategori, seviye,
             kontenjan, fiyat, kapak, yayinda))
        self.vt.baglanti.commit()
        return {"basarili": True, "id": c.lastrowid}

    def getir(self, id_: int) -> Optional[dict]:
        c = self.vt.baglanti.cursor()
        c.execute("""
            SELECT k.*,
                   e.ad as egitmen_ad, e.soyad as egitmen_soyad,
                   e.uzmanlik as egitmen_uzmanlik,
                   e.biyografi as egitmen_biyografi,
                   (SELECT COUNT(*) FROM kayitlar WHERE kurs_id = k.id) as kayit_sayisi,
                   (SELECT AVG(puan) FROM yorumlar WHERE kurs_id = k.id) as ort_puan,
                   (SELECT COUNT(*) FROM yorumlar WHERE kurs_id = k.id) as yorum_sayisi
            FROM kurslar k
            JOIN egitmenler e ON k.egitmen_id = e.id
            WHERE k.id = ?
        """, (id_,))
        r = c.fetchone()
        return dict(r) if r else None

    def listele(self, kategori: Optional[str] = None,
                seviye: Optional[str] = None,
                arama: Optional[str] = None,
                yayinda: bool = True) -> list:
        kosullar, parametreler = [], []
        if yayinda:
            kosullar.append("k.yayinda = 1")
        if kategori:
            kosullar.append("k.kategori = ?")
            parametreler.append(kategori)
        if seviye:
            kosullar.append("k.seviye = ?")
            parametreler.append(seviye)
        if arama:
            kosullar.append("(k.ad LIKE ? OR k.aciklama LIKE ?)")
            t = f"%{arama}%"
            parametreler.extend([t, t])
        where = "WHERE " + " AND ".join(kosullar) if kosullar else ""

        c = self.vt.baglanti.cursor()
        c.execute(f"""
            SELECT k.*,
                   e.ad as egitmen_ad, e.soyad as egitmen_soyad,
                   (SELECT COUNT(*) FROM kayitlar WHERE kurs_id = k.id) as kayit_sayisi,
                   (SELECT AVG(puan) FROM yorumlar WHERE kurs_id = k.id) as ort_puan,
                   (SELECT COUNT(*) FROM yorumlar WHERE kurs_id = k.id) as yorum_sayisi
            FROM kurslar k JOIN egitmenler e ON k.egitmen_id = e.id
            {where}
            ORDER BY k.olusturulma_tarihi DESC
        """, parametreler)
        return [dict(r) for r in c.fetchall()]

    def egitmen_kurslari(self, egitmen_id: int) -> list:
        """Belirli bir eğitmenin tüm kursları (yayında ve taslak)."""
        c = self.vt.baglanti.cursor()
        c.execute("""
            SELECT k.*,
                   (SELECT COUNT(*) FROM kayitlar WHERE kurs_id = k.id) as kayit_sayisi,
                   (SELECT AVG(puan) FROM yorumlar WHERE kurs_id = k.id) as ort_puan,
                   (SELECT COUNT(*) FROM yorumlar WHERE kurs_id = k.id) as yorum_sayisi
            FROM kurslar k
            WHERE k.egitmen_id = ?
            ORDER BY k.olusturulma_tarihi DESC
        """, (egitmen_id,))
        return [dict(r) for r in c.fetchall()]

    def sahibi_mi(self, kurs_id: int, kullanici_id: int) -> bool:
        """Bu kullanıcı, bu kursun eğitmeni mi?"""
        c = self.vt.baglanti.cursor()
        c.execute("""
            SELECT 1 FROM kurslar k
            JOIN egitmenler e ON k.egitmen_id = e.id
            WHERE k.id = ? AND e.kullanici_id = ?
        """, (kurs_id, kullanici_id))
        return c.fetchone() is not None

    def guncelle(self, id_: int, **alanlar) -> dict:
        izinli = {"ad", "aciklama", "kategori", "seviye", "kontenjan",
                  "fiyat", "yayinda", "egitmen_id"}
        g = {k: v for k, v in alanlar.items() if k in izinli}
        if not g:
            return {"basarili": False, "mesaj": "Güncellenecek alan yok."}
        sql = "UPDATE kurslar SET " + \
              ", ".join(f"{k} = ?" for k in g) + " WHERE id = ?"
        c = self.vt.baglanti.cursor()
        c.execute(sql, (*g.values(), id_))
        self.vt.baglanti.commit()
        return {"basarili": True}

    def sil(self, id_: int) -> dict:
        c = self.vt.baglanti.cursor()
        c.execute("DELETE FROM kurslar WHERE id = ?", (id_,))
        self.vt.baglanti.commit()
        return {"basarili": c.rowcount > 0}

    def ogrenci_kaydet(self, kurs_id: int, ogrenci_id: int) -> dict:
        c = self.vt.baglanti.cursor()
        c.execute("SELECT kontenjan, "
                  "(SELECT COUNT(*) FROM kayitlar WHERE kurs_id = ?) as mevcut "
                  "FROM kurslar WHERE id = ?", (kurs_id, kurs_id))
        r = c.fetchone()
        if not r:
            return {"basarili": False, "mesaj": "Kurs bulunamadı."}
        if r["mevcut"] >= r["kontenjan"]:
            return {"basarili": False, "mesaj": "Kontenjan dolu."}
        try:
            c.execute("INSERT INTO kayitlar (kurs_id, ogrenci_id) VALUES (?, ?)",
                      (kurs_id, ogrenci_id))
            self.vt.baglanti.commit()
            return {"basarili": True}
        except sqlite3.IntegrityError:
            return {"basarili": False, "mesaj": "Zaten kayıtlısınız."}

    def ogrenci_cikar(self, kurs_id: int, ogrenci_id: int) -> dict:
        c = self.vt.baglanti.cursor()
        c.execute("DELETE FROM kayitlar WHERE kurs_id = ? AND ogrenci_id = ?",
                  (kurs_id, ogrenci_id))
        self.vt.baglanti.commit()
        return {"basarili": c.rowcount > 0}

    def kayitli_ogrenciler(self, kurs_id: int) -> list:
        c = self.vt.baglanti.cursor()
        c.execute("""
            SELECT o.*, ka.ilerleme, ka.kayit_tarihi as kayit_zamani
            FROM kayitlar ka JOIN ogrenciler o ON ka.ogrenci_id = o.id
            WHERE ka.kurs_id = ?
        """, (kurs_id,))
        return [dict(r) for r in c.fetchall()]

    def ilerleme_guncelle(self, kurs_id: int, ogrenci_id: int,
                          yuzde: int) -> dict:
        yuzde = max(0, min(100, yuzde))
        c = self.vt.baglanti.cursor()
        c.execute("""UPDATE kayitlar SET ilerleme = ?
                     WHERE kurs_id = ? AND ogrenci_id = ?""",
                  (yuzde, kurs_id, ogrenci_id))
        self.vt.baglanti.commit()
        return {"basarili": c.rowcount > 0}


# ═════════════════════════════════════════════════════════════════════════
#  YORUM
# ═════════════════════════════════════════════════════════════════════════
class Yorum:
    def __init__(self, vt: Veritabani):
        self.vt = vt

    def ekle(self, kurs_id: int, kullanici_id: int,
             puan: int, mesaj: str = "") -> dict:
        if not 1 <= puan <= 5:
            return {"basarili": False, "mesaj": "Puan 1-5 arası olmalı."}
        c = self.vt.baglanti.cursor()
        c.execute("""INSERT INTO yorumlar (kurs_id, kullanici_id, puan, mesaj)
                     VALUES (?,?,?,?)""",
                  (kurs_id, kullanici_id, puan, mesaj))
        self.vt.baglanti.commit()
        return {"basarili": True, "id": c.lastrowid}

    def kurs_yorumlari(self, kurs_id: int) -> list:
        c = self.vt.baglanti.cursor()
        c.execute("""
            SELECT y.*, k.ad as kullanici_ad, k.soyad as kullanici_soyad,
                   k.kullanici_adi, k.avatar_renk
            FROM yorumlar y JOIN kullanicilar k ON y.kullanici_id = k.id
            WHERE y.kurs_id = ? ORDER BY y.tarih DESC
        """, (kurs_id,))
        return [dict(r) for r in c.fetchall()]

    def tum_yorumlar(self, limit: int = 200) -> list:
        """Admin moderasyonu için tüm yorumlar (en yeni önce)."""
        c = self.vt.baglanti.cursor()
        c.execute("""
            SELECT y.*,
                   k.ad as kullanici_ad, k.soyad as kullanici_soyad,
                   k.kullanici_adi, k.avatar_renk,
                   ku.ad as kurs_ad, ku.id as kurs_id_alias
            FROM yorumlar y
            JOIN kullanicilar k ON y.kullanici_id = k.id
            JOIN kurslar ku     ON y.kurs_id      = ku.id
            ORDER BY y.tarih DESC
            LIMIT ?
        """, (limit,))
        return [dict(r) for r in c.fetchall()]

    def egitmen_yorumlari(self, egitmen_id: int) -> list:
        """Belirli eğitmenin sahibi olduğu kurslara gelen tüm yorumlar."""
        c = self.vt.baglanti.cursor()
        c.execute("""
            SELECT y.*,
                   k.ad as kullanici_ad, k.soyad as kullanici_soyad,
                   k.kullanici_adi, k.avatar_renk,
                   ku.ad as kurs_ad
            FROM yorumlar y
            JOIN kullanicilar k ON y.kullanici_id = k.id
            JOIN kurslar ku     ON y.kurs_id      = ku.id
            WHERE ku.egitmen_id = ?
            ORDER BY y.tarih DESC
        """, (egitmen_id,))
        return [dict(r) for r in c.fetchall()]

    def silebilir_mi(self, yorum_id: int, kullanici: dict) -> bool:
        """Verilen kullanıcı bu yorumu silebilir mi?
        Kurallar:
        - Admin her yorumu silebilir
        - Yorum sahibi kendi yorumunu silebilir
        - Eğitmen kendi kurslarındaki yorumları silebilir
        """
        if kullanici.get("rol") == "admin":
            return True
        c = self.vt.baglanti.cursor()
        c.execute("""SELECT y.kullanici_id, ku.egitmen_id, e.kullanici_id as eg_kul_id
                     FROM yorumlar y
                     JOIN kurslar ku ON y.kurs_id = ku.id
                     JOIN egitmenler e ON ku.egitmen_id = e.id
                     WHERE y.id = ?""", (yorum_id,))
        r = c.fetchone()
        if not r:
            return False
        if r["kullanici_id"] == kullanici["id"]:
            return True
        if kullanici.get("rol") == "egitmen" and r["eg_kul_id"] == kullanici["id"]:
            return True
        return False

    def sil(self, id_: int) -> dict:
        c = self.vt.baglanti.cursor()
        c.execute("DELETE FROM yorumlar WHERE id = ?", (id_,))
        self.vt.baglanti.commit()
        return {"basarili": c.rowcount > 0}


# ═════════════════════════════════════════════════════════════════════════
#  FAVORİ
# ═════════════════════════════════════════════════════════════════════════
class Favori:
    def __init__(self, vt: Veritabani):
        self.vt = vt

    def ekle_cikar(self, kurs_id: int, kullanici_id: int) -> dict:
        c = self.vt.baglanti.cursor()
        c.execute("""SELECT id FROM favoriler
                     WHERE kurs_id = ? AND kullanici_id = ?""",
                  (kurs_id, kullanici_id))
        if c.fetchone():
            c.execute("""DELETE FROM favoriler
                         WHERE kurs_id = ? AND kullanici_id = ?""",
                      (kurs_id, kullanici_id))
            self.vt.baglanti.commit()
            return {"basarili": True, "favori": False}
        c.execute("""INSERT INTO favoriler (kurs_id, kullanici_id)
                     VALUES (?, ?)""", (kurs_id, kullanici_id))
        self.vt.baglanti.commit()
        return {"basarili": True, "favori": True}

    def favori_mi(self, kurs_id: int, kullanici_id: int) -> bool:
        c = self.vt.baglanti.cursor()
        c.execute("""SELECT 1 FROM favoriler
                     WHERE kurs_id = ? AND kullanici_id = ?""",
                  (kurs_id, kullanici_id))
        return c.fetchone() is not None

    def kullanici_favorileri(self, kullanici_id: int) -> list:
        c = self.vt.baglanti.cursor()
        c.execute("""
            SELECT k.*, e.ad as egitmen_ad, e.soyad as egitmen_soyad,
                   (SELECT COUNT(*) FROM kayitlar WHERE kurs_id = k.id) as kayit_sayisi
            FROM favoriler f
            JOIN kurslar k    ON f.kurs_id = k.id
            JOIN egitmenler e ON k.egitmen_id = e.id
            WHERE f.kullanici_id = ?
            ORDER BY f.tarih DESC
        """, (kullanici_id,))
        return [dict(r) for r in c.fetchall()]


# ═════════════════════════════════════════════════════════════════════════
#  BİLDİRİM
# ═════════════════════════════════════════════════════════════════════════
class Bildirim:
    def __init__(self, vt: Veritabani):
        self.vt = vt

    def gonder(self, kullanici_id: int, baslik: str,
               mesaj: str = "", tip: str = "bilgi") -> dict:
        c = self.vt.baglanti.cursor()
        c.execute("""INSERT INTO bildirimler
            (kullanici_id, baslik, mesaj, tip) VALUES (?,?,?,?)""",
            (kullanici_id, baslik, mesaj, tip))
        self.vt.baglanti.commit()
        return {"basarili": True, "id": c.lastrowid}

    def toplu_gonder(self, baslik: str, mesaj: str,
                     tip: str = "bilgi", rol: Optional[str] = None) -> dict:
        c = self.vt.baglanti.cursor()
        if rol:
            c.execute("SELECT id FROM kullanicilar WHERE rol = ? AND aktif = 1", (rol,))
        else:
            c.execute("SELECT id FROM kullanicilar WHERE aktif = 1")
        ids = [r["id"] for r in c.fetchall()]
        for uid in ids:
            c.execute("""INSERT INTO bildirimler
                (kullanici_id, baslik, mesaj, tip) VALUES (?,?,?,?)""",
                (uid, baslik, mesaj, tip))
        self.vt.baglanti.commit()
        return {"basarili": True, "gonderilen": len(ids)}

    def kullanici_bildirimleri(self, kullanici_id: int,
                                sadece_okunmamis: bool = False) -> list:
        c = self.vt.baglanti.cursor()
        sql = "SELECT * FROM bildirimler WHERE kullanici_id = ?"
        if sadece_okunmamis:
            sql += " AND okundu = 0"
        sql += " ORDER BY tarih DESC"
        c.execute(sql, (kullanici_id,))
        return [dict(r) for r in c.fetchall()]

    def okundu_isaretle(self, id_: int) -> dict:
        c = self.vt.baglanti.cursor()
        c.execute("UPDATE bildirimler SET okundu = 1 WHERE id = ?", (id_,))
        self.vt.baglanti.commit()
        return {"basarili": True}

    def tumu_okundu(self, kullanici_id: int) -> dict:
        c = self.vt.baglanti.cursor()
        c.execute("UPDATE bildirimler SET okundu = 1 WHERE kullanici_id = ?",
                  (kullanici_id,))
        self.vt.baglanti.commit()
        return {"basarili": True, "guncellenen": c.rowcount}


# ═════════════════════════════════════════════════════════════════════════
#  LOGGER
# ═════════════════════════════════════════════════════════════════════════
class Logger:
    def __init__(self, vt: Veritabani):
        self.vt = vt

    def log(self, seviye: str, kaynak: str, mesaj: str,
            kullanici_id: Optional[int] = None,
            ip: Optional[str] = None):
        c = self.vt.baglanti.cursor()
        c.execute("""INSERT INTO sistem_loglari
            (seviye, kaynak, mesaj, kullanici_id, ip) VALUES (?,?,?,?,?)""",
            (seviye, kaynak, mesaj, kullanici_id, ip))
        self.vt.baglanti.commit()

    def info(self, kaynak, mesaj, **k): self.log("INFO",  kaynak, mesaj, **k)
    def uyari(self, kaynak, mesaj, **k): self.log("UYARI", kaynak, mesaj, **k)
    def hata(self, kaynak, mesaj, **k):  self.log("HATA",  kaynak, mesaj, **k)

    def son_loglar(self, limit: int = 100,
                   seviye: Optional[str] = None) -> list:
        c = self.vt.baglanti.cursor()
        if seviye:
            c.execute("""SELECT * FROM sistem_loglari
                         WHERE seviye = ? ORDER BY tarih DESC LIMIT ?""",
                      (seviye, limit))
        else:
            c.execute("SELECT * FROM sistem_loglari "
                      "ORDER BY tarih DESC LIMIT ?", (limit,))
        return [dict(r) for r in c.fetchall()]


# ═════════════════════════════════════════════════════════════════════════
#  İSTATİSTİK
# ═════════════════════════════════════════════════════════════════════════
class IstatistikYoneticisi:
    def __init__(self, vt: Veritabani):
        self.vt = vt

    def genel_istatistikler(self) -> dict:
        c = self.vt.baglanti.cursor()

        c.execute("SELECT COUNT(*) FROM egitmenler"); te = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM ogrenciler"); to = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM kurslar");    tk = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM kayitlar");   tka = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM kullanicilar WHERE aktif = 1"); tku = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM yorumlar");   ty = c.fetchone()[0]

        c.execute("SELECT kategori, COUNT(*) c FROM kurslar GROUP BY kategori")
        kat = {r["kategori"]: r["c"] for r in c.fetchall()}

        c.execute("SELECT seviye, COUNT(*) c FROM kurslar GROUP BY seviye")
        sev = {r["seviye"]: r["c"] for r in c.fetchall()}

        c.execute("""
            SELECT k.id, k.ad, COUNT(ka.id) c
            FROM kurslar k LEFT JOIN kayitlar ka ON ka.kurs_id = k.id
            GROUP BY k.id ORDER BY c DESC LIMIT 5
        """)
        en_pop = [dict(r) for r in c.fetchall()]

        c.execute("SELECT AVG(ilerleme) FROM kayitlar")
        ort_ilerleme = c.fetchone()[0] or 0

        c.execute("SELECT AVG(puan) FROM yorumlar")
        ort_puan = c.fetchone()[0] or 0

        return {
            "toplam_egitmen":     te,
            "toplam_ogrenci":     to,
            "toplam_kurs":        tk,
            "toplam_kayit":       tka,
            "toplam_kullanici":   tku,
            "toplam_yorum":       ty,
            "kategori_dagilimi":  kat,
            "seviye_dagilimi":    sev,
            "en_populer_kurslar": en_pop,
            "ortalama_ilerleme":  round(ort_ilerleme, 1),
            "ortalama_puan":      round(ort_puan, 2),
        }

    def egitmen_istatistikleri(self, egitmen_id: int) -> dict:
        """Belirli eğitmenin istatistikleri."""
        c = self.vt.baglanti.cursor()

        c.execute("SELECT COUNT(*) FROM kurslar WHERE egitmen_id = ?", (egitmen_id,))
        toplam_kurs = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM kurslar WHERE egitmen_id = ? AND yayinda = 1",
                  (egitmen_id,))
        yayinda = c.fetchone()[0]

        c.execute("""SELECT COUNT(*) FROM kayitlar ka
                     JOIN kurslar k ON ka.kurs_id = k.id
                     WHERE k.egitmen_id = ?""", (egitmen_id,))
        toplam_ogrenci = c.fetchone()[0]

        c.execute("""SELECT COUNT(*) FROM yorumlar y
                     JOIN kurslar k ON y.kurs_id = k.id
                     WHERE k.egitmen_id = ?""", (egitmen_id,))
        toplam_yorum = c.fetchone()[0]

        c.execute("""SELECT AVG(puan) FROM yorumlar y
                     JOIN kurslar k ON y.kurs_id = k.id
                     WHERE k.egitmen_id = ?""", (egitmen_id,))
        ort_puan = c.fetchone()[0] or 0

        c.execute("""SELECT AVG(ilerleme) FROM kayitlar ka
                     JOIN kurslar k ON ka.kurs_id = k.id
                     WHERE k.egitmen_id = ?""", (egitmen_id,))
        ort_ilerleme = c.fetchone()[0] or 0

        return {
            "toplam_kurs":      toplam_kurs,
            "yayinda":          yayinda,
            "taslak":           toplam_kurs - yayinda,
            "toplam_ogrenci":   toplam_ogrenci,
            "toplam_yorum":     toplam_yorum,
            "ortalama_puan":    round(ort_puan, 2),
            "ortalama_ilerleme": round(ort_ilerleme, 1),
        }
