# 🤖 Crypto Signal Bot - Kurulum Rehberi

## Adım 1: Telegram Bot Oluştur (2 dakika)

1. Telegram'da `@BotFather` aç
2. `/newbot` yaz
3. Bot adı gir: `CryptoSignalBot` (veya istediğin isim)
4. Username gir: `your_crypto_signals_bot` (benzersiz olmalı)
5. Sana bir **TOKEN** verecek → Kopyala

## Adım 2: Telegram Kanalları Oluştur

### Premium Kanal:
1. Telegram'da yeni kanal oluştur
2. İsim: "Crypto Signals Premium 💎"
3. Tür: **Private** (özel)
4. Botunu kanala admin olarak ekle (mesaj gönderme izni ver)

### Ücretsiz Kanal:
1. Telegram'da yeni kanal oluştur
2. İsim: "Crypto Signals Free 📊"
3. Tür: **Public** (herkese açık)
4. Botunu kanala admin olarak ekle

### Kanal ID'lerini Bul:
1. Kanalına bir mesaj at
2. O mesajı `@userinfobot`'a forward et
3. Sana kanal ID'sini verecek (örn: -1001234567890)

## Adım 3: Config Dosyasını Doldur

`config.py` dosyasını aç ve şunları doldur (veya GUI'den gir):

```python
TELEGRAM_BOT_TOKEN = "123456:ABC-DEF..."  # BotFather'dan aldığın token
PREMIUM_CHANNEL_ID = "-1001234567890"      # Premium kanal ID
FREE_CHANNEL_ID = "-1001234567891"         # Ücretsiz kanal ID
```

**NOT: Binance API key'e GEREK YOK!** Public API kullanıyoruz, tamamen ücretsiz.

## Adım 4: Botu Çalıştır

```bash
cd crypto_signal_bot
pip install -r requirements.txt
python bot.py
```

## Adım 5: 7/24 Çalıştırma (VPS)

Botun sürekli çalışması için ucuz bir VPS al:
- **Contabo**: 4.99€/ay
- **Hetzner**: 3.49€/ay
- **DigitalOcean**: 4$/ay

VPS'te:
```bash
# Screen ile arka planda çalıştır
screen -S cryptobot
python bot.py
# Ctrl+A, D ile çık (bot çalışmaya devam eder)
```

---

## 💰 Para Kazanma Stratejisi

### Hafta 1-2: Ücretsiz kanal büyüt
- Reddit, Twitter, TikTok'ta sonuçları paylaş
- Kripto gruplarında kanalını tanıt
- Hedef: 500+ ücretsiz abone

### Hafta 3-4: Premium'u aç
- Ücretsiz kanalda "Premium'da bu sinyal 1 saat önce verildi" yaz
- Fiyat: 29$/ay veya 0.005 BTC/ay
- Hedef: 10-20 premium abone

### Ay 2-3: Ölçekle
- Sonuçları düzenli paylaş (win rate, kar oranı)
- Referral sistemi kur (arkadaş getirene 1 hafta ücretsiz)
- Hedef: 50-100 premium abone = 1500-3000$/ay

---

## ⚠️ Önemli Uyarılar

1. **Garanti yok**: Hiçbir bot %100 doğru sinyal veremez
2. **Disclaimer koy**: "Bu finansal tavsiye değildir, yatırım tavsiyesi değildir"
3. **Şeffaf ol**: Win/loss oranını her zaman göster
4. **Kendi paran ile trade etme**: Bot sinyal verir, sen satarsın. Kendi paranı riske atma.
