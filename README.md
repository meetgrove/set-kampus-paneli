# 🚀 SET Kampüse Hoş Geldin — 7/24 Kesintisiz Bulut Paneli

Bu paket, **SET Kampüse Hoş Geldin Festivali** için geliştirilen iki büyük yönetim sistemini (**Ekip Koordinasyon Paneli** ve **Festival Alanı Krokisi Paneli**) bilgisayarınıza bağımlı olmadan, **7/24 internette sürekli açık kalacak şekilde** tek bir adreste birleştirir.

---

## 🌟 Neler İçerir?

1. **Ana Ekip Paneli (`/`):**
   * Canlı Festival Sayaç & Metrikleri
   * Görev Yönetimi (Görev Alma, Tamamlama, Sorumlu Atama)
   * 🎨 **Saha Kozmetik & İçerik Takibi (24 Kalem):** Armut minderler, boyalı variller, yer örtüleri, açık hava turnuva oyunları (Jenga, Langırt, Cornhole) canlı tedarik ve tek tıkla durum güncelleme
   * 🏢 **Sponsorluk & Marka Portalı (16 Firma/Kurum):** E-posta durum takibi, yetkili bilgileri, teklif mektubu
   * Festival Saatlik Program Akışı
   * Canlı Ekip Duyuru Panosu & SMS/WhatsApp Rehberi

2. **Festival Alan Krokisi & Stant Paneli (`/kroki/`):**
   * NKÜ Spor Kompleksi Önü 1:1 ölçekli interaktif uydu haritası
   * Metrik (metre bazlı) stant, çadır, sahne ve etkinlik alanı ekleme/düzenleme
   * Döndürme, taşıma, elektrik ihtiyacı ve sorumlu belirleme
   * Excel / CSV ve Yüksek Çözünürlüklü Plan indirme
   * Paylaşım ve QR Kod üretimi

3. **Mobil PWA Desteği:**
   * Telefonunuzda "Ana Ekrana Ekle" yaptığınızda özel **SET Logolu** bağımsız mobil uygulama olarak çalışır.

---

## ⚡ 3 Adımda 7/24 Ücretsiz Bulut Kurulumu (Render.com)

### 1. Adım: GitHub Deposu Açın
1. [github.com/new](https://github.com/new) adresine gidin.
2. Repository name: `set-kampus-paneli` yazın.
3. "Create repository" butonuna tıklayın.

### 2. Adım: Kodları GitHub'a Gönderin
Terminalden bu klasöre gelip aşağıdaki komutları çalıştırın (veya dosyaları GitHub web arayüzüne sürükleyip bırakın):
```bash
git remote add origin https://github.com/KULLANICI_ADINIZ/set-kampus-paneli.git
git push -u origin main
```

### 3. Adım: Render.com'da 1 Tıkla Yayınlayın
1. [render.com](https://render.com) adresine gidin ve GitHub hesabınızla giriş yapın.
2. Sağ üstten **"New +" -> "Web Service"** seçin.
3. `set-kampus-paneli` deponuzu seçip bağlayın.
4. Ayarları kontrol edin:
   * **Name:** `set-kampus-paneli` (veya istediğiniz bir isim)
   * **Runtime:** `Python`
   * **Build Command:** *(boş bırakın)*
   * **Start Command:** `python3 server.py`
   * **Instance Type:** `Free` (Ücretsiz)
5. **"Deploy Web Service"** butonuna basın!

🎉 **Tebrikler!** 60 saniye içinde Render size kalıcı bir link verecektir:
👉 **`https://set-kampus-paneli.onrender.com`**

Bilgisayarınız kapalıyken dahi tüm ekibiniz bu link üzerinden 7/24 sisteme erişebilir.
