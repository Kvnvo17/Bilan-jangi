// Bilim Jangi — asosiy sahifa logikasi

const tg = window.Telegram ? window.Telegram.WebApp : null;
if (tg) {
    tg.ready();
    tg.expand();
}

function getTelegramUser() {
    if (tg && tg.initDataUnsafe && tg.initDataUnsafe.user) {
        return tg.initDataUnsafe.user;
    }
    // Telegramdan tashqarida (brauzerda) sinash uchun zaxira foydalanuvchi
    return { id: 999999999, username: "test_user", first_name: "Mehmon" };
}

function showToast(text) {
    const toast = document.getElementById("toast");
    toast.textContent = text;
    toast.classList.add("show");
    setTimeout(() => toast.classList.remove("show"), 2200);
}

function showComingSoon(featureName) {
    showToast(`${featureName} — tez orada qo'shiladi 🚧`);
}

let currentTelegramId = null;

async function syncProfile() {
    const user = getTelegramUser();
    currentTelegramId = user.id;

    const avatarUrl = user.photo_url || null;

    const res = await fetch("/api/profile/sync", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            telegram_id: user.id,
            username: user.username || null,
            first_name: user.first_name || "Foydalanuvchi",
            avatar_url: avatarUrl,
        }),
    });
    const profile = await res.json();
    renderProfile(profile);
    return profile;
}

function renderProfile(profile) {
    document.getElementById("firstName").textContent = profile.first_name || profile.username || "Foydalanuvchi";
    document.getElementById("level").textContent = profile.level;
    document.getElementById("bCoin").textContent = Number(profile.b_coin).toFixed(2);
    if (profile.avatar_url) {
        document.getElementById("avatar").src = profile.avatar_url;
    } else {
        const name = encodeURIComponent(profile.first_name || "B");
        document.getElementById("avatar").src = `https://ui-avatars.com/api/?background=2563EB&color=fff&name=${name}`;
    }
}

async function loadDailyMissions() {
    if (!currentTelegramId) return;
    const res = await fetch(`/api/missions/daily/${currentTelegramId}`);
    const missions = await res.json();
    renderMissions(missions);
}

function renderMissions(missions) {
    const container = document.getElementById("missionsList");
    if (!missions.length) {
        container.innerHTML = `<div class="mission-desc">Hozircha kunlik missiyalar mavjud emas.</div>`;
        return;
    }
    container.innerHTML = missions
        .map((m) => {
            const pct = Math.min(100, Math.round((m.progress / m.requirement_count) * 100));
            let btnHtml;
            if (m.claimed) {
                btnHtml = `<button class="mission-claim-btn" disabled>✅ Olingan</button>`;
            } else if (m.completed) {
                btnHtml = `<button class="mission-claim-btn" onclick="claimMission('${m.key}')">🎁 Mukofotni olish</button>`;
            } else {
                btnHtml = "";
            }
            return `
                <div class="mission-card">
                    <div class="mission-top">
                        <div class="mission-title">${m.title}</div>
                        <div class="mission-reward">+${Number(m.reward_coin).toFixed(2)} 🪙</div>
                    </div>
                    <div class="mission-desc">${m.description}</div>
                    <div class="mission-progress-bar"><div class="mission-progress-fill" style="width:${pct}%"></div></div>
                    <div class="mission-desc">${m.progress}/${m.requirement_count} bajarildi</div>
                    ${btnHtml}
                </div>
            `;
        })
        .join("");
}

async function claimMission(key) {
    try {
        const res = await fetch("/api/missions/claim", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ telegram_id: currentTelegramId, key }),
        });
        if (!res.ok) {
            const err = await res.json();
            showToast(err.detail || "Xatolik yuz berdi");
            return;
        }
        const data = await res.json();
        showToast(`+${Number(data.reward_coin).toFixed(2)} B Coin olindi! 🎉`);
        document.getElementById("bCoin").textContent = Number(data.new_b_coin).toFixed(2);
        await loadDailyMissions();
    } catch (e) {
        showToast("Tarmoq xatosi");
    }
}

(async function init() {
    try {
        await syncProfile();
        await loadDailyMissions();
    } catch (e) {
        showToast("Ma'lumotlarni yuklashda xatolik");
        console.error(e);
    }
})();
