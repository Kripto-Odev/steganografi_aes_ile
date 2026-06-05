# 🔐 AES-256 + PVD Steganografi Aracı

> **Kriptolojinin Temelleri** dersi kapsamında geliştirilmiş, AES-256 şifreleme ve PVD (Pixel Value Differencing) steganografi algoritmalarını birleştiren çift katmanlı veri gizleme uygulaması.

**Geliştirenler:** Firdevs Tosun · Şerife Nazlı Ünay · Esma Nur Kökören 

---

## 📌 Proje Hakkında

Bu araç iki güvenlik katmanını birleştirir:

1. **AES-256 Şifreleme** — Gizlenecek veri, steganografi işleminden *önce* 256-bit simetrik anahtarla şifrelenir. Böylece stego-görüntü analiz edilip veriye ulaşılsa bile, AES anahtarı olmadan içerik okunamaz (Kerckhoffs İlkesi).
2. **PVD Steganografi** — Şifreli veri, komşu piksel çiftleri arasındaki fark değerine göre görüntüye gizlenir. LSB'nin aksine PVD, insan gözünün kenar/doku bölgelerindeki değişimlere karşı duyarsızlığından yararlanarak daha yüksek kapasitede, daha az iz bırakarak veri saklar.

---

## 🚀 Özellikler

- AES-256 ile kırılmaz şifreleme katmanı (Fernet kütüphanesi)
- PVD algoritması ile görsel bütünlüğü bozmayan steganografi
- RGB kanallarının her birinde bağımsız veri gömme (3× kapasite)
- Metin (TXT) ve görüntü (IMG) gizleme desteği
- TXT/IMG başlık etiketi ile otomatik veri tipi tanıma
- EOF sonlandırıcı ile temiz ve hızlı veri çıkarma (early-exit)
- Piksel taşma (overflow) kontrolü — renk uzayı 0–255 sınırı korunur
- PSNR, MSE, SSIM kalite metrikleri ile analiz çıktısı
- Yalnızca PNG formatı (kayıpsız sıkıştırma zorunluluğu)

---

## 🛠️ Gereksinimler

```
Python 3.x
Pillow
cryptography (Fernet / AES-256)
numpy
```

Kurulum:

```bash
pip install Pillow cryptography numpy
```
---

## ⚙️ Kullanım

### Veri Gizleme — Encoder

```python
from steganography.steganography import encode

encode(
    cover_image="kapak.png",   # Taşıyıcı görüntü (PNG)
    secret="gizli_mesaj.txt",  # Gizlenecek dosya (.txt veya .png)
    key=b"<256-bit AES anahtariniz>",
    output="stego.png"
)
```

**Encoder akışı:**
1. Gizli veri AES-256 ile şifrelenir
2. `TXT`/`IMG` başlığı + `EOF` sonlandırıcısı eklenerek bit dizisine dönüştürülür
3. PVD döngüsü: görüntü 1×2 piksel blokları halinde taranır
4. Her bloğun piksel farkı (d) hesaplanıp Kuantalama Tablosu'na göre kapasite belirlenir
5. Piksel kaydırma mekanizması ile taşma engellenerek stego-görüntü PNG olarak kaydedilir

### Veri Çözme — Decoder

```python
from steganography.steganography import decode

decode(
    stego_image="stego.png",
    key=b"<256-bit AES anahtariniz>",
    output="cikti"   # .txt veya .png olarak kaydedilir
)
```

**Decoder akışı:**
1. Stego-görüntü 1×2 piksel blokları halinde taranır
2. Her bloktan PVD tablosuna göre gizli bitler çıkarılır
3. EOF bulununca tarama durdurulur (early-exit)
4. İzole edilen veri AES-256 anahtarıyla deşifre edilir
5. Başlık etiketine göre metin ekrana yazdırılır veya görsel PNG olarak kaydedilir


---

## 📊 Performans Sonuçları

| Metrik | Değer | Yorum |
|--------|-------|-------|
| **PSNR** | 39 – 67 dB | 30 dB üstü → insan gözü fark edemez |
| **SSIM** | 0.96 – 1.00 | 1.00'a yakın → yapısal bozulma yok |
| **MSE** | ≈ 0 | Sıfıra yakın → piksel bozulması yok |
| **BER** | 0 | %100 doğrulukla veri geri alındı |

---

## 🔒 Güvenlik Mimarisi

```
Düz Metin / Görüntü
        │
        ▼
  [AES-256 Şifreleme]  ← 256-bit Gizli Anahtar
        │
        ▼
  Şifreli Bayt Dizisi
        │
  TXT/IMG Başlığı + EOF eklenir
        │
        ▼
  [PVD Steganografi]   ← Kapak Görüntüsü (PNG)
        │  1×2 piksel blokları, RGB kanalları
        ▼
  Stego-Görüntü (gözle ayırt edilemez PNG)
```

Çözme işlemi tersine çalışır: PVD → EOF → AES deşifre → orijinal veri.

---

## ⚠️ Önemli Notlar

- Taşıyıcı görüntü **PNG formatında** olmalıdır. JPEG gibi kayıplı formatlar piksel değerlerini değiştirerek gizli veriyi tahrip eder.
- AES anahtarının **tek bir biti bile** yanlış girildiğinde şifre çözülemez.
- Gizlenecek verinin boyutu taşıyıcı görüntünün kapasitesini aşmamalıdır.
- Bu proje **akademik/eğitim** amaçlı geliştirilmiştir.

---
