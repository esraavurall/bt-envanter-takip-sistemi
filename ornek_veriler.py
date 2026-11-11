"""Uygulamayı denemek için örnek cihaz kayıtları oluşturur."""

from main import baglan, tablo_olustur

ORNEK_CIHAZLAR = [
    ('BT-001', 'Masaüstü Bilgisayar', 'Bilgi İşlem', 'Aktif'),
    ('BT-002', 'Monitör', 'İnsan Kaynakları', 'Aktif'),
    ('BT-003', 'Yazıcı', 'Yazı İşleri', 'Bakımda'),
]


def main():
    tablo_olustur()
    eklenen = 0
    with baglan() as baglanti:
        for cihaz in ORNEK_CIHAZLAR:
            sonuc = baglanti.execute("""
                INSERT OR IGNORE INTO cihazlar
                (demirbas_no, cihaz_turu, birim, durum)
                VALUES (?, ?, ?, ?)
            """, cihaz)
            eklenen += sonuc.rowcount
    print(f'{eklenen} örnek cihaz eklendi.')


if __name__ == '__main__':
    main()
