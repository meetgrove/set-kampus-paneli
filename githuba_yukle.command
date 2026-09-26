#!/bin/bash
cd "$(dirname "$0")"

echo "======================================================="
echo "   SET KAMPÜSE HOŞ GELDİN — 7/24 BULUT YÜKLEME ARACI"
echo "======================================================="
echo ""

# GitHub CLI kimlik kontrolü
if command -v gh >/dev/null 2>&1; then
    if ! gh auth status >/dev/null 2>&1; then
        echo "GitHub oturumunuz açık görünmüyor."
        echo "Tarayıcınız üzerinden tek tıkla oturum açmak ister misiniz? (Şifre gerekmez)"
        read -p "(E/H): " do_login
        if [[ "$do_login" =~ ^[eEyY]$ ]]; then
            echo ""
            echo "Tarayıcı açılıyor... Lütfen GitHub ekranındaki onay kodunu girip onaylayın:"
            gh auth login -w -p https
            gh auth setup-git
        fi
    else
        gh auth setup-git
    fi
fi

echo ""
read -p "GitHub Depo Bağlantınızı (URL) yapıştırın: " repo_url

if [ -z "$repo_url" ]; then
    echo "Hata: Bir URL girmediniz."
    read -p "Çıkmak için Enter'a basın..."
    exit 1
fi

echo ""
echo "Bağlantı ayarlanıyor: $repo_url"
git remote remove origin 2>/dev/null || true
git remote add origin "$repo_url"
git branch -M main

echo ""
echo "Kodlar GitHub'a gönderiliyor..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "======================================================="
    echo "  ✓ BAŞARILI! Kodlarınız GitHub'a yüklendi."
    echo "  Şimdi Render.com'a girip bu depoyu seçerek 'Deploy' deyin."
    echo "======================================================="
else
    echo ""
    echo "-------------------------------------------------------"
    echo "Şifre Hatası Aldıysanız:"
    echo "GitHub, 2021 yılından beri normal şifre kabul etmemektedir."
    echo "EN KOLAY ÇÖZÜM:"
    echo "1. GitHub deponuza web tarayıcınızdan gidin."
    echo "2. 'uploading an existing file' butonuna tıklayın."
    echo "3. Bu klasördeki tüm dosyaları tarayıcıya sürükleyip bırakın."
    echo "4. 'Commit changes' butonuna basın."
    echo "-------------------------------------------------------"
fi

echo ""
read -p "Çıkmak için Enter'a basın..."
