import sqlite3
from datetime import date

VERITABANI = 'envanter.db'
DURUMLAR = ('Aktif', 'Bakımda', 'Arızalı')


def baglan():
    baglanti = sqlite3.connect(VERITABANI)
    baglanti.execute('PRAGMA foreign_keys = ON')
    return baglanti


def tablo_olustur():
    with baglan() as baglanti:
        baglanti.execute("""
            CREATE TABLE IF NOT EXISTS cihazlar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                demirbas_no TEXT NOT NULL UNIQUE,
                cihaz_turu TEXT NOT NULL,
                birim TEXT NOT NULL,
                durum TEXT NOT NULL
            )
        """)
        baglanti.execute("""
            CREATE TABLE IF NOT EXISTS bakim_kayitlari (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cihaz_id INTEGER NOT NULL,
                tarih TEXT NOT NULL,
                aciklama TEXT NOT NULL,
                yapilan_islem TEXT NOT NULL,
                FOREIGN KEY (cihaz_id) REFERENCES cihazlar(id)
            )
        """)


def kayitlari_yazdir(kayitlar):
    if not kayitlar:
        print('Kayıt bulunamadı.')
        return
    print(f'\n{"Demirbaş No":<18} {"Cihaz Türü":<20} {"Birim":<22} Durum')
    print('-' * 75)
    for no, tur, birim, durum in kayitlar:
        print(f'{no:<18} {tur:<20} {birim:<22} {durum}')


def cihaz_ekle():
    no = input('Demirbaş numarası: ').strip()
    tur = input('Cihaz türü: ').strip()
    birim = input('Birim: ').strip()
    durum = input('Durum (Aktif/Bakımda/Arızalı): ').strip()
    if not no or not tur or not birim:
        print('Demirbaş numarası, cihaz türü ve birim boş bırakılamaz.')
        return
    if durum not in DURUMLAR:
        print('Geçersiz durum. Aktif, Bakımda veya Arızalı yazın.')
        return
    try:
        with baglan() as baglanti:
            baglanti.execute("""
                INSERT INTO cihazlar (demirbas_no, cihaz_turu, birim, durum)
                VALUES (?, ?, ?, ?)
            """, (no, tur, birim, durum))
        print('Cihaz kaydedildi.')
    except sqlite3.IntegrityError:
        print('Bu demirbaş numarası zaten kayıtlı.')


def cihazlari_listele():
    with baglan() as baglanti:
        kayitlar = baglanti.execute("""
            SELECT demirbas_no, cihaz_turu, birim, durum
            FROM cihazlar ORDER BY id
        """).fetchall()
    kayitlari_yazdir(kayitlar)


def cihaz_ara():
    no = input('Aranacak demirbaş numarası: ').strip()
    with baglan() as baglanti:
        kayitlar = baglanti.execute("""
            SELECT demirbas_no, cihaz_turu, birim, durum
            FROM cihazlar WHERE demirbas_no = ?
        """, (no,)).fetchall()
    kayitlari_yazdir(kayitlar)


def durum_guncelle():
    no = input('Demirbaş numarası: ').strip()
    durum = input('Yeni durum (Aktif/Bakımda/Arızalı): ').strip()
    if durum not in DURUMLAR:
        print('Geçersiz durum.')
        return
    with baglan() as baglanti:
        sonuc = baglanti.execute(
            'UPDATE cihazlar SET durum = ? WHERE demirbas_no = ?', (durum, no)
        )
        degisen = sonuc.rowcount
    print('Durum güncellendi.' if degisen else 'Cihaz bulunamadı.')


def cihazlari_filtrele():
    print('1. Birime göre listele')
    print('2. Duruma göre listele')
    secim = input('Seçim: ').strip()
    if secim == '1':
        birim = input('Birim adı: ').strip()
        with baglan() as baglanti:
            kayitlar = baglanti.execute("""
                SELECT demirbas_no, cihaz_turu, birim, durum
                FROM cihazlar ORDER BY id
            """).fetchall()
        kayitlar = [
            k for k in kayitlar
            if k[2].casefold().replace('i\u0307', 'i')
            == birim.casefold().replace('i\u0307', 'i')
        ]
    elif secim == '2':
        durum = input('Durum (Aktif/Bakımda/Arızalı): ').strip()
        if durum not in DURUMLAR:
            print('Geçersiz durum.')
            return
        with baglan() as baglanti:
            kayitlar = baglanti.execute("""
                SELECT demirbas_no, cihaz_turu, birim, durum
                FROM cihazlar WHERE durum = ? ORDER BY id
            """, (durum,)).fetchall()
    else:
        print('Geçersiz seçim.')
        return
    kayitlari_yazdir(kayitlar)


