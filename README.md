# 🅱️ Bilim Jangi — Telegram Bot + Web App

Bilim sinovi (viktorina) o'yini: B Coin, 1v1 Duel, Kunlik missiyalar va Admin Panel.

> ⚠️ **Muhim izoh — loyiha bosqichi haqida.**
> Bu ZIP — **1+2-bosqich**: to'liq ishlaydigan, ishga tushiriladigan, GitHub+Render'ga
> tayyor holat. Ishlaydigan qismlar:
> - Profil / B Coin / Level, 64 savoldan iborat bank bilan **1v1 Bot bilan Duel**
> - **Kunlik missiyalar** (progress + mukofot olish)
> - **👤 Odam bilan 1v1 Duel** — username/ID/havola orqali chaqirish, navbat bilan
>   10 ta savol, to'g'ri javob +1 B Coin, g'olibga reyting bali
> - **🌍 Ommaviy Duel** — foydalanuvchi (max 50) va admin (max 100) duellari,
>   ishtirokchilar savol qo'shadi, o'z savoliga javob berib bo'lmaydi, 10 daqiqa
>   harakatsizlikdan keyin avtomatik yopiladi, admin dueli fondining 50%i Top 1'ga
> - **👥 Do'stlar** — qidirish, so'rov yuborish/qabul qilish, do'stlar ro'yxati,
>   duelga chaqirish, B Coin sovg'a qilish
> - **🏆 Reyting** — Umumiy / 1v1 / Turnir bo'limlari (Turnir bo'yicha ballar
>   3-bosqichda to'ladi, hozircha bo'lim ishlaydi lekin bo'sh)
> - Responsive Telegram Web App va login qilinadigan **Admin Panel**
>   (Dashboard + Foydalanuvchilar)
>
> To'liq texnik hujjatingizdagi **Turnir, Do'kon, Premium, Vaucher, Mahsulot
> sotish, Sklad, To'lov (screenshot tasdiqlash), Oylik missiyalar, va Admin
> Panelning qolgan bo'limlari (Savollar, Missiyalar, Do'kon, To'lovlar, Reklama,
> Loglar)** — bularning har biri katta tizim, shuning uchun **keyingi ZIP'larda**
> xuddi shu arxitektura ustiga to'liq ishlaydigan holda qo'shiladi.
> Interfeysdagi "🎯 Oylik missiyalar" va "🏅 Turnir" tugmalari hozircha "tez orada"
> degan xabar chiqaradi — bu ataylab shunday, 3-bosqichda haqiqiy funksiyaga
> almashtiriladi.
>
> **Eski (1-3-bosqich) bazadan yangilayotganlar uchun:** kod `users` jadvaliga
> (`wins_1v1`, `duels_played_1v1`, `mass_duel_score`, `turnir_wins`,
> `premium_tier`) va `daily_missions`/`monthly_missions` jadvallariga
> `trigger_event` ustunini avtomatik qo'shadi (ilova ishga tushganda
> `backend/app/database.py` ichidagi yengil migratsiya orqali, qo'lda SQL
> yozish shart emas) va mavjud 3+3 ta missiyani yangi voqea-tizimiga
> moslashtiradi. Yangi 47+47 ta missiya **qo'shiladi**, eskilari o'chirilmaydi
> (key bo'yicha "upsert").

---

## 🆕 4-bosqichda qo'shilganlar — Admin Panelning qolgan barcha bo'limlari

- **❓ Savollar** (`/admin/questions`) — qo'lda savol qo'shish/tahrirlash/
  faollashtirish-o'chirish, matn bo'yicha qidirish, va **"🌐 Internetdan olish"**
  — Open Trivia DB (ochiq, bepul, kalitsiz API) dan 10 ta tasodifiy savol
  tortib, admin ko'rib chiqib tahrirlagach bankka qo'shadi.
- **🎯 Missiyalar** (`/admin/missions`) — endi **50 ta kunlik + 50 ta oylik**
  tayyor missiya bor, barchasi haqiqiy o'yin voqealariga ulangan (to'g'ri javob,
  do'st taklif qilish, duelda g'olib bo'lish, ommaviy duel/turnirga qo'shilish,
  mahsulot sotib olish, sovg'a yuborish). Har kuni shu 50 tadan **3 tasi**, har
  oy 50 tadan **5 tasi** barqaror (kun/oy bo'yicha) tanlanib ko'rsatiladi. Admin
  spec talabiga muvofiq faqat **B Coin mukofoti va faollik holatini** o'zgartira
  oladi.
- **🛒 Do'kon** (`/admin/shop`) — barcha mahsulotlarni (Premium tariflar,
  Vaucher rejalari, ramka/nik/fon/badge, sotuvchi mahsulotlari) narxi, tavsifi
  va maxsus maydonlari (bonus %, vaucher kunlari/mahsulot soni) bo'yicha
  tahrirlash, yashirish yoki olib tashlash.
- **💳 To'lovlar** (`/admin/payments`) — barcha to'lov buyurtmalari tarixi,
  holat bo'yicha filtrlash (kutilmoqda/tekshiruvda/tasdiqlangan/rad etilgan/
  muddati tugagan).
