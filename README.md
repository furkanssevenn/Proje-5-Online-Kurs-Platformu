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

## Seven YZ — Wireframe Hologram İnsan Yüzü

AI filmindeki David kafası tarzında, anatomik orantılı mavi hologram yüz:

- Gerçekçi insan kafası (elips + sivri çene)
- **Gözler** — beyaz + mavi iris + pupil + parlama (nefes alır)
- **Burun** — köprü + yuvarlak uç + delikler
- **Ağız** — konuşurken açılır (dudaklar + dişler + iç karanlık)
- **Kaşlar** — eğrisel
- **Kulaklar** — 2 yanda
- **Boyun** — gradient
- **Wireframe ağ** — 8 yatay + 5 dikey yüzey çizgisi (3B eğrilik)
- **Braille dot grid** — arkada kabartmalı noktalar
- **Elektrik arkları** — 8 adet animasyonlu zigzag
- **Merkez glow** — pulse eden ışıltı halesi
- **Hareketli tarama çizgisi** — yukarıdan aşağıya
- Hafif baş sallanışı (yaw)
- HUD: SEVEN.AI v3.0 / DURUM / SYNC %

## Dashboard

- "İyi günler, [ad]!" kartı **sade koyu arka plan** (renk karışıklığı yok)
- Sol kenarda mor-mavi dikey vurgu çizgisi
- 4 istatistik kartı (renkli üst şerit)
- Tam genişlik İstanbul haritası
- Halka doluluk + animasyonlu çubuk grafik
- Hızlı işlemler + son aktiviteler

## 4 Aşamalı Türkçe Konuşma (pyttsx3)

1. **"Merhaba."**
2. **"Ben Seven."**
3. **"ByTeach yapay zeka yardımcınızım."**
4. **"Sizinle tanışmaktan büyük mutluluk duydum."**

Her cümlede ağız hareket eder, sesli konuşmayla senkron.

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
