# BT Envanter Takip Sistemi

Bilgi işlem stajında gördüğüm donanım envanteri ve cihaz bakım süreçlerini örnek alarak hazırladığım terminal uygulaması. Cihazların hangi birimde bulunduğunu, güncel durumlarını ve geçmiş bakım işlemlerini kaydetmek için Python ve SQLite kullandım.

## Özellikler

- Demirbaş numarası, cihaz türü, birim ve durum ile cihaz kaydı
- Cihazları listeleme ve demirbaş numarasıyla arama
- Birim ve duruma göre filtreleme
- Cihaz durumunu güncelleme, cihaz türü ve birim bilgilerini düzenleme
- Envanter özeti ve Excel ile açılabilen CSV dışa aktarma
- Cihaza tarih, açıklama ve yapılan işlem bilgisiyle bakım kaydı ekleme
- Cihazın bakım geçmişini görüntüleme

Demirbaş numarası benzersizdir. Bakım kayıtları `cihazlar` tablosuna `cihaz_id` ile bağlanır; bakım geçmişinde `JOIN` kullanılır. Bakım kaydı eklemek cihaz durumunu otomatik değiştirmez.

## Kullanılan teknolojiler

Python 3 ve Python ile birlikte gelen `sqlite3` modülü. Harici paket kurulumu gerekmez.

## Çalıştırma

Proje klasöründe terminal açıp:

```bash
python3 main.py
```

İlk çalıştırmada `envanter.db` otomatik oluşturulur. Veriler program kapandıktan sonra da saklanır.

Örnek kayıtları eklemek için (isteğe bağlı):

```bash
python3 ornek_veriler.py
```

Örnek veri dosyası yalnızca `BT-001`, `BT-002` ve `BT-003` numaralı cihazlar henüz kayıtlı değilse bunları ekler; mevcut cihazları silmez.

## CSV dışa aktarma

Ana menüde `10` seçilerek cihazlar `envanter_listesi.csv` dosyasına aktarılır. Dosya Excel'de açılabilir. Mevcut CSV dosyası varsa yeni dışa aktarma sırasında üzerine yazılır.

## Testler

```bash
python3 -m unittest -v
```

Testler geçici bir SQLite veritabanı kullanır; kendi `envanter.db` dosyanızı değiştirmez.

## Veritabanı

- `cihazlar`: demirbaş numarası, cihaz türü, birim ve durum
- `bakim_kayitlari`: cihaza bağlı tarih, açıklama ve yapılan işlem

Bu proje eğitim amaçlı örnek verilerle hazırlanmıştır; gerçek kurum envanteri içermez.
