// Bilim Jangi — Do'stlar sahifasi

const tg = window.Telegram ? window.Telegram.WebApp : null;
if (tg) { tg.ready(); tg.expand(); }

function getTelegramUser() {
    if (tg && tg.initDataUnsafe && tg.initDataUnsafe.user) return tg.initDataUnsafe.user;
    return { id: 999999999, username: "test_user", first_name: "Mehmon" };
}

const currentUser = getTelegramUser();
let activeTab = "friends";

function showToast(text) {
    const toast = document.getElementById("toast");
    toast.textContent = text;
    toast.classList.add("show");
    setTimeout(() => toast.classList.remove("show"), 2200);
}

function switchTab(tab) {
    activeTab = tab;
    document.querySelectorAll(".tab-btn").forEach((b) => b.classList.toggle("active", b.dataset.tab === tab));
    document.getElementById("searchBox").classList.toggle("hidden", tab !== "search");
    if (tab === "search") {
        document.getElementById("listContainer").innerHTML = "";
        return;
    }
    loadTab(tab);
}

function userCardHtml(user, actionsHtml) {
    const name = user.first_name || user.username || "Foydalanuvchi";
    const avatar = user.avatar_url || `https://ui-avatars.com/api/?background=2563EB&color=fff&name=${encodeURIComponent(name)}`;
    return `
        <div class="friend-card">
            <img class="friend-avatar" src="${avatar}">
            <div class="friend-info">
                <div class="friend-name">${name}</div>
                <div class="friend-sub">@${user.username || "—"} · Level ${user.level} · 🪙 ${Number(user.b_coin).toFixed(2)}</div>
            </div>
            <div class="friend-actions">${actionsHtml}</div>
        </div>
    `;
}

async function loadTab(tab) {
    const container = document.getElementById("listContainer");
    container.innerHTML = `<div class="mission-skeleton"></div>`;

    if (tab === "friends") {
        const res = await fetch(`/api/friends/list/${currentUser.id}`);
        const users = await res.json();
        if (!users.length) {
            container.innerHTML = `<div class="mission-desc">Hali do'stlaringiz yo'q. "🔍 Qidirish" orqali toping.</div>`;
            return;
        }
        container.innerHTML = users
            .map((u) =>
                userCardHtml(
                    u,
                    `<button class="mini-btn" onclick="inviteDuel(${u.telegram_id})">⚔️ Duel</button>
                     <button class="mini-btn" onclick="giftPrompt(${u.telegram_id})">🎁 Sovg'a</button>`
                )
            )
            .join("");
    } else if (tab === "incoming") {
        const res = await fetch(`/api/friends/incoming/${currentUser.id}`);
        const requests = await res.json();
        if (!requests.length) {
            container.innerHTML = `<div class="mission-desc">Kelgan so'rovlar yo'q.</div>`;
            return;
        }
        container.innerHTML = requests
            .map((r) =>
                userCardHtml(
                    r.user,
                    `<button class="mini-btn primary" onclick="respond(${r.request_id}, 'accept')">✅</button>
                     <button class="mini-btn danger" onclick="respond(${r.request_id}, 'reject')">❌</button>`
                )
            )
            .join("");
    } else if (tab === "outgoing") {
        const res = await fetch(`/api/friends/outgoing/${currentUser.id}`);
        const requests = await res.json();
        if (!requests.length) {
            container.innerHTML = `<div class="mission-desc">Yuborilgan so'rovlar yo'q.</div>`;
            return;
        }
        container.innerHTML = requests.map((r) => userCardHtml(r.user, `<span class="mini-badge">⏳ Kutilmoqda</span>`)).join("");
    }
}

async function doSearch() {
    const q = document.getElementById("searchInput").value.trim();
    if (!q) return;
    const container = document.getElementById("listContainer");
    container.innerHTML = `<div class="mission-skeleton"></div>`;
    const res = await fetch(`/api/friends/search?telegram_id=${currentUser.id}&q=${encodeURIComponent(q)}`);
    const data = await res.json();
    if (!data.users.length) {
        container.innerHTML = `<div class="mission-desc">Hech kim topilmadi.</div>`;
        return;
    }
    container.innerHTML = data.users
        .map((u) => userCardHtml(u, `<button class="mini-btn primary" onclick="sendRequest('${u.username || u.telegram_id}')">➕ Qo'shish</button>`))
        .join("");
}

async function sendRequest(target) {
    const res = await fetch("/api/friends/request", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ telegram_id: currentUser.id, target: String(target) }),
    });
    const data = await res.json();
    showToast(res.ok ? "So'rov yuborildi ✅" : data.detail || "Xatolik");
}

async function respond(requestId, action) {
    const res = await fetch("/api/friends/respond", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ telegram_id: currentUser.id, request_id: requestId, action }),
    });
    const data = await res.json();
    showToast(res.ok ? "Bajarildi" : data.detail || "Xatolik");
    loadTab("incoming");
}

async function inviteDuel(friendTelegramId) {
    const res = await fetch("/api/duel/human/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ telegram_id: currentUser.id, target: String(friendTelegramId) }),
    });
    const data = await res.json();
    if (!res.ok) {
        showToast(data.detail || "Xatolik");
        return;
    }
    location.href = `/human-duel?code=${data.invite_code}`;
}

async function giftPrompt(friendTelegramId) {
    const amount = prompt("Necha B Coin sovg'a qilmoqchisiz?");
    if (!amount || isNaN(amount) || Number(amount) <= 0) return;
    const res = await fetch("/api/friends/gift", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ telegram_id: currentUser.id, friend_telegram_id: friendTelegramId, amount: Number(amount) }),
    });
    const data = await res.json();
    showToast(res.ok ? "Sovg'a yuborildi 🎁" : data.detail || "Xatolik");
}

loadTab("friends");
