# Telegram Bot + Mini App Media Gallery

এটি একটি **সাধারণ, non-explicit Telegram media gallery** template। নিজের/অনুমোদিত channel-এর photo/video-এর জন্য ব্যবহার করুন।

## কীভাবে কাজ করে

1. Bot-এ `/start`
2. `🌐 Open Media Website` বাটন
3. Telegram-এর ভিতরে Mini App খুলবে
4. Bot যেসব channel post দেখতে পায়, সেগুলোর photo/video database-এ জমা হবে
5. Gallery-তে photo/video-এর preview দেখা যাবে
6. `📩 Telegram-এ পাঠান` চাপলে Bot chat-এ selected media পাঠাবে

## খুব গুরুত্বপূর্ণ সীমাবদ্ধতা

Telegram Bot API দিয়ে bot সাধারণভাবে channel-এর পুরোনো সম্পূর্ণ history ইচ্ছামতো পড়ে ফেলতে পারে না। এই template-এ bot admin হওয়ার পর যে photo/video channel post bot পায়, সেগুলো database-এ save করা হয়।

তাই setup-এর পরে test হিসেবে নতুন photo/video channel-এ post করুন।

## Step 1 — Bot token

BotFather থেকে নিজের bot তৈরি করুন এবং `config.py`-তে:

```python
BOT_TOKEN = "YOUR_REAL_BOT_TOKEN"
```

Bot token কাউকে প্রকাশ করবেন না।

## Step 2 — Channel

`config.py`:

```python
CHANNEL = "@YOUR_CHANNEL"
```

Bot-কে channel-এ **administrator** করুন, যাতে channel post update পেতে পারে।

## Step 3 — Website URL

Telegram Mini App-এর জন্য HTTPS URL ব্যবহার করুন:

```python
WEBSITE_URL = "https://YOUR-HTTPS-WEBSITE-URL"
```

লোকাল `http://127.0.0.1:8080` অন্য ফোন থেকে Telegram Mini App হিসেবে ব্যবহার করা যাবে না। Production hosting-এ HTTPS ব্যবহার করুন।

## Step 4 — Install

```bash
pip install -r requirements.txt
```

## Step 5 — Run

```bash
python bot.py
```

এতে bot polling এবং local web server দুটোই চালু হবে।

## Step 6 — Test

1. Bot-এ `/start`
2. `🌐 Open Media Website` চাপুন
3. Website খুলবে
4. Channel-এ একটি নতুন photo/video post দিন
5. আবার gallery refresh করুন
6. `📩 Telegram-এ পাঠান` চাপুন

## Production hosting

Hosting provider-এ Python project deploy করে `gunicorn` দিয়ে web server চালাতে পারেন। উদাহরণ:

```bash
gunicorn -b 0.0.0.0:8080 bot:app_web
```

তবে bot polling-ও একই process-এ চালানোর কারণে কিছু hosting setup-এ আলাদা web service + bot worker লাগতে পারে। সবচেয়ে স্থিতিশীল production setup হলো web app এবং bot worker আলাদা process/service হিসেবে চালানো এবং একই SQLite/database ব্যবহার না করে shared database ব্যবহার করা।

## ফাইলগুলো

- `config.py` — Bot token, channel, website URL
- `bot.py` — Telegram bot + API
- `templates/index.html` — Mini App page
- `static/app.js` — gallery এবং Telegram WebApp button
- `static/style.css` — design
- `requirements.txt` — Python packages
- `README_BN.md` — বাংলা setup guide
