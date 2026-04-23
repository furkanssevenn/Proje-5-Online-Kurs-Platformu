# ByTeach v11.0 — Çevrimiçi Öğrenme Platformu

## Hızlı Başlangıç

```bash
pip install PyQt5 pyttsx3
python app.py
```

**Not:** Eski `kurs_platformu.db` varsa silin.

## Dosya Yapısı

```
Proje/
├── app.py              # PyQt5 uygulaması (~2000 satır)
├── models.py           # 5 sınıf, SQLite
├── test.py             # 23 test
├── README.md
└── kurs_platformu.db   # SQLite (otomatik)
```



## Dashboard

- "İyi günler, [ad]!" kartı **sade koyu arka plan** (renk karışıklığı yok)
- Sol kenarda mor-mavi dikey vurgu çizgisi
- 4 istatistik kartı (renkli üst şerit)
- Tam genişlik İstanbul haritası
- Halka doluluk + animasyonlu çubuk grafik
- Hızlı işlemler + son aktiviteler





## Özellikler

- Mor/mavi tema
- SHA-256 giriş/üye olma
- Kurs/eğitmen/öğrenci CRUD + arama
- Kurs detay + öğrenci kaydetme
- Öğrenci detay sayfası
- CSV dışa aktarma
- Seven YZ sağ panel (canlı veri sorgulama)
- İstanbul haritası (Boğaz + yakalar + 5 yerleşke)
- Toast bildirimleri, canlı saat
- 23/23 test

## Sınıflar

| Sınıf | Türü |
|-------|------|
| Kurs | Ana |
| Egitmen | Ana |
| Ogrenci | Ana |
| Veritabani | Yardımcı |
| IstatistikYoneticisi | Yardımcı |