def ozet():
    with baglan() as baglanti:
        toplam = baglanti.execute('SELECT COUNT(*) FROM cihazlar').fetchone()[0]
        durumlar = baglanti.execute(
            'SELECT durum, COUNT(*) FROM cihazlar GROUP BY durum'
        ).fetchall()
    print(f'\nToplam cihaz: {toplam}')
    sayilar = dict(durumlar)
    for durum in DURUMLAR:
        print(f'{durum}: {sayilar.get(durum, 0)}')


def bakim_ekle():
    no = input('Demirbaş numarası: ').strip()
    with baglan() as baglanti:
        cihaz = baglanti.execute(
            'SELECT id FROM cihazlar WHERE demirbas_no = ?', (no,)
        ).fetchone()
    if not cihaz:
        print('Bu demirbaş numarasıyla kayıtlı cihaz bulunamadı.')
        return
    tarih = input('İşlem tarihi (YYYY-AA-GG): ').strip()
    aciklama = input('Arıza / bakım açıklaması: ').strip()
    islem = input('Yapılan işlem: ').strip()
    try:
        if date.fromisoformat(tarih).isoformat() != tarih:
            raise ValueError
    except ValueError:
        print('Tarih geçersiz. Örnek: 2026-08-12')
        return
    if not aciklama or not islem:
        print('Açıklama ve yapılan işlem boş bırakılamaz.')
        return
    with baglan() as baglanti:
        baglanti.execute("""
            INSERT INTO bakim_kayitlari (cihaz_id, tarih, aciklama, yapilan_islem)
            VALUES (?, ?, ?, ?)
        """, (cihaz[0], tarih, aciklama, islem))
    print('Bakım kaydı eklendi.')


def bakim_gecmisi():
    no = input('Demirbaş numarası: ').strip()
    with baglan() as baglanti:
        cihaz = baglanti.execute(
            'SELECT id FROM cihazlar WHERE demirbas_no = ?', (no,)
        ).fetchone()
        if not cihaz:
            print('Cihaz bulunamadı.')
            return
        kayitlar = baglanti.execute("""
            SELECT b.tarih, b.aciklama, b.yapilan_islem
            FROM bakim_kayitlari AS b
            JOIN cihazlar AS c ON b.cihaz_id = c.id
            WHERE c.demirbas_no = ?
            ORDER BY b.tarih DESC, b.id DESC
        """, (no,)).fetchall()
    if not kayitlar:
        print('Bu cihaz için bakım kaydı yok.')
        return
    print(f'\n{no} - Bakım geçmişi')
    for tarih, aciklama, islem in kayitlar:
        print(f'\nTarih: {tarih}')
        print(f'Açıklama: {aciklama}')
        print(f'Yapılan işlem: {islem}')


def main():
    tablo_olustur()
    while True:
        print('\n--- BT Envanter Takip ---')
        print('1. Cihaz ekle')
        print('2. Cihazları listele')
        print('3. Demirbaş numarasıyla ara')
        print('4. Cihaz durumunu güncelle')
        print('5. Birime veya duruma göre listele')
        print('6. Envanter özeti')
        print('7. Bakım kaydı ekle')
        print('8. Cihaz bakım geçmişi')
        print('0. Çıkış')
        secim = input('Seçim: ').strip()
        if secim == '1':
            cihaz_ekle()
        elif secim == '2':
            cihazlari_listele()
        elif secim == '3':
            cihaz_ara()
        elif secim == '4':
            durum_guncelle()
        elif secim == '5':
            cihazlari_filtrele()
        elif secim == '6':
            ozet()
        elif secim == '7':
            bakim_ekle()
        elif secim == '8':
            bakim_gecmisi()
        elif secim == '0':
            print('Program kapatıldı.')
            break
        else:
            print('Geçersiz seçim.')


if __name__ == '__main__':
    main()