- **📢 Reklama** (`/admin/broadcast`) — matn + ixtiyoriy rasm + ixtiyoriy tugma
  bilan xabarni **barcha faol foydalanuvchilarga** botdan yuboradi, natijada
  necha kishiga yetib borgani ko'rsatiladi.
- **📝 Loglar** (`/admin/logs`) — barcha admin amallari (ban/unban, coin
  o'zgarishi, mahsulot tasdiqlash/rad etish, reklama), xaridlar va to'lov
  qarorlari avtomatik shu yerga yoziladi, amal turi bo'yicha filtrlanadi.

### ⚠️ Bilish kerak: nima hali "qo'lda" boshqariladi

- Bot ichidan `/admin` kabi maxsus buyruqlar hali yo'q — barcha boshqaruv
  brauzerdagi `/admin` panel orqali.
- Do'kon/Missiya bo'limlarida yangi katalog turi yoki tamomila yangi missiya
  turini qo'shish hali kod darajasida (`database/*.py` fayllarida) — admin
  panel orqali faqat mavjudlarini tahrirlash mumkin (bu spec talabiga mos:
  "faqat narx/mukofot belgilash").

---

## 🆕 3-bosqichda qo'shilganlar

- **🏅 Turnir** — Foydalanuvchi (max 100, Top 1) va Admin (max 200, Top 3) turnirlari.
  Har bir ishtirokchi bir xil savollar to'plamiga o'z tezligida javob beradi.
  To'g'ri/xato javob uchun coin o'zgarishi spec bo'yicha (foydalanuvchi: 0.10/0.40,
  admin: 0.15/0.35). Turnir yopilganda Top 1 (yoki Top 3) `turnir_wins` oladi —
  bu "🏆 Reyting → Turnir" bo'limida ko'rinadi.
- **🛒 Do'kon** — Kataloglar: Premium, Vaucher, Ramka, Nik bezagi, Orqa fon, Badge,
  Sotuvchilar. "🏪 Sotuvchilar" katalogi **faqat faol vaucheri bor foydalanuvchilarga**
  ko'rinadi (spec talabi). Har bir foydalanuvchi kuniga 3 tagacha mahsulot
  joylashi mumkin — admin tasdig'idan keyin do'konga chiqadi (`/admin/products`).
- **👑 Premium** — 4 ta tarif (+10/+30/+50/+80% bonus), faqat pulga sotiladi
  (screenshot tasdiqlash orqali).
- **🎟️ Vaucher** — 3/7/30 kunlik (B Coinga) va VIP Plus 30 kunlik (pulga).
  Vaucher "Sotuvchilar" katalogidan xarid qilish limitini beradi (oddiy/pullik).
- **📦 Sklad** — Sotib olingan mahsulotlarni "Qo'llash" yoki "50% B Coinga
  qaytarish" (sotuvchidan hech narsa yechilmaydi).
- **💳 To'lov (screenshot)** — Pulga xarid: Web App karta raqamini ko'rsatadi →
  foydalanuvchi screenshotni **to'g'ridan-to'g'ri botga** yuboradi → bot uni
  tasdiqlovchiga (Premium/VIP uchun admin, oddiy sotuvchi mahsuloti uchun
  sotuvchining o'zi) ✅/❌ tugmalari bilan yuboradi. Sotuvchi rad etsa — buyurtma
  avtomatik adminga yuboriladi. 30 daqiqa ichida screenshot kelmasa buyurtma
  muddati tugaydi.
- **🎯 Oylik missiyalar** — Kunlik bilan bir xil naqsh, davr oy bo'yicha
  hisoblanadi (masalan 100 ta to'g'ri javob, 10 ta do'st, 5 ta duel g'alabasi).

### 💳 To'lov bo'limi uchun qo'shimcha `.env` sozlamalari

`PAYMENT_CARD_NUMBER`, `PAYMENT_CARD_HOLDER`, `PAYMENT_TIMEOUT_MINUTES` —
foydalanuvchilarga ko'rsatiladigan karta va screenshot kutish vaqti.

### ⚠️ 3-bosqichdagi ma'lum soddalashtirish

Vaucher orqali "Sotuvchilar" katalogidan necha marta xarid qilish mumkinligi
(15/60/200/VIP 15) vaucher **muddati davomida qilingan xaridlar soni** orqali
hisoblanadi — bu ishlaydigan va spec'ga mos, lekin "ko'rilgan mahsulotlar soni"
emas, balki "sotib olingan mahsulotlar soni" sifatida amalga oshirilgan (oddiy
ko'rib chiqish cheklanmagan). Agar sizga aynan ko'rish-bo'yicha limit kerak
bo'lsa, xabar bering — buni alohida qo'shib beraman.

---

## 📁 Loyiha tuzilmasi

```
bilim-jangi/
├── backend/
│   └── app/
│       ├── main.py          # FastAPI ilova, health, static, routerlar
│       ├── config.py        # .env sozlamalari
│       ├── database.py      # SQLAlchemy Async + PostgreSQL
│       ├── models.py        # User, Question, DailyMission, ...
│       ├── schemas.py       # Pydantic sxemalar
│       ├── crud.py          # Ma'lumotlar bazasi funksiyalari
│       ├── admin.py         # Admin panel (FastAPI + Jinja2)
│       ├── seed.py          # Savol/missiya bazasini avtomatik to'ldirish
│       ├── api/              # /api/profile, /api/duel/bot, /api/missions
│       └── bot/
│           └── bot.py        # aiogram 3 bot (/start, WebApp tugmalari)
├── frontend/                 # Telegram Web App (HTML/CSS/JS)
├── admin_panel/               # Admin panel shablonlari (Jinja2) va CSS
├── database/
│   ├── questions_seed.py     # 60+ tayyor savol (A/B/C/D)
│   └── missions_seed.py      # 3 ta kunlik missiya shabloni
├── requirements.txt
├── render.yaml
├── .env.example
└── README.md
```

---

## 1️⃣ GitHub'ga qanday yuklash

Telefon orqali ishlayotgan bo'lsangiz, eng qulay yo'l — GitHub'ning veb-saytidagi
**"Upload files"** tugmasi (siz Pydroid3/GitHub veb interfeysidan foydalanishingizni
bilaman, shuning uchun terminal buyruqlarisiz yo'l ham beryapman):

1. https://github.com saytida yangi repository yarating (masalan `bilim-jangi`),
   **Private** yoki **Public** — o'zingiz tanlang.
2. Repository sahifasida **"Add file" → "Upload files"** tugmasini bosing.
3. Ushbu ZIP'ni kompyuter/telefoningizda oching (arxivdan chiqaring) va barcha
   fayl/papkalarni (backend, frontend, database, admin_panel, requirements.txt,
   render.yaml, .env.example, README.md, .gitignore) shu yerga tashlang (drag & drop)
   yoki "choose your files" orqali tanlang.
4. Pastda **"Commit changes"** tugmasini bosing.

Agar terminal/git bilan ishlasangiz:
```bash
git init
git add .
git commit -m "Bilim Jangi — 1-bosqich"
git branch -M main
git remote add origin https://github.com/USERNAME/bilim-jangi.git
git push -u origin main
```

**Diqqat:** `.env` faylini hech qachon yuklamang — faqat `.env.example` ochiq turadi,
haqiqiy `.env` esa faqat Render paneli ichida (Environment Variables) turadi.

---

## 2️⃣ Render'da qanday deploy qilish

### A) `render.yaml` orqali (eng oson — tavsiya etiladi)

1. https://dashboard.render.com → **"New" → "Blueprint"**.
2. GitHub repositoryingizni ulang (`bilim-jangi`).
3. Render `render.yaml` faylini avtomatik topadi va quyidagilarni taklif qiladi:
   - `bilim-jangi` — Web Service (Free plan)
   - `bilim-jangi-db` — PostgreSQL (Free plan)
4. **"Apply"** tugmasini bosing.
5. Render so'raydigan maxfiy qiymatlarni kiriting (BOT_TOKEN, ADMIN_TELEGRAM_ID va
   h.k. — pastdagi 4-bo'limga qarang). `DATABASE_URL` va `SECRET_KEY` avtomatik
   to'ldiriladi.
6. Deploy tugagach, sizga `https://bilim-jangi.onrender.com` kabi domen beriladi.
7. **Muhim:** shu domenni nusxalab, `WEBAPP_URL` environment variable'ga qo'ying
   (Render Dashboard → Service → Environment) va **Manual Deploy → Deploy latest
   commit** orqali qayta ishga tushiring — chunki bot tugmalari shu manzilga bog'lanadi.

### B) Qo'lda (Blueprint ishlamasa)

1. **New → PostgreSQL** — nom bering (`bilim-jangi-db`), Free plan, yarating.
   Yaratilgach, **"Internal Database URL"**ni nusxalab oling.
2. **New → Web Service** — GitHub repo'ni tanlang:
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free
3. **Environment** bo'limida pastdagi barcha o'zgaruvchilarni qo'shing
   (`DATABASE_URL` ga 1-qadamdagi Internal Database URL'ni qo'ying, lekin
   boshini `postgres://` bo'lsa ham muammo yo'q — ilova avtomatik
   `postgresql+asyncpg://` ga o'zgartirib oladi).
4. **Health Check Path:** `/health` deb kiriting.
5. **Create Web Service** — deploy boshlanadi.

---

## 3️⃣ PostgreSQL ulash

- Render'da yaratilgan Postgres'ning **Internal Database URL**'ini `DATABASE_URL`
  o'zgaruvchisiga qo'ying (bir xil Render account ichida bo'lsa, Internal URL
  tezroq va bepul trafik).
- Ilova birinchi marta ishga tushganda (`backend/app/database.py` → `init_models()`)
  barcha jadvallarni (`users`, `questions`, `daily_missions`, ...) **avtomatik**
  yaratadi — qo'lda SQL yozish shart emas.
- Shu bilan bir vaqtda `backend/app/seed.py` avtomatik ishga tushib, agar
  `questions` jadvali bo'sh bo'lsa — `database/questions_seed.py`'dagi 60+ savolni,
  agar `daily_missions` bo'sh bo'lsa — `database/missions_seed.py`'dagi 3 ta
  missiyani bazaga yozadi.
- Lokal (kompyuteringizda) sinab ko'rmoqchi bo'lsangiz, `DATABASE_URL`'ni lokal
  Postgres'ga yo'naltirishingiz mumkin, masalan:
  `postgresql+asyncpg://postgres:postgres@localhost:5432/bilimjangi`

---

## 4️⃣ `.env` to'ldirish

`.env.example` faylini nusxalab `.env` deb saqlang (Render'da esa bu qiymatlar
Dashboard → Environment bo'limida to'g'ridan-to'g'ri kiritiladi, alohida fayl kerak
emas):

| O'zgaruvchi | Tavsif |
|---|---|
| `BOT_TOKEN` | @BotFather'dan olingan bot tokeni |
| `ADMIN_TELEGRAM_ID` | Sizning shaxsiy Telegram ID'ingiz (raqam) |
| `ADMIN_CHANNEL_URL` | "📢 Yangiliklar" tugmasi ochadigan kanal linki |
| `ADMIN_USERNAME` | "🆘 Yordam" tugmasi ochadigan sizning Telegram username'ingiz (@ belgisiz) |
| `START_PHOTO_URL` | `/start` xabarida chiqadigan rasm URL (ixtiyoriy, bo'sh qoldirsa faqat matn chiqadi) |
| `WEBAPP_URL` | Render'dagi asosiy domeningiz, masalan `https://bilim-jangi.onrender.com` |
| `DATABASE_URL` | PostgreSQL ulanish manzili |
| `ADMIN_PANEL_USERNAME` / `ADMIN_PANEL_PASSWORD` | `/admin` panelga kirish login/parol |
| `SECRET_KEY` | Session cookie shifrlash uchun tasodifiy uzun matn |

Bot tokenini olish: Telegram'da **@BotFather** → `/newbot` → nomini va username'ini
kiriting (username `bot` bilan tugashi kerak, masalan `bilim_jangi_bot`).

---

## 5️⃣ UptimeRobot'ni `/health` ga ulash

Render Free Web Service faollik bo'lmasa "uxlab qoladi" — buni oldini olish uchun:

1. https://uptimerobot.com saytida ro'yxatdan o'ting (bepul).
2. **"+ Add New Monitor"** bosing.
3. **Monitor Type:** HTTP(s)
4. **URL:** `https://your-app-name.onrender.com/health`
5. **Monitoring Interval:** 5 daqiqa
6. Saqlang. Endi UptimeRobot har 5 daqiqada `/health` ga so'rov yuborib,
   `{"status": "ok", "service": "bilim-jangi"}` javobini oladi va bot/ilovani
   doim faol holatda ushlab turadi (bot polling ham shu jarayon ichida ishlaydi).

---

## 6️⃣ Admin yaratish

Bu bosqichda admin panel **login/parol** orqali ishlaydi (Telegram ID orqali emas):

1. `.env` (yoki Render Environment) ichida `ADMIN_PANEL_USERNAME` va
   `ADMIN_PANEL_PASSWORD`ni o'zingiz xohlagan qiymatga o'zgartiring.
2. Deploy tugagach, brauzerda: `https://your-app-name.onrender.com/admin/login`
   ga kiring va shu login/parolni kiriting.
3. **Dashboard** — umumiy statistikani ko'rasiz.
4. **Foydalanuvchilar** — Telegram ID/username bo'yicha qidirib, B Coin
   qo'shishingiz/ayirishingiz yoki foydalanuvchini Ban/Unban qilishingiz mumkin.
5. **Mahsulotlar** (`/admin/products`) — foydalanuvchilar joylagan mahsulotlarni
   tasdiqlash yoki rad etish.
6. **Savollar, Missiyalar, Do'kon, To'lovlar, Reklama, Loglar** — yuqoridagi
   navigatsiya paneli orqali barchasiga kirish mumkin (4-bosqich bo'limiga
   qarang).

> **Bot ichidan to'lov tasdiqlash uchun admin sifatida tanilish:** `.env` dagi
> `ADMIN_TELEGRAM_ID`ni o'zingizning shaxsiy Telegram ID'ingizga o'rnating —
> shunda tizim sizni avtomatik admin deb belgilaydi (Premium/VIP to'lovlarini
> tasdiqlash, Admin Duel/Turnir yaratish huquqi shu orqali beriladi). Telegram
> ID'ingizni bilish uchun @userinfobot kabi botlardan foydalanishingiz mumkin.
>
> To'liq huquqli rol tizimi va qolgan Admin Panel bo'limlari (Savollar,
> Missiyalar, Do'kon narxlari, To'lovlar tarixi, Reklama, Loglar) 4-bosqichda
> qo'shiladi.

---

## ▶️ Ishga tushirishni tekshirish

1. Deploy tugagach `https://your-app-name.onrender.com/health` ochib
   `{"status":"ok",...}` chiqishini tekshiring.
2. Botga Telegram'da `/start` yozing — salomlashuv xabari va tugmalar chiqishi kerak.
3. "🧠 Bilim Jangi" tugmasini bosib Web App ochilishini, profil/B Coin/Level
   ko'rinishini va "⚔️ 1v1 Duel"da savollarga javob berib B Coin yig'ilishini
   tekshiring.
4. Kunlik missiyalarda progress oshib, bajarilgach "🎁 Mukofotni olish" tugmasi
   ishlashini tekshiring.

## 🛠️ Lokal ishga tushirish (ixtiyoriy)

```bash
pip install -r requirements.txt
# .env faylni to'ldiring, lokal PostgreSQL ishga tushirilgan bo'lsin
cd backend
python -m uvicorn app.main:app --reload --port 8000
```
Web App: `http://localhost:8000`, Admin: `http://localhost:8000/admin/login`

---

## 🗺️ Keyingi bosqichlar rejasi

- ~~**2-bosqich:** Odam bilan 1v1 Duel, Ommaviy Duel (foydalanuvchi + admin),
  Do'stlar tizimi (so'rov/qidiruv/sovg'a), Reyting (umumiy/1v1/turnir).~~ ✅ Tayyor
- ~~**3-bosqich:** Turnir (foydalanuvchi + admin), Do'kon, Premium (4 tarif),
  Vaucher, Mahsulot sotish, Sklad, To'lov (screenshot tasdiqlash oqimi,
  30 daqiqalik taymer), Oylik missiyalar.~~ ✅ Tayyor
- ~~**4-bosqich:** Admin Panelning qolgan bo'limlari — Savollar banki boshqaruvi
  (qo'shish/tahrirlash/internetdan olish), Missiyalar (50 kunlik + 50 oylik
  ro'yxati va mukofot boshqaruvi), Do'kon narx/katalog boshqaruvi, Premium/Vaucher
  narxlarini tahrirlash, To'lovlar tarixi, Reklama (broadcast — barcha
  foydalanuvchilarga xabar), Loglar (admin amallari, xaridlar, coin
  o'zgarishlari tarixi).~~ ✅ Tayyor

**🎉 Barcha 4 bosqich yakunlandi — loyiha texnik hujjatingizdagi barcha
funksiyalar bilan to'liq ishlaydigan holatda.**

## 🧩 2-bosqichda qo'shilgan API'lar

- `POST /api/duel/human/create`, `/join`, `GET /state/{code}`, `POST /answer`
- `POST /api/mass-duel/create`, `/join`, `GET /list`, `GET /{code}`,
  `POST /question/add`, `GET /{code}/next-question`, `POST /answer`, `POST /close`
- `GET/POST /api/friends/...` (list, incoming, outgoing, search, request, respond, gift)
- `GET /api/ranking/{umumiy|1v1|turnir}`

## 🧩 3-bosqichda qo'shilgan yangi API'lar (ma'lumot uchun)

- `POST /api/tournament/create`, `/join`, `GET /list`, `GET /{code}`,
  `GET /{code}/question`, `POST /answer`, `POST /close`
- `GET /api/shop/products`, `GET /product/{id}`, `POST /products/submit`,
  `POST /purchase`, `GET /inventory/{telegram_id}`, `POST /inventory/apply`,
  `POST /inventory/refund`
- `GET /api/payment/status/{order_id}`
- `GET/POST /api/missions/monthly/...`
- Admin: `GET /admin/products`, `POST /admin/products/{id}/approve`,
  `POST /admin/products/{id}/reject`

Har bir keyingi ZIP shu loyihaning **davomi** bo'ladi (mavjud fayllarga qo'shiladi,
buzilmaydi) va yana to'liq ishlaydigan, placeholder'siz holatda beriladi.
