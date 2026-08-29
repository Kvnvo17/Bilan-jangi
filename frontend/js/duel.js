// Bilim Jangi — 1v1 Bot bilan duel logikasi

const tg = window.Telegram ? window.Telegram.WebApp : null;
if (tg) {
    tg.ready();
    tg.expand();
}

function getTelegramUser() {
    if (tg && tg.initDataUnsafe && tg.initDataUnsafe.user) {
        return tg.initDataUnsafe.user;
    }
    return { id: 999999999, username: "test_user", first_name: "Mehmon" };
}

const currentUser = getTelegramUser();
let currentQuestion = null;
let answered = false;

function showToast(text) {
    const toast = document.getElementById("toast");
    toast.textContent = text;
    toast.classList.add("show");
    setTimeout(() => toast.classList.remove("show"), 2200);
}

function showComingSoon(featureName) {
    showToast(`${featureName} — tez orada qo'shiladi 🚧`);
}

async function refreshCoinBadge() {
    const res = await fetch(`/api/profile/${currentUser.id}`);
    const profile = await res.json();
    document.getElementById("bCoin").textContent = Number(profile.b_coin).toFixed(2);
}

async function loadNextQuestion() {
    answered = false;
    document.getElementById("resultBanner").className = "result-banner hidden";
    document.getElementById("nextBtn").className = "next-btn hidden";

    const card = document.getElementById("questionCard");
    card.innerHTML = `<div class="question-loading">Savol yuklanmoqda...</div>`;

    // Foydalanuvchini avval sinxronlaymiz (agar birinchi marta kirgan bo'lsa)
    await fetch("/api/profile/sync", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            telegram_id: currentUser.id,
            username: currentUser.username || null,
            first_name: currentUser.first_name || "Foydalanuvchi",
        }),
    });

    const res = await fetch("/api/duel/bot/question");
    if (!res.ok) {
        card.innerHTML = `<div class="question-loading">Savollar bazasi bo'sh. Admin bilan bog'laning.</div>`;
        return;
    }
    currentQuestion = await res.json();
    renderQuestion(currentQuestion);
    await refreshCoinBadge();
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
        <div id="optionsWrap">
            ${options
                .map(
                    ([key, text]) =>
                        `<button class="option-btn" data-key="${key}" onclick="selectAnswer('${key}')">${key}) ${text}</button>`
                )
                .join("")}
        </div>
    `;
}

async function selectAnswer(selectedKey) {
    if (answered) return;
    answered = true;

    const res = await fetch("/api/duel/bot/answer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            telegram_id: currentUser.id,
            question_id: currentQuestion.id,
            selected_option: selectedKey,
        }),
    });
    const result = await res.json();

    document.querySelectorAll(".option-btn").forEach((btn) => {
        btn.disabled = true;
        const key = btn.getAttribute("data-key");
        if (key === result.correct_option) {
            btn.classList.add("correct");
        } else if (key === selectedKey) {
            btn.classList.add("wrong");
        }
    });

    const banner = document.getElementById("resultBanner");
    if (result.is_correct) {
        banner.textContent = `✅ To'g'ri javob! +${Number(result.coin_change).toFixed(2)} B Coin`;
        banner.className = "result-banner correct";
    } else {
        banner.textContent = `❌ Noto'g'ri. To'g'ri javob: ${result.correct_option}`;
        banner.className = "result-banner wrong";
    }

    if (result.leveled_up) {
        showToast(`🎉 Tabriklaymiz! Siz ${result.new_level}-levelga o'tdingiz!`);
    }

    document.getElementById("bCoin").textContent = Number(result.new_b_coin).toFixed(2);
    document.getElementById("nextBtn").className = "next-btn";
}

loadNextQuestion();
