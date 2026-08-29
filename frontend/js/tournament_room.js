// Bilim Jangi — Turnir xonasi

const tg = window.Telegram ? window.Telegram.WebApp : null;
if (tg) { tg.ready(); tg.expand(); }

function getTelegramUser() {
    if (tg && tg.initDataUnsafe && tg.initDataUnsafe.user) return tg.initDataUnsafe.user;
    return { id: 999999999, username: "test_user", first_name: "Mehmon" };
}

const currentUser = getTelegramUser();
const code = new URLSearchParams(location.search).get("code");
let currentQuestion = null;
let answered = false;

function showToast(text) {
    const toast = document.getElementById("toast");
    toast.textContent = text;
    toast.classList.add("show");
    setTimeout(() => toast.classList.remove("show"), 2200);
}

async function ensureProfile() {
    const res = await fetch("/api/profile/sync", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            telegram_id: currentUser.id,
            username: currentUser.username || null,
            first_name: currentUser.first_name || "Foydalanuvchi",
        }),
    });
    const profile = await res.json();
    document.getElementById("bCoin").textContent = Number(profile.b_coin).toFixed(2);
}

async function joinAndLoadInfo() {
    if (!code) {
        showToast("Turnir kodi topilmadi");
        return;
    }
    const res = await fetch("/api/tournament/join", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ telegram_id: currentUser.id, code }),
    });
    if (!res.ok) {
        const err = await res.json();
        showToast(err.detail || "Qo'shilib bo'lmadi");
    }
    await refreshInfo();
}

async function refreshInfo() {
    const res = await fetch(`/api/tournament/${code}?telegram_id=${currentUser.id}`);
    if (!res.ok) return;
    const data = await res.json();
    const t = data.tournament;
    document.getElementById("tTitle").textContent = t.name;
    const badge = t.is_admin_tournament ? " 👑 (Admin Turnir)" : "";
    document.getElementById("infoBox").textContent =
        `Kod: ${t.code}${badge} · 👥 ${t.participant_count}/${t.max_participants} · Holat: ${t.status === "open" ? "🟢 Ochiq" : "🔴 Yopiq"} · Yutuq: ${t.prize_text || "belgilanmagan"}`;

    const isOwnerOrAdmin = t.owner && t.owner.telegram_id === currentUser.id;
    document.getElementById("closeBtn").classList.toggle("hidden", !isOwnerOrAdmin || t.status !== "open");

    renderLeaderboard(data.leaderboard);
    return data;
}

function renderLeaderboard(leaderboard) {
    const container = document.getElementById("boardTab");
    if (!leaderboard.length) {
        container.innerHTML = `<div class="mission-desc">Hali ballar yo'q.</div>`;
        return;
    }
    container.innerHTML = leaderboard
        .map((e) => {
            const name = e.user.first_name || e.user.username || "Foydalanuvchi";
            return `
                <div class="friend-card">
                    <div class="rank-badge">#${e.rank}</div>
                    <div class="friend-info">
                        <div class="friend-name">${name}</div>
                        <div class="friend-sub">${e.score} to'g'ri javob</div>
                    </div>
                </div>
            `;
        })
        .join("");
}

function switchTab(tab) {
    document.querySelectorAll(".tab-btn").forEach((b) => b.classList.toggle("active", b.dataset.tab === tab));
    document.getElementById("playTab").classList.toggle("hidden", tab !== "play");
    document.getElementById("boardTab").classList.toggle("hidden", tab !== "board");
    if (tab === "board") refreshInfo();
}

async function loadCurrentQuestion() {
    answered = false;
    document.getElementById("resultBanner").className = "result-banner hidden";
    document.getElementById("nextBtn").className = "next-btn hidden";

    const card = document.getElementById("questionCard");
    card.innerHTML = `<div class="question-loading">Savol yuklanmoqda...</div>`;

    const res = await fetch(`/api/tournament/${code}/question?telegram_id=${currentUser.id}`);
    if (!res.ok) {
        card.innerHTML = `<div class="question-loading">Turnir topilmadi.</div>`;
        return;
    }
    const q = await res.json();
    if (!q) {
        card.innerHTML = `<div class="question-loading">🎉 Siz barcha savollarga javob berdingiz! "🏆 Reyting" bo'limidan natijangizni ko'ring.</div>`;
        return;
    }
    currentQuestion = q;
    renderQuestion(q);
}

function renderQuestion(q) {
    const card = document.getElementById("questionCard");
    const options = [
        ["A", q.option_a],
        ["B", q.option_b],
        ["C", q.option_c],
        ["D", q.option_d],
    ];
    card.innerHTML = `
        <div class="question-text">${q.text}</div>
        <div>
            ${options.map(([key, text]) => `<button class="option-btn" data-key="${key}" onclick="selectAnswer('${key}')">${key}) ${text}</button>`).join("")}
        </div>
    `;
}

async function selectAnswer(key) {
    if (answered) return;
    answered = true;
    document.querySelectorAll(".option-btn").forEach((b) => (b.disabled = true));

    const res = await fetch("/api/tournament/answer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ telegram_id: currentUser.id, code, question_id: currentQuestion.id, selected_option: key }),
    });
    const result = await res.json();
    if (!res.ok) {
        showToast(result.detail || "Xatolik");
        return;
    }

    document.querySelectorAll(".option-btn").forEach((btn) => {
        const k = btn.getAttribute("data-key");
        if (k === result.correct_option) btn.classList.add("correct");
        else if (k === key) btn.classList.add("wrong");
    });

    const banner = document.getElementById("resultBanner");
    banner.classList.remove("hidden");
    if (result.is_correct) {
        banner.className = "result-banner correct";
        banner.textContent = `✅ To'g'ri! +${Number(result.coin_change).toFixed(2)} B Coin`;
    } else {
        banner.className = "result-banner wrong";
        banner.textContent = `❌ Noto'g'ri. ${Number(result.coin_change).toFixed(2)} B Coin`;
    }
    await ensureProfile();
    document.getElementById("nextBtn").className = "next-btn";
    if (result.finished_all_questions) {
        document.getElementById("nextBtn").textContent = "Yakunlandi — Reytingni ko'rish 🏆";
        document.getElementById("nextBtn").onclick = () => switchTab("board");
    }
}

async function closeTournament() {
    if (!confirm("Turnirni yopmoqchimisiz? Bu amalni bekor qilib bo'lmaydi.")) return;
    const res = await fetch("/api/tournament/close", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ telegram_id: currentUser.id, code }),
    });
    const data = await res.json();
    showToast(res.ok ? "Turnir yopildi" : data.detail || "Xatolik");
    refreshInfo();
}

(async function init() {
    await ensureProfile();
    await joinAndLoadInfo();
    await loadCurrentQuestion();
})();
