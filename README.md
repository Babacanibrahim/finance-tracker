# 💰 Kişisel Finans Takip Uygulaması

Bu uygulama, kullanıcıların gelir ve giderlerini yönetebilmeleri, bütçe limiti belirleyebilmeleri ve mali durumlarını görselleştirebilmeleri için geliştirilmiş bir **kişisel finans takip sistemidir**.

---

## 🧩 Özellikler

- ✅ Kullanıcı Kayıt, Giriş, Profil Güncelleme
- 🔐 Şifre Sıfırlama (Gizli sorularla)
- 💵 Gelir ve Gider Ekleme / Güncelleme / Silme
- 📊 Aylık / Kategorik Finansal Raporlama
- 📅 Bütçe Limiti Belirleme (Sihirbaz adımlı yapı)
- 🔔 Bildirim Sistemi (Limit aşımı)
- 🧠 Dinamik analizler ve grafiksel özetler
- 👤 Kullanıcıya özel kategori tanımlama
- 🧾 PDF veya Excel çıktısı alma (isteğe bağlı geliştirme)
- 📱 Mobil uyumlu arayüz (Bootstrap ile)

---

## 🛠️ Kullanılan Teknolojiler

| Katman | Teknoloji |
|--------|-----------|
| Backend | Flask, SQLAlchemy |
| Frontend | HTML5, Bootstrap, Jinja2 |
| Veritabanı | SQLite (geliştirme), SQLAlchemy ORM |
| Oturum Yönetimi | Flask Session |
| Şifreleme | passlib (sha256_crypt) |
| Formlar | Flask-WTF |

---

## 🚀 Kurulum

### 1. Reposu Klonla

```bash
git clone https://github.com/kullaniciadi/finance-tracker.git
cd finance-tracker
```

### 2. Sanal Ortam Oluştur & Aktifleştir

```bash
python -m venv venv
source venv/bin/activate       # Linux/Mac
venv\Scripts\activate        # Windows
```

### 3. Gereksinimleri Kur

```bash
pip install -r requirements.txt
```

### 4. Uygulamayı Başlat

```bash
python run.py
```

> Varsayılan olarak `http://localhost:5000` üzerinden çalışır.

---

## 📸 Ekran Görüntüleri

| Giriş Sayfası | Bütçe Sihirbazı |
|---------------|-----------------|
| ![login](screenshots/login.png) | ![wizard](screenshots/wizard_step1.png) |

> `static/screenshots/` klasörüne örnek görseller ekleyebilirsin.

---

## 🛡️ Güvenlik

- Şifreler **hashlenerek** saklanır (SHA-256)
- Formlarda CSRF koruması aktiftir
- Kullanıcı bazlı erişim sınırlamaları uygulanmıştır

---

## 📦 Geliştirilecekler

- [ ] PDF veya Excel dışa aktarma
- [ ] RESTful API desteği (mobil uygulama için)
- [ ] Karanlık tema seçeneği
- [ ] Takvim entegrasyonu (gelir-gider takibi için)
- [ ] Gelir/giderleri QR kod ile içe/dışa aktar

---

## 📄 Lisans

Bu proje bireysel eğitim amaçlı geliştirilmiştir. Lisans belirtilmemiştir.

---

## ✨ Geliştirici

**İbrahim Babacan**  
📧 [E-posta ile ulaş](mailto:ibrahim@example.com)  
🌐 [LinkedIn Profilin (opsiyonel)](https://www.linkedin.com/in/ibrahim-babacan)