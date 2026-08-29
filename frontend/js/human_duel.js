// Bilim Jangi — Odam bilan 1v1 Duel logikasi

const tg = window.Telegram ? window.Telegram.WebApp : null;
if (tg) { tg.ready(); tg.expand(); }

function getTelegramUser() {
    if (tg && tg.initDataUnsafe && tg.initDataUnsafe.user) return tg.initDataUnsafe.user;
    return { id: 999999999, username: "test_user", first_name: "Mehmon" };
}

const currentUser = getTelegramUser();
let inviteCode = new URLSearchParams(location.search).get("code");
let pollTimer = null;
let lastRenderedIndex = -1;
let answered = false;

function showToast(text) {
    const toast = document.getElementById("toast");
    toast.textContent = text;
    toast.classList.add("show");
    setTimeout(() => toast.classList.remove("show"), 2200);
}

async function ensureProfile() {
    await fetch("/api/profile/sync", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            telegram_id: currentUser.id,
            username: currentUser.username || null,
            first_name: currentUser.first_name || "Foydalanuvchi",
        }),
    });
}

async function createDuel() {
    await ensureProfile();
    const target = document.getElementById("targetInput").value.trim();
    const res = await fetch("/api/duel/human/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ telegram_id: currentUser.id, target: target || null }),
    });
    const data = await res.json();
    if (!res.ok) {
        showToast(data.detail || "Xatolik");
        return;
    }
    inviteCode = data.invite_code;
    history.replaceState(null, "", `/human-duel?code=${inviteCode}`);
    startGame();
}

async function joinDuel() {
    await ensureProfile();
    const res = await fetch("/api/duel/human/join", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ telegram_id: currentUser.id, invite_code: inviteCode }),
    });
    const data = await res.json();
    if (!res.ok) {
        showToast(data.detail || "Xatolik");
        return;
    }
    startGame();
}

function copyLink() {
    const link = `${location.origin}/human-duel?code=${inviteCode}`;
    navigator.clipboard?.writeText(link);
    showToast("Havola nusxalandi 📋");
}

function startGame() {
    document.getElementById("setupBox").classList.add("hidden");
    document.getElementById("scoreBoard").classList.remove("hidden");
    pollTimer = setInterval(pollState, 2500);
    pollState();
}

async function pollState() {
    const res = await fetch(`/api/duel/human/state/${inviteCode}?telegram_id=${currentUser.id}`);
    if (!res.ok) return;
    const state = await res.json();
    render(state);
}

function render(state) {
    const scoreBoard = document.getElementById("scoreBoard");
    const p1Name = state.player1.first_name || state.player1.username;
    const p2Name = state.player2 ? state.player2.first_name || state.player2.username : "Kutilmoqda...";
    scoreBoard.innerHTML = `
        <div class="score-side"><b>${p1Name}</b><br>${state.player1_correct} ✅</div>
        <div class="score-vs">VS</div>
        <div class="score-side"><b>${p2Name}</b><br>${state.player2_correct} ✅</div>
    `;

    if (state.status === "waiting_for_opponent") {
        document.getElementById("waitingBox").classList.remove("hidden");
        document.getElementById("shareLink").textContent = `${location.origin}/human-duel?code=${inviteCode}`;
        return;
    }
    document.getElementById("waitingBox").classList.add("hidden");

    if (state.status === "finished") {
        clearInterval(pollTimer);
        document.getElementById("questionCard").classList.add("hidden");
        const banner = document.getElementById("finishBanner");
        banner.classList.remove("hidden");
        if (!state.winner_telegram_id) {
            banner.className = "result-banner";
            banner.textContent = "🤝 Durang! Ikkalangiz ham teng ball to'pladingiz.";
        } else if (state.winner_telegram_id === currentUser.id) {
            banner.className = "result-banner correct";
            banner.textContent = "🎉 Siz g'olib chiqdingiz! Reyting balingiz oshdi.";
        } else {
            banner.className = "result-banner wrong";
            banner.textContent = "😔 Siz yutqazdingiz. Keyingi safar omad!";
        }
        return;
    }

    if (state.current_index === lastRenderedIndex) return;
    lastRenderedIndex = state.current_index;
    answered = false;

    const card = document.getElementById("questionCard");
    card.classList.remove("hidden");
    document.getElementById("resultBanner").className = "result-banner hidden";

    const isMyTurn = state.current_turn_telegram_id === currentUser.id;

    if (!isMyTurn || !state.current_question) {
        card.innerHTML = `<div class="question-loading">⏳ Raqib javob bermoqda...</div>`;
        return;
    }

    const q = state.current_question;
    const options = [
        ["A", q.option_a],
        ["B", q.option_b],
        ["C", q.option_c],
        ["D", q.option_d],
    ];
    card.innerHTML = `
        <div class="question-text">${q.text}</div>
        <div>
            ${options
                .map(([key, text]) => `<button class="option-btn" data-key="${key}" onclick="selectAnswer('${key}', ${q.id})">${key}) ${text}</button>`)
                .join("")}
        </div>
    `;
}

async function selectAnswer(key, questionId) {
    if (answered) return;
    answered = true;
    document.querySelectorAll(".option-btn").forEach((b) => (b.disabled = true));

    const res = await fetch("/api/duel/human/answer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ telegram_id: currentUser.id, invite_code: inviteCode, question_id: questionId, selected_option: key }),
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
        banner.textContent = `❌ Noto'g'ri javob`;
    }

    setTimeout(pollState, 1200);
}

(async function init() {
    await ensureProfile();
    if (inviteCode) {
        await joinDuel();
    }
})();
