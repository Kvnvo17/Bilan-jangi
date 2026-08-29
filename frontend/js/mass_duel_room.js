// Bilim Jangi — Ommaviy Duel xonasi

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
        showToast("Duel kodi topilmadi");
        return;
    }
    const res = await fetch("/api/mass-duel/join", {
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
    const res = await fetch(`/api/mass-duel/${code}`);
    if (!res.ok) return;
    const data = await res.json();
    const d = data.duel;
    document.getElementById("duelTitle").textContent = d.name;
    const badge = d.is_admin_duel ? " 👑 (Admin Duel)" : "";
    document.getElementById("infoBox").textContent =
        `Kod: ${d.code}${badge} · 👥 ${d.participant_count}/${d.max_participants} · Holat: ${d.status === "open" ? "🟢 Ochiq" : "🔴 Yopiq"} · Jamg'arma: ${d.fund.toFixed(2)} 🪙`;

    const isOwnerOrAdmin = d.owner && (d.owner.telegram_id === currentUser.id);
    document.getElementById("closeBtn").classList.toggle("hidden", !isOwnerOrAdmin || d.status !== "open");

    renderLeaderboard(data.leaderboard);
}

function renderLeaderboard(leaderboard) {
    const container = document.getElementById("boardTab");
    if (!leaderboard.length) {
        container.innerHTML = `<div class="mission-desc">Hali ballar yo'q.</div>`;
        return;
    }
    container.innerHTML = leaderboard
        .map((entry, i) => {
            const name = entry.user.first_name || entry.user.username || "Foydalanuvchi";
            return `
                <div class="friend-card">
                    <div class="rank-badge">#${i + 1}</div>
                    <div class="friend-info">
                        <div class="friend-name">${name}</div>
                        <div class="friend-sub">${entry.score} to'g'ri javob</div>
                    </div>
                </div>
            `;
        })
        .join("");
}

function switchTab(tab) {
    document.querySelectorAll(".tab-btn").forEach((b) => b.classList.toggle("active", b.dataset.tab === tab));
    document.getElementById("playTab").classList.toggle("hidden", tab !== "play");
    document.getElementById("addTab").classList.toggle("hidden", tab !== "add");
    document.getElementById("boardTab").classList.toggle("hidden", tab !== "board");
    if (tab === "board") refreshInfo();
    if (tab === "play") loadNextQuestion();
}

async function loadNextQuestion() {
    answered = false;
    document.getElementById("resultBanner").className = "result-banner hidden";
    document.getElementById("nextBtn").className = "next-btn hidden";

    const card = document.getElementById("questionCard");
    card.innerHTML = `<div class="question-loading">Savol yuklanmoqda...</div>`;

    const res = await fetch(`/api/mass-duel/${code}/next-question?telegram_id=${currentUser.id}`);
    if (!res.ok) {
        card.innerHTML = `<div class="question-loading">Duel topilmadi.</div>`;
        return;
    }
    const q = await res.json();
    if (!q) {
        card.innerHTML = `<div class="question-loading">Hozircha yangi savol yo'q. "➕ Savol qo'shish" orqali o'zingiz qo'shing yoki keyinroq qayting.</div>`;
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
    ];
    if (q.option_d) options.push(["D", q.option_d]);
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

    const res = await fetch("/api/mass-duel/answer", {
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
        banner.textContent = `❌ Noto'g'ri. -${Math.abs(Number(result.coin_change)).toFixed(2)} B Coin`;
    }
    document.getElementById("bCoin").textContent = Number(result.new_b_coin).toFixed(2);
    document.getElementById("nextBtn").className = "next-btn";
}

async function addQuestion() {
    const text = document.getElementById("qText").value.trim();
    const a = document.getElementById("qA").value.trim();
    const b = document.getElementById("qB").value.trim();
    const c = document.getElementById("qC").value.trim();
    const d = document.getElementById("qD").value.trim();
    const correct = document.getElementById("qCorrect").value;

    if (!text || !a || !b || !c) {
        showToast("Savol matni va kamida 3 ta variant kerak");
        return;
    }

    const res = await fetch("/api/mass-duel/question/add", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            telegram_id: currentUser.id,
            code,
            text,
            option_a: a,
            option_b: b,
            option_c: c,
            option_d: d || null,
            correct_option: correct,
        }),
    });
    const data = await res.json();
    if (!res.ok) {
        showToast(data.detail || "Xatolik");
        return;
    }
    showToast("Savol qo'shildi ✅");
    ["qText", "qA", "qB", "qC", "qD"].forEach((id) => (document.getElementById(id).value = ""));
}

async function closeDuel() {
    if (!confirm("Duelni yopmoqchimisiz? Bu amalni bekor qilib bo'lmaydi.")) return;
    const res = await fetch("/api/mass-duel/close", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ telegram_id: currentUser.id, code }),
    });
    const data = await res.json();
    showToast(res.ok ? "Duel yopildi" : data.detail || "Xatolik");
    refreshInfo();
}

(async function init() {
    await ensureProfile();
    await joinAndLoadInfo();
    await loadNextQuestion();
})();
