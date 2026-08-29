"""
Bilim Jangi — 4-bosqich: to'liq 50 ta oylik missiya ro'yxati.
Naqsh kunlik bilan bir xil (database/missions_seed.py'ga qarang), faqat
talab qilingan son va davr (bir oy) kattaroq. Har oy 50 tadan **5 tasi**
foydalanuvchiga ko'rsatiladi (oy bo'yicha o'zgaruvchi, barqaror tanlov).
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


MONTHLY_MISSIONS: list[dict] = []

# --- ❓ To'g'ri javob berish (15 ta, 20 dan 300 gacha) ---
for count in [20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240, 260, 280, 300]:
    MONTHLY_MISSIONS.append(
        _mission(
            key=f"monthly_correct_{count}",
            title=f"❓ {count} ta savolga to'g'ri javob berish",
            description=f"Shu oy davomida jami {count} ta savolga to'g'ri javob bering",
            event="correct_answer",
            count=count,
            reward=count * 0.06,
        )
    )

# --- 👥 Do'st taklif qilish (8 ta, 2 dan 16 gacha) ---
for count in [2, 4, 6, 8, 10, 12, 14, 16]:
    MONTHLY_MISSIONS.append(
        _mission(
            key=f"monthly_invite_{count}",
            title=f"👥 {count} ta do'st taklif qilish",
            description=f"Shu oy davomida {count} ta yangi do'stni botga taklif qiling",
            event="invite_friend",
            count=count,
            reward=count * 0.7,
        )
    )

# --- ⚔️ Duelda g'olib bo'lish (8 ta, 2 dan 16 gacha) ---
for count in [2, 4, 6, 8, 10, 12, 14, 16]:
    MONTHLY_MISSIONS.append(
        _mission(
            key=f"monthly_duel_win_{count}",
            title=f"⚔️ {count} ta duelda g'olib bo'lish",
            description=f"Shu oy Odam bilan 1v1 Duelda {count} marta g'olib chiqing",
            event="duel_win",
            count=count,
            reward=count * 0.9,
        )
    )

# --- 👤 Odam bilan duel o'ynash (6 ta, 2 dan 12 gacha) ---
for count in [2, 4, 6, 8, 10, 12]:
    MONTHLY_MISSIONS.append(
        _mission(
            key=f"monthly_human_duel_{count}",
            title=f"👤 {count} marta Odam bilan Duel o'ynash",
            description=f"Shu oy {count} marta Odam bilan 1v1 Duelni yakunlang",
            event="human_duel_played",
            count=count,
            reward=count * 0.5,
        )
    )

# --- 🌍 Ommaviy Duelga qo'shilish (5 ta, 2 dan 10 gacha) ---
for count in [2, 4, 6, 8, 10]:
    MONTHLY_MISSIONS.append(
        _mission(
            key=f"monthly_mass_duel_{count}",
            title=f"🌍 {count} ta Ommaviy Duelga qo'shilish",
            description=f"Shu oy {count} ta Ommaviy Duelga a'zo bo'ling",
            event="mass_duel_played",
            count=count,
            reward=count * 0.5,
        )
    )

# --- 🏅 Turnirga qo'shilish (3 ta) ---
for count in [1, 2, 3]:
    MONTHLY_MISSIONS.append(
        _mission(
            key=f"monthly_tournament_{count}",
            title=f"🏅 {count} ta Turnirga qo'shilish",
            description=f"Shu oy {count} ta Turnirga a'zo bo'ling",
            event="tournament_played",
            count=count,
            reward=count * 0.8,
        )
    )

# --- 🛒 Mahsulot sotib olish (3 ta) ---
for count in [1, 2, 3]:
    MONTHLY_MISSIONS.append(
        _mission(
            key=f"monthly_purchase_{count}",
            title=f"🛒 {count} ta mahsulot sotib olish",
            description=f"Shu oy Do'kondan {count} ta mahsulot xarid qiling",
            event="product_purchased",
            count=count,
            reward=count * 0.8,
        )
    )

# --- 🎁 Sovg'a yuborish (2 ta) ---
for count in [1, 2]:
    MONTHLY_MISSIONS.append(
        _mission(
            key=f"monthly_gift_{count}",
            title=f"🎁 {count} marta do'stga sovg'a yuborish",
            description=f"Shu oy do'stlaringizga {count} marta B Coin sovg'a qiling",
            event="gift_sent",
            count=count,
            reward=count * 0.8,
        )
    )

assert len(MONTHLY_MISSIONS) == 50
