# 🎓 ByTeach — Ultra Profesyonel Online Kurs Platformu

PyQt5 + SQLite tabanlı, **tam Türkçe**, **modern masaüstü** online kurs platformu.
Custom QSS teması, gradient kartlar, QtChart grafikleri, dark/light mode, animasyonlu toast bildirimleri.

![PyQt5](https://img.shields.io/badge/PyQt5-5.15-green) ![Python](https://img.shields.io/badge/Python-3.10+-blue) ![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## ✨ Öne Çıkan Özellikler

### 🎨 Modern Masaüstü Arayüz
- **Custom QSS tema** (dark/light, indigo marka rengi)
- **Sidebar navigasyon** + üst bar + stacked content
- **Split-screen giriş ekranı** — gradient hero + sekmeli form
- **Animasyonlu toast bildirimleri** (sağ alt köşede stack)
- **Yıldızlı puanlama** widget'ı (interaktif, gradient dolgu)
- **Progress ring** (yuvarlak ilerleme göstergesi)
- **Kategori kartları** + öne çıkan kurslar grid'i
- **Avatar widget** (ad-soyad baş harfli, gradient)

### 📚 Kurs Sistemi
- Kurs listeleme + arama + kategori/seviye filtreleri
- Detay sayfası (eğitmen, açıklama, kontenjan, fiyat, yorumlar)
- **Kayıt/ayrılma** + kontenjan kontrolü
- **İlerleme takibi** (% bazlı, +25% demo butonu)
- **Yorum + 1-5 yıldız puanlama**
- **Favori toggle** (kalp ikonu)

### 🔐 Kimlik Doğrulama & RBAC
- Kayıt, giriş, profil yönetimi, şifre değiştirme
- **PBKDF2-SHA256** (100k iterasyon) + per-user salt
- Rol Tabanlı Erişim Kontrolü: `admin` / `egitmen` / `ogrenci`
- Her rol için farklı sidebar menüsü ve farklı yetki seti

### 🎯 Yetki Matrisi

| İşlem | Öğrenci | Eğitmen | Admin |
|---|---|---|---|
| Kursları görüntüle | ✅ | ✅ | ✅ |
| Kursa kaydol / ayrıl | ✅ | ❌ | ❌ |
| İlerleme takibi | ✅ | — | — |
| Favorilere ekle | ✅ | — | — |
| Yorum yap & puan ver | ✅ | — | — |
| **Kendi yorumunu sil** | ✅ | ✅ | ✅ |
| **Kurs oluştur** | ❌ | ✅ | ✅ (eğitmen profili gerekir) |
| **Kendi kursunu düzenle/sil** | ❌ | ✅ | ✅ |
| **Kendi kursundaki yorumları sil** | ❌ | ✅ | ✅ |
| **Kurs yayınla / taslağa al** | ❌ | ✅ | ✅ |
| Kayıtlı öğrencileri görme | ❌ | ✅ (kendi kursları) | ✅ |
| **Tüm kursları yönet** | ❌ | ❌ | ✅ |
| **Tüm yorumları moderasyon** | ❌ | ❌ | ✅ |
| Kullanıcı yönetimi | ❌ | ❌ | ✅ |
| Eğitmen ekle/sil | ❌ | ❌ | ✅ |
| Toplu duyuru gönder | ❌ | ❌ | ✅ |
| Sistem logları | ❌ | ❌ | ✅ |

### 👤 Öğrenci Paneli
- 4 stat kartı (kayıtlı / tamamlanan / devam eden / ortalama ilerleme)
- Sekmeli görünüm: Kayıtlı Kurslarım / Favorilerim / Son Bildirimler
- Her kurs için progress bar + tamamlanma rozeti

### 🎓 Eğitmen Paneli (Tam Yetkili)
- Hero kart + 4 stat kartı (toplam kurs, yayında, öğrenci, ⭐ ortalama puan)
- **3 sekmeli yönetim:**
  - 📚 **Kurslarım** — kurs listesi + her kurs için: Görüntüle, **Düzenle**, **Yayınla/Yayından Kaldır**, **Sil**
  - 👥 **Öğrencilerim** — kayıtlı öğrenci tablosu + kurs adı + ilerleme barı + kayıt tarihi
  - 💬 **Yorumlar** — kendi kurslarına gelen tüm yorumlar (her birini silebilir)
- Sağ üstte **"Yeni Kurs Oluştur"** butonu — modal dialog ile yeni kurs ekleme
- Her aksiyon sistem loglarına işleniyor

### 🛡️ Admin Paneli (Genişletilmiş)
- 4 stat kartı (kullanıcı, eğitmen, kurs, kayıt)
- **QtChart pasta grafiği** (kategori dağılımı)
- **QtChart bar grafiği** (seviye dağılımı)
- En popüler kurslar listesi
- **Toplu duyuru gönderme** (rol bazlı hedefleme)
- **Kullanıcı yönetimi** (filtre, aktif/pasif, silme)
- **Eğitmen yönetimi** (kart grid + ekleme formu)
- **🆕 Kurs Yönetimi** — tüm kursları (taslaklar dahil) tablo halinde, kategori/seviye filtreleri + arama, **her satırda Düzenle ve Sil**
- **🆕 Yorum Moderasyonu** — sistemdeki tüm yorumları gör ve uygunsuzları sil
- **Sistem logları** (filterable, INFO/UYARI/HATA chip'leri)

### 🔔 Bildirim Sistemi
- Anlık badge sayısı (üst barda)
- Tip bazlı renk (başarı/hata/uyarı/bilgi)
- Tek tek veya toplu okundu işaretleme
- Okunmamış bildirimler için brand renkli vurgulama

### 📊 İstatistik & Raporlama
- Genel sistem istatistikleri
- Kategori/seviye dağılımı
- En popüler kurslar
- Ortalama ilerleme/puan

---

## 🚀 Hızlı Başlangıç

### Gereksinimler
- Python 3.10+
- pip

### Kurulum

```bash
# 1. Bağımlılıkları yükle
pip install -r requirements.txt

# 2. Uygulamayı çalıştır
python main.py
```

İlk çalıştırmada:
- `data/kurs_platformu.db` SQLite veritabanı oluşturulur
- 6 kullanıcı + 7 kurs demo verisi yüklenir
- `logs/app.log` log dosyası başlatılır

---

## 🔑 Demo Hesaplar

Giriş ekranında **demo butonlarıyla tek tıkla** otomatik doldurulur:

| Rol | Kullanıcı Adı | Şifre |
|---|---|---|
| 🛡️ Admin | `admin` | `admin123` |
| 🎓 Eğitmen (Ahmet) | `ahmet` | `ahmet123` |
| 🎓 Eğitmen (Zeynep) | `zeynep` | `zeynep123` |
| 🎓 Eğitmen (Mehmet) | `mehmet` | `mehmet123` |
| 📖 Öğrenci (Ayşe) | `ayse` | `ayse123` |
| 📖 Öğrenci (Burak) | `burak` | `burak123` |

---

## 📁 Proje Yapısı

```
online_kurs_platformu_pyqt/
│
├── main.py                       # Giriş noktası, login loop
├── models.py                     # Veritabanı katmanı (10 sınıf)
├── theme.py                      # QSS tema (dark/light palet)
├── requirements.txt
├── README.md
│
├── data/
│   └── kurs_platformu.db         # SQLite (otomatik oluşur)
│
├── logs/
│   └── app.log                   # Uygulama logları
│
├── widgets/                      # Yeniden kullanılabilir bileşenler
│   ├── __init__.py
│   ├── modern.py                 # Avatar, StatCard, CourseCard, Toast,
│   │                             #   StarRating, ProgressRing, SearchBar...
│   └── sidebar.py                # Sidebar + LogoWidget + NavButton
│
└── views/                        # Sayfalar (12 ekran)
    ├── __init__.py
    ├── login_view.py             # Split-screen login (Hero + Form)
    ├── main_window.py            # Ana pencere + TopBar
    ├── home_view.py              # Anasayfa (hero + kategoriler + popüler)
    ├── courses_view.py           # Kurs listesi + filtreler
    ├── course_detail_view.py     # Kurs detayı + yorumlar + ilerleme
    ├── student_dashboard.py      # Öğrenci paneli (3 sekme)
    ├── instructor_dashboard.py   # Eğitmen paneli
    ├── admin_view.py             # 4 admin sayfası: AdminView,
    │                             #   AdminUsersView, AdminInstructorsView,
    │                             #   AdminLogsView
    ├── profile_view.py           # Profil + şifre değiştir
    └── notifications_view.py     # Bildirimler
```

---

## 🗄️ Veritabanı Şeması

| Tablo | Açıklama |
|---|---|
| `kullanicilar` | Tüm kullanıcılar — auth + avatar_renk |
| `egitmenler` | Eğitmen profil detayları |
| `ogrenciler` | Öğrenci profili |
| `kurslar` | Kurs bilgileri + kapak_renk (gradient) |
| `kayitlar` | Öğrenci-kurs ilişkisi + ilerleme (0-100) |
| `bolumler`, `dersler` | Kurs içerik yapısı (gelecek özellik için hazır) |
| `yorumlar` | Yorum + 1-5 yıldız puan |
| `favoriler` | Kullanıcı favori kursları |
| `bildirimler` | Sistem bildirimleri (4 tip) |
| `sistem_loglari` | Audit log (INFO/UYARI/HATA) |

Tüm `FOREIGN KEY`'ler aktif, kritik alanlarda `CHECK` constraint'leri var.

---

## 🧩 Test Uyumluluğu

Mevcut `test.py` dosyasındaki sınıf API'si tamamen korunmuştur:

```python
from models import Veritabani, Egitmen, Kurs, Ogrenci, IstatistikYoneticisi

vt = Veritabani(":memory:")
egitmen = Egitmen(vt)
egitmen.ekle("Ali", "Yılmaz", "ali@x.com", "Python")
# ... eski test senaryoları çalışmaya devam eder
vt.kapat()
```

---

## 🎨 Tema & Stil

`theme.py` iki palet sunar:

```python
import theme
qss_dark  = theme.get_qss(dark=True)   # Karanlık tema
qss_light = theme.get_qss(dark=False)  # Aydınlık tema
```

Üst bardaki 🌙/☀️ butonu ile **anlık tema geçişi** yapılır.

### Renk Paleti
- **Marka:** `#6366f1` (indigo)
- **Başarı:** `#10b981`
- **Uyarı:** `#f59e0b`
- **Hata:** `#ef4444`
- **Bilgi:** `#3b82f6`

---

## 🔮 Gelecek Geliştirme Fikirleri

- 🎬 Video oynatıcı entegrasyonu (QtMultimedia)
- 💳 Sanal POS / iyzico entegrasyonu
- 📜 PDF sertifika oluşturma (kurs tamamlandığında)
- 🎯 Quiz/sınav modülü
- 🌍 Çoklu dil desteği (Qt translations)
- 📦 Tek dosya executable (PyInstaller / Nuitka)
- 🎨 Tema editörü (canlı renk önizleme)
- 🖼️ Splash screen + about dialog

---

## 🛠️ Teknolojiler

- **GUI:** PyQt5 5.15 + PyQtChart 5.15
- **Veritabanı:** SQLite (built-in)
- **Hash:** hashlib (PBKDF2-SHA256)
- **Logging:** Python `logging` modülü (dosya + konsol)
- **Font:** Inter / Segoe UI / SF Pro fallback

---

## 📝 Lisans

MIT License — kişisel ve ticari kullanım serbest.

---

## 💡 Notlar

- `seed_demo_verisi()` sadece veritabanı boşsa çalışır
- Çıkış yapıldığında uygulama kapanmaz, **giriş ekranına geri döner**
- Tüm UI metinleri **Türkçedir**
- Çekirdek API (Egitmen/Kurs/Ogrenci/IstatistikYoneticisi) test.py uyumludur

İyi öğrenmeler! 🚀
