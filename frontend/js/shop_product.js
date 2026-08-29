// Bilim Jangi — Mahsulot tafsilotlari va sotib olish oqimi

const tg = window.Telegram ? window.Telegram.WebApp : null;
if (tg) { tg.ready(); tg.expand(); }

function getTelegramUser() {
    if (tg && tg.initDataUnsafe && tg.initDataUnsafe.user) return tg.initDataUnsafe.user;
    return { id: 999999999, username: "test_user", first_name: "Mehmon" };
}

const currentUser = getTelegramUser();
const productId = new URLSearchParams(location.search).get("id");
let statusPoll = null;

function showToast(text) {
    const toast = document.getElementById("toast");
    toast.textContent = text;
    toast.classList.add("show");
    setTimeout(() => toast.classList.remove("show"), 2500);
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

const CATALOG_LABELS = {
    premium: "👑 Premium", vaucher: "🎟️ Vaucher", frame: "🖼️ Ramka",
    nick_decor: "✨ Nik bezagi", background: "🏞️ Orqa fon", badge: "🏅 Badge", seller: "🏪 Sotuvchi mahsuloti",
};

async function loadProduct() {
    if (!productId) {
        document.getElementById("productBox").innerHTML = `<div class="mission-desc">Mahsulot ID topilmadi.</div>`;
        return;
    }
    const res = await fetch(`/api/shop/product/${productId}`);
    if (!res.ok) {
        document.getElementById("productBox").innerHTML = `<div class="mission-desc">Mahsulot topilmadi.</div>`;
        return;
    }
    const p = await res.json();
    renderProduct(p);
}

function renderProduct(p) {
    const img = p.image_url || "https://placehold.co/600x400/2563EB/fff?text=B";
    const priceText = p.price_type === "money" ? `${Number(p.price_amount).toFixed(0)} so'm` : `${Number(p.price_amount).toFixed(2)} 🪙`;

    let extra = "";
    if (p.catalog === "premium") {
        extra = `<div class="mission-desc">Bonus: +${p.bonus_percent}% barcha mukofotlarga</div>`;
    } else if (p.catalog === "vaucher") {
        extra = `<div class="mission-desc">${p.voucher_days} kun · ${p.voucher_product_count} ta mahsulot${p.is_vip_plus ? ` + ${p.voucher_paid_count} ta pullik mahsulot` : ""}</div>`;
    }

    document.getElementById("productBox").innerHTML = `
        <img class="product-detail-image" src="${img}">
        <div class="mini-badge" style="margin-bottom:10px; display:inline-block">${CATALOG_LABELS[p.catalog] || p.catalog}</div>
        <div class="product-detail-title">${p.name}</div>
        <div class="product-detail-desc">${p.description || "Tavsif mavjud emas."}</div>
        ${extra}
        <div class="product-detail-price">${priceText}</div>
        <button class="next-btn" onclick="purchase(${p.price_type === 'money'})">🛒 Sotib olish</button>
        <div style="display:flex; gap:8px; margin-top:10px">
            <button class="mini-btn" style="flex:1; padding:10px" onclick="showToast('Do\\'stga sovg\\'a qilish — Sklad orqali amalga oshiring 🎁')">🎁 Do'stga sovg'a</button>
        </div>
    `;
}

async function purchase(isMoney) {
    const res = await fetch("/api/shop/purchase", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ telegram_id: currentUser.id, product_id: Number(productId) }),
    });
    const data = await res.json();
    if (!res.ok) {
        showToast(data.detail || "Xatolik");
        return;
    }

    if (!isMoney) {
        showToast("✅ Xarid muvaffaqiyatli!");
        document.getElementById("bCoin").textContent = Number(data.new_b_coin).toFixed(2);
        return;
    }

    showPaymentBox(data);
}

function showPaymentBox(order) {
    const box = document.getElementById("paymentBox");
    box.classList.remove("hidden");
    box.innerHTML = `
        <div class="payment-card-box">
            <div style="font-size:13px; opacity:.85">To'lov uchun karta</div>
            <div class="payment-card-number">${order.card_number}</div>
            <div class="payment-card-holder">${order.card_holder}</div>
            <div style="margin-top:10px; font-size:18px; font-weight:800">${Number(order.amount).toFixed(0)} so'm</div>
        </div>
        <div class="mission-desc">${order.instructions}</div>
        <div class="payment-timer" id="paymentTimer"></div>
        <div class="mission-desc" style="margin-top:10px; text-align:center" id="paymentStatusText">⏳ Screenshot kutilmoqda...</div>
    `;
    startCountdown(order.expires_at);
    statusPoll = setInterval(() => pollPaymentStatus(order.order_id), 4000);
}

function startCountdown(expiresAtIso) {
    const expiresAt = new Date(expiresAtIso).getTime();
    const timerEl = document.getElementById("paymentTimer");
    const tick = () => {
        const diff = expiresAt - Date.now();
        if (diff <= 0) {
            timerEl.textContent = "⏰ Vaqt tugadi";
            clearInterval(statusPoll);
            return;
        }
        const mins = Math.floor(diff / 60000);
        const secs = Math.floor((diff % 60000) / 1000);
        timerEl.textContent = `⏰ Qolgan vaqt: ${mins}:${String(secs).padStart(2, "0")}`;
    };
    tick();
    setInterval(tick, 1000);
}

async function pollPaymentStatus(orderId) {
    const res = await fetch(`/api/payment/status/${orderId}?telegram_id=${currentUser.id}`);
    if (!res.ok) return;
    const status = await res.json();
    const statusText = document.getElementById("paymentStatusText");
    if (!statusText) return;

    if (status.status === "pending_approval") {
        statusText.textContent = "🔎 Screenshot qabul qilindi, tasdiqlanishi kutilmoqda...";
    } else if (status.status === "approved") {
        statusText.textContent = "🎉 To'lov tasdiqlandi! Mahsulot hisobingizga qo'shildi.";
        clearInterval(statusPoll);
        await ensureProfile();
    } else if (status.status === "rejected") {
        statusText.textContent = "❌ To'lov rad etildi.";
        clearInterval(statusPoll);
    } else if (status.status === "expired") {
        statusText.textContent = "⏰ Vaqt tugadi, buyurtma bekor qilindi.";
        clearInterval(statusPoll);
    }
}

(async function init() {
    await ensureProfile();
    await loadProduct();
})();
