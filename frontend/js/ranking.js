// Bilim Jangi — Reyting sahifasi

function showToast(text) {
    const toast = document.getElementById("toast");
    toast.textContent = text;
    toast.classList.add("show");
    setTimeout(() => toast.classList.remove("show"), 2200);
}

const MEDALS = ["🥇", "🥈", "🥉"];

async function loadRanking(type) {
    document.querySelectorAll(".tab-btn").forEach((b) => b.classList.toggle("active", b.dataset.type === type));
    const container = document.getElementById("rankingList");
    container.innerHTML = `<div class="mission-skeleton"></div><div class="mission-skeleton"></div>`;

    const res = await fetch(`/api/ranking/${type}`);
    const entries = await res.json();

    if (!entries.length) {
        container.innerHTML = `<div class="mission-desc">Hozircha reyting bo'sh.</div>`;
        return;
    }

    const labels = { umumiy: "to'g'ri javob", "1v1": "g'alaba", turnir: "turnir g'alabasi" };

    container.innerHTML = entries
        .map((e) => {
            const badge = MEDALS[e.rank - 1] || `#${e.rank}`;
            const name = e.user.first_name || e.user.username || "Foydalanuvchi";
            const avatar =
                e.user.avatar_url ||
                `https://ui-avatars.com/api/?background=2563EB&color=fff&name=${encodeURIComponent(name)}`;
            return `
                <div class="friend-card">
                    <div class="rank-badge">${badge}</div>
                    <img class="friend-avatar" src="${avatar}">
                    <div class="friend-info">
                        <div class="friend-name">${name}</div>
                        <div class="friend-sub">Level ${e.user.level} · ${e.score} ${labels[type]}</div>
                    </div>
                </div>
            `;
        })
        .join("");
}

loadRanking("umumiy");
