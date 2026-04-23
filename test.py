"""
╔══════════════════════════════════════════════════════════════╗
║          ONLINE KURS PLATFORMU - TEST MODÜLÜ                 ║
╠══════════════════════════════════════════════════════════════╣
║  Tüm sistem senaryolarını test eder                          ║
║  23 test senaryosu                                           ║
╚══════════════════════════════════════════════════════════════╝
"""
from models import Veritabani, Egitmen, Kurs, Ogrenci, IstatistikYoneticisi
import os

def testleri_calistir():
    test_db = "test_kurs_platformu.db"
    if os.path.exists(test_db): os.remove(test_db)
    vt = Veritabani(test_db)
    egitmen = Egitmen(vt); kurs = Kurs(vt); ogrenci = Ogrenci(vt); istatistik = IstatistikYoneticisi(vt)
    basarili = basarisiz = 0

    def test(adi, kosul):
        nonlocal basarili, basarisiz
        if kosul: basarili += 1; print(f"  ✅ {adi}")
        else: basarisiz += 1; print(f"  ❌ {adi}")

    print("\n" + "=" * 60)
    print("  ONLINE KURS PLATFORMU - TEST RAPORU")
    print("=" * 60)

    print("\n📚 Eğitmen Testleri:")
    sonuc = egitmen.ekle("Ahmet", "Yılmaz", "ahmet@test.com", "Python")
    test("Eğitmen ekleme", sonuc["basarili"])
    sonuc2 = egitmen.ekle("Test", "Kullanıcı", "ahmet@test.com", "Java")
    test("Aynı e-posta engeli", not sonuc2["basarili"])
    e = egitmen.getir(1)
    test("Eğitmen getirme", e is not None and e["ad"] == "Ahmet")
    test("Eğitmen listeleme", len(egitmen.listele()) == 1)
    test("Eğitmen güncelleme", egitmen.guncelle(1, uzmanlik="Python ve Django")["basarili"])

    print("\n🎓 Kurs Testleri:")
    test("Kurs ekleme", kurs.ekle("Python 101", 1, 30, "Başlangıç", "Programlama", "Başlangıç")["basarili"])
    test("İkinci kurs", kurs.ekle("Django Web", 1, 20, "Web", "Web", "Orta")["basarili"])
    test("Kurs getirme", kurs.getir(1) is not None)
    test("Kurs listeleme", len(kurs.listele()) == 2)
    test("Kategori filtre", len(kurs.listele(kategori="Programlama")) == 1)

    print("\n👤 Öğrenci Testleri:")
    test("Öğrenci ekleme", ogrenci.ekle("Ali", "Veli", "ali@test.com", "555")["basarili"])
    test("İkinci öğrenci", ogrenci.ekle("Ayşe", "Kara", "ayse@test.com")["basarili"])
    test("Öğrenci getirme", ogrenci.getir(1) is not None)

    print("\n📝 Kayıt Testleri:")
    test("Kursa kayıt", kurs.ogrenci_kaydet(1, 1)["basarili"])
    test("Tekrar kayıt engeli", not kurs.ogrenci_kaydet(1, 1)["basarili"])
    test("İkinci öğrenci kayıt", kurs.ogrenci_kaydet(1, 2)["basarili"])
    test("Kayıtlı öğrenci listesi", len(kurs.kayitli_ogrenciler(1)) == 2)
    test("kurs_listesi()", len(ogrenci.kurs_listesi(1)) == 1)
    kurs.ekle("Küçük", 1, 1, "Test", "Test", "Başlangıç")
    kurs.ogrenci_kaydet(3, 1)
    test("Kontenjan kontrolü", not kurs.ogrenci_kaydet(3, 2)["basarili"])

    print("\n🗑️  Silme Testleri:")
    test("Kurstan çıkarma", kurs.ogrenci_cikar(1, 2)["basarili"])
    test("Eğitmen silme engeli", not egitmen.sil(1)["basarili"])

    print("\n📊 İstatistik Testleri:")
    ist = istatistik.genel_istatistikler()
    test("İstatistik hesaplama", ist["toplam_egitmen"] == 1)
    test("Kategori dağılımı", "Programlama" in ist["kategori_dagilimi"])

    print("\n" + "=" * 60)
    print(f"  SONUÇ: {basarili} başarılı / {basarisiz} başarısız / {basarili+basarisiz} toplam")
    print("=" * 60)
    vt.kapat(); os.remove(test_db)

if __name__ == "__main__":
    testleri_calistir()
