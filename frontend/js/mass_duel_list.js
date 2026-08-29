// Bilim Jangi — Ommaviy Duel ro'yxati

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

async function checkAdmin() {
    const res = await fetch(`/api/profile/${currentUser.id}`);
    const profile = await res.json();
    if (profile.is_admin) {
        document.getElementById("adminCreateBtn").style.display = "block";
    }
}

async function createMassDuel(isAdminDuel = false) {
    const name = document.getElementById("duelNameInput").value.trim() || "Ommaviy Duel";
    const res = await fetch("/api/mass-duel/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ telegram_id: currentUser.id, name, is_admin_duel: isAdminDuel }),
    });
    const data = await res.json();
    if (!res.ok) {
        showToast(data.detail || "Xatolik");
        return;
    }
    location.href = `/mass-duel/room?code=${data.code}`;
}

async function joinByCode() {
    const code = document.getElementById("joinCodeInput").value.trim().toUpperCase();
    if (!code) return;
    location.href = `/mass-duel/room?code=${code}`;
}

async function loadDuels() {
    const container = document.getElementById("duelsList");
    container.innerHTML = `<div class="mission-skeleton"></div>`;
    const res = await fetch("/api/mass-duel/list");
    const data = await res.json();
    if (!data.duels.length) {
        container.innerHTML = `<div class="mission-desc">Hozircha faol duellar yo'q. Birinchi bo'lib yarating!</div>`;
        return;
    }
    container.innerHTML = data.duels
        .map((d) => {
            const badge = d.is_admin_duel ? `<span class="mini-badge admin-badge">👑 Admin</span>` : "";
            return `
                <div class="friend-card" onclick="location.href='/mass-duel/room?code=${d.code}'">
                    <div class="friend-info">
                        <div class="friend-name">${d.name} ${badge}</div>
                        <div class="friend-sub">👥 ${d.participant_count}/${d.max_participants} · Kod: ${d.code}</div>
                    </div>
                </div>
            `;
        })
        .join("");
}

checkAdmin();
loadDuels();
