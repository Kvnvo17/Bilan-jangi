// Bilim Jangi — Sklad (inventar)

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

const STATUS_LABELS = { owned: "📥 Sotib olingan", applied: "✅ Qo'llangan", refunded: "↩️ Qaytarilgan" };

async function loadInventory() {
    const container = document.getElementById("inventoryList");
    container.innerHTML = `<div class="mission-skeleton"></div>`;
    const res = await fetch(`/api/shop/inventory/${currentUser.id}`);
    const data = await res.json();
    if (!data.items.length) {
        container.innerHTML = `<div class="mission-desc">Skladingiz hozircha bo'sh. <a href="/shop">Do'kondan</a> nimadir sotib oling!</div>`;
        return;
    }
    container.innerHTML = data.items
        .map((item) => {
            const p = item.product;
            const img = p.image_url || "https://placehold.co/100x100/2563EB/fff?text=B";
            const canAct = item.status === "owned";
            return `
                <div class="inventory-card">
                    <img class="inventory-img" src="${img}">
                    <div class="inventory-info">
                        <div class="inventory-name">${p.name}</div>
                        <div class="inventory-status">${STATUS_LABELS[item.status] || item.status} · narxi ${Number(p.price_amount).toFixed(2)}</div>
                    </div>
                    ${
                        canAct
                            ? `<div class="inventory-actions">
                                <button class="mini-btn primary" onclick="applyItem(${item.id})">✅ Qo'llash</button>
                                <button class="mini-btn danger" onclick="refundItem(${item.id})">↩️ 50% qaytarish</button>
                               </div>`
                            : ""
                    }
                </div>
            `;
        })
        .join("");
}

async function applyItem(id) {
    const res = await fetch("/api/shop/inventory/apply", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ telegram_id: currentUser.id, inventory_item_id: id }),
    });
    const data = await res.json();
    showToast(res.ok ? "✅ Qo'llanildi" : data.detail || "Xatolik");
    loadInventory();
}

async function refundItem(id) {
    if (!confirm("Mahsulotni qaytarib, narxining 50% ini B Coin ko'rinishida olmoqchimisiz?")) return;
    const res = await fetch("/api/shop/inventory/refund", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ telegram_id: currentUser.id, inventory_item_id: id }),
    });
    const data = await res.json();
    if (!res.ok) {
        showToast(data.detail || "Xatolik");
        return;
    }
    showToast(data.detail);
    document.getElementById("bCoin").textContent = Number(data.new_b_coin).toFixed(2);
    loadInventory();
}

(async function init() {
    await ensureProfile();
    await loadInventory();
})();
