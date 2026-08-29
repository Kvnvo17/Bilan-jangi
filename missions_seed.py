"""
Bilim Jangi — 4-bosqich: to'liq 50 ta kunlik missiya ro'yxati.

Har bir missiya `trigger_event` orqali haqiqiy o'yin voqealariga ulangan —
foydalanuvchi mos harakatni bajarganda progress avtomatik oshadi:
  correct_answer      — istalgan rejimda to'g'ri javob berish
  invite_friend       — do'stlik so'rovi qabul qilinishi (taklif qiluvchiga)
  duel_win            — Odam bilan 1v1 Duelda g'olib chiqish
  human_duel_played   — Odam bilan 1v1 Duelni yakunlash (g'alaba/mag'lubiyat farqsiz)
  mass_duel_played    — Ommaviy Duelga qo'shilish
  tournament_played   — Turnirga qo'shilish
  product_purchased   — Do'kondan mahsulot sotib olish
  gift_sent           — Do'stga B Coin sovg'a qilish

Har kuni foydalanuvchiga shu 50 tadan **3 tasi** ko'rsatiladi (kun bo'yicha
o'zgaruvchi, lekin barqaror tanlov). Admin panel orqali faqat `reward_coin`
va `is_active` o'zgartiriladi (spec talabi: "faqat B Coin mukofotini
belgilash").
"""


def _mission(key: str, title: str, description: str, event: str, count: int, reward: float) -> dict:
    return {
        "key": key,
        "title": title,
        "description": description,
        "requirement_count": count,
        "reward_coin": round(reward, 2),
        "trigger_event": event,
    }


DAILY_MISSIONS: list[dict] = []

# --- ❓ To'g'ri javob berish (15 ta, 5 dan 75 gacha) ---
for count in [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75]:
    DAILY_MISSIONS.append(
        _mission(
            key=f"daily_correct_{count}",
            title=f"❓ {count} ta savolga to'g'ri javob berish",
            description=f"Bugun istalgan rejimda jami {count} ta savolga to'g'ri javob bering",
            event="correct_answer",
            count=count,
            reward=count * 0.08,
        )
    )

# --- 👥 Do'st taklif qilish (8 ta, 1 dan 8 gacha) ---
for count in range(1, 9):
    DAILY_MISSIONS.append(
        _mission(
            key=f"daily_invite_{count}",
            title=f"👥 {count} ta do'st taklif qilish",
            description=f"Referal havolangiz orqali {count} ta yangi do'stni botga taklif qiling",
            event="invite_friend",
            count=count,
            reward=count * 0.5,
        )
    )

# --- ⚔️ Duelda g'olib bo'lish (8 ta) ---
for count in range(1, 9):
    DAILY_MISSIONS.append(
        _mission(
            key=f"daily_duel_win_{count}",
            title=f"⚔️ {count} ta duelda g'olib bo'lish",
            description=f"Odam bilan 1v1 Duelda bugun {count} marta g'olib chiqing",
            event="duel_win",
            count=count,
            reward=count * 0.6,
        )
    )

# --- 👤 Odam bilan duel o'ynash (6 ta) ---
for count in range(1, 7):
    DAILY_MISSIONS.append(
        _mission(
            key=f"daily_human_duel_{count}",
            title=f"👤 {count} marta Odam bilan Duel o'ynash",
            description=f"Bugun {count} marta Odam bilan 1v1 Duelni yakunlang",
            event="human_duel_played",
            count=count,
            reward=count * 0.4,
        )
    )

# --- 🌍 Ommaviy Duelga qo'shilish (5 ta) ---
for count in range(1, 6):
    DAILY_MISSIONS.append(
        _mission(
            key=f"daily_mass_duel_{count}",
            title=f"🌍 {count} ta Ommaviy Duelga qo'shilish",
            description=f"Bugun {count} ta Ommaviy Duelga a'zo bo'ling",
            event="mass_duel_played",
            count=count,
            reward=count * 0.4,
        )
    )

# --- 🏅 Turnirga qo'shilish (3 ta) ---
for count in range(1, 4):
    DAILY_MISSIONS.append(
        _mission(
            key=f"daily_tournament_{count}",
            title=f"🏅 {count} ta Turnirga qo'shilish",
            description=f"Bugun {count} ta Turnirga a'zo bo'ling",
            event="tournament_played",
            count=count,
            reward=count * 0.5,
        )
    )

# --- 🛒 Mahsulot sotib olish (3 ta) ---
for count in range(1, 4):
    DAILY_MISSIONS.append(
        _mission(
            key=f"daily_purchase_{count}",
            title=f"🛒 {count} ta mahsulot sotib olish",
            description=f"Bugun Do'kondan {count} ta mahsulot xarid qiling",
            event="product_purchased",
            count=count,
            reward=count * 0.5,
        )
    )

# --- 🎁 Sovg'a yuborish (2 ta) ---
for count in range(1, 3):
    DAILY_MISSIONS.append(
        _mission(
            key=f"daily_gift_{count}",
            title=f"🎁 {count} marta do'stga sovg'a yuborish",
            description=f"Bugun do'stlaringizga {count} marta B Coin sovg'a qiling",
            event="gift_sent",
            count=count,
            reward=count * 0.5,
        )
    )

assert len(DAILY_MISSIONS) == 50
