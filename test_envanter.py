import contextlib
import csv
import io
import os
import tempfile
import unittest
from unittest.mock import patch

import main


class EnvanterTestleri(unittest.TestCase):
    def setUp(self):
        self.klasor = tempfile.TemporaryDirectory()
        self.onceki_db = main.VERITABANI
        main.VERITABANI = os.path.join(self.klasor.name, 'test.db')
        main.tablo_olustur()

    def tearDown(self):
        main.VERITABANI = self.onceki_db
        self.klasor.cleanup()

    def calistir(self, fonksiyon, cevaplar):
        cikti = io.StringIO()
        with patch('builtins.input', side_effect=cevaplar):
            with contextlib.redirect_stdout(cikti):
                fonksiyon()
        return cikti.getvalue()

    def cihaz_ekle(self, no='BT-001', tur='Bilgisayar', birim='Bilgi İşlem', durum='Aktif'):
        return self.calistir(main.cihaz_ekle, [no, tur, birim, durum])

    def test_cihaz_ekleme_ve_listeleme(self):
        self.assertIn('Cihaz kaydedildi', self.cihaz_ekle())
        self.assertIn('BT-001', self.calistir(main.cihazlari_listele, []))

    def test_ayni_demirbas_iki_kez_eklenmez(self):
        self.cihaz_ekle()
        self.assertIn('zaten kayıtlı', self.cihaz_ekle())
        with main.baglan() as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM cihazlar').fetchone()[0], 1)

    def test_gecersiz_durum_kaydedilmez(self):
        self.assertIn('Geçersiz durum', self.cihaz_ekle(durum='Aktif,'))
        with main.baglan() as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM cihazlar').fetchone()[0], 0)

    def test_cihaz_duzenleme(self):
        self.cihaz_ekle()
        self.assertIn('güncellendi', self.calistir(main.cihaz_duzenle, ['BT-001', '', 'İnsan Kaynakları', 'Bakımda']))
        with main.baglan() as db:
            self.assertEqual(db.execute('SELECT cihaz_turu, birim, durum FROM cihazlar').fetchone(),
                             ('Bilgisayar', 'İnsan Kaynakları', 'Bakımda'))

    def test_gecersiz_duzenleme_eski_bilgileri_korur(self):
        self.cihaz_ekle()
        self.assertIn('Güncelleme yapılmadı', self.calistir(main.cihaz_duzenle, ['BT-001', 'Yazıcı', '', 'Yanlış']))
        with main.baglan() as db:
            self.assertEqual(db.execute('SELECT cihaz_turu FROM cihazlar').fetchone()[0], 'Bilgisayar')

    def test_olmayan_cihaz_duzenlenemez(self):
        self.assertIn('bulunamadı', self.calistir(main.cihaz_duzenle, ['BT-999']))

    def test_durum_guncelleme(self):
        self.cihaz_ekle()
        self.calistir(main.durum_guncelle, ['BT-001', 'Arızalı'])
        with main.baglan() as db:
            self.assertEqual(db.execute('SELECT durum FROM cihazlar').fetchone()[0], 'Arızalı')

    def test_birim_filtresi(self):
        self.cihaz_ekle()
        self.assertIn('BT-001', self.calistir(main.cihazlari_filtrele, ['1', 'bilgi işlem']))

    def test_durum_filtresi(self):
        self.cihaz_ekle()
        self.assertIn('BT-001', self.calistir(main.cihazlari_filtrele, ['2', 'Aktif']))

    def test_bakim_kaydi_ve_gecmisi(self):
        self.cihaz_ekle()
        self.assertIn('Bakım kaydı eklendi', self.calistir(
            main.bakim_ekle, ['BT-001', '2026-08-12', 'Fan sesi', 'Fan temizliği']
        ))
        self.assertIn('Fan temizliği', self.calistir(main.bakim_gecmisi, ['BT-001']))

    def test_gecersiz_tarih_reddedilir(self):
        self.cihaz_ekle()
        self.assertIn('Tarih geçersiz', self.calistir(
            main.bakim_ekle, ['BT-001', '2026-02-30', 'Sorun', 'Kontrol']
        ))

    def test_csv_aktar(self):
        self.cihaz_ekle()
        eski = os.getcwd()
        try:
            os.chdir(self.klasor.name)
            self.assertIn('1 cihaz', self.calistir(main.csv_aktar, []))
            with open('envanter_listesi.csv', encoding='utf-8-sig', newline='') as dosya:
                satirlar = list(csv.reader(dosya))
            self.assertEqual(satirlar[0], ['Demirbaş No', 'Cihaz Türü', 'Birim', 'Durum'])
            self.assertEqual(satirlar[1], ['BT-001', 'Bilgisayar', 'Bilgi İşlem', 'Aktif'])
        finally:
            os.chdir(eski)

    def test_bos_liste_csv_olusturmaz(self):
        eski = os.getcwd()
        try:
            os.chdir(self.klasor.name)
            self.assertIn('Aktarılacak cihaz bulunamadı', self.calistir(main.csv_aktar, []))
            self.assertFalse(os.path.exists('envanter_listesi.csv'))
        finally:
            os.chdir(eski)


if __name__ == '__main__':
    unittest.main()
