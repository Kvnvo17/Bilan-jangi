// Bilim Jangi — Turnir ro'yxati

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
    if (profile.is_admin) document.getElementById("adminCreateBtn").style.display = "block";
}

async function createTournament(isAdmin = false) {
    const name = document.getElementById("tName").value.trim() || "Turnir";
    const prize = document.getElementById("tPrize").value.trim();
    const res = await fetch("/api/tournament/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ telegram_id: currentUser.id, name, is_admin_tournament: isAdmin, prize_text: prize }),
    });
    const data = await res.json();
    if (!res.ok) {
        showToast(data.detail || "Xatolik");
        return;
    }
    location.href = `/tournament/room?code=${data.code}`;
}

async function joinByCode() {
    const code = document.getElementById("joinCodeInput").value.trim().toUpperCase();
    if (!code) return;
    location.href = `/tournament/room?code=${code}`;
}

async function loadTournaments() {
    const container = document.getElementById("tournamentsList");
    container.innerHTML = `<div class="mission-skeleton"></div>`;
    const res = await fetch("/api/tournament/list");
    const data = await res.json();
    if (!data.tournaments.length) {
        container.innerHTML = `<div class="mission-desc">Hozircha faol turnirlar yo'q. Birinchi bo'lib yarating!</div>`;
        return;
    }
    container.innerHTML = data.tournaments
        .map((t) => {
            const badge = t.is_admin_tournament ? `<span class="mini-badge admin-badge">👑 Admin</span>` : "";
            return `
                <div class="friend-card" onclick="location.href='/tournament/room?code=${t.code}'">
                    <div class="friend-info">
                        <div class="friend-name">${t.name} ${badge}</div>
                        <div class="friend-sub">👥 ${t.participant_count}/${t.max_participants} · Kod: ${t.code} · 🏆 ${t.prize_text || "belgilanmagan"}</div>
                    </div>
                </div>
            `;
        })
        .join("");
}

checkAdmin();
loadTournaments();
