// Bilim Jangi — Oylik missiyalar

const tg = window.Telegram ? window.Telegram.WebApp : null;
if (tg) { tg.ready(); tg.expand(); }

function getTelegramUser() {
    if (tg && tg.initDataUnsafe && tg.initDataUnsafe.user) return tg.initDataUnsafe.user;
    return { id: 999999999, username: "test_user", first_name: "Mehmon" };
}

const currentUser = getTelegramUser();

function showToast(text) {
    const toast = document.getElementById("toast");
    toast.textContent = text;
    toast.classList.add("show");
    setTimeout(() => toast.classList.remove("show"), 2200);
}

async function loadMissions() {
    const res = await fetch(`/api/missions/monthly/${currentUser.id}`);
    const missions = await res.json();
    renderMissions(missions);
}

function renderMissions(missions) {
    const container = document.getElementById("missionsList");
    if (!missions.length) {
        container.innerHTML = `<div class="mission-desc">Hozircha oylik missiyalar mavjud emas.</div>`;
        return;
    }
    container.innerHTML = missions
        .map((m) => {
            const pct = Math.min(100, Math.round((m.progress / m.requirement_count) * 100));
            let btnHtml;
            if (m.claimed) btnHtml = `<button class="mission-claim-btn" disabled>✅ Olingan</button>`;
            else if (m.completed) btnHtml = `<button class="mission-claim-btn" onclick="claimMission('${m.key}')">🎁 Mukofotni olish</button>`;
            else btnHtml = "";
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
    const res = await fetch("/api/missions/monthly/claim", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ telegram_id: currentUser.id, key }),
    });
    const data = await res.json();
    if (!res.ok) {
        showToast(data.detail || "Xatolik");
        return;
    }
    showToast(`+${Number(data.reward_coin).toFixed(2)} B Coin olindi! 🎉`);
    loadMissions();
}

loadMissions();
