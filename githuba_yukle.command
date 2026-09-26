#!/bin/bash
cd "$(dirname "$0")"

echo "======================================================="
echo "   SET KAMPÜSE HOŞ GELDİN — 7/24 BULUT YÜKLEME ARACI"
echo "======================================================="
echo ""
echo "Bu araç, bu klasördeki tüm paneli GitHub deponuza gönderecektir."
echo ""
read -p "GitHub Depo Bağlantınızı (URL) yapıştırın: " repo_url

if [ -z "$repo_url" ]; then
    echo "Hata: Bir URL girmediniz."
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
    echo "Gönderme sırasında bir hata oluştu. Lütfen GitHub giriş bilgilerinizi kontrol edin."
fi

echo ""
read -p "Çıkmak için Enter'a basın..."
