// Bilim Jangi — Do'kon katalogi

const tg = window.Telegram ? window.Telegram.WebApp : null;
if (tg) { tg.ready(); tg.expand(); }

function getTelegramUser() {
    if (tg && tg.initDataUnsafe && tg.initDataUnsafe.user) return tg.initDataUnsafe.user;
    return { id: 999999999, username: "test_user", first_name: "Mehmon" };
}

const currentUser = getTelegramUser();
let activeCatalog = "";

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

function selectCatalog(cat) {
    activeCatalog = cat;
    document.querySelectorAll(".cat-chip").forEach((c) => c.classList.toggle("active", c.dataset.cat === cat));
    loadProducts();
}

function priceLabel(p) {
    return p.price_type === "money" ? `${Number(p.price_amount).toFixed(0)} so'm` : `${Number(p.price_amount).toFixed(2)} 🪙`;
}

async function loadProducts() {
    const container = document.getElementById("productsList");
    container.innerHTML = `<div class="mission-skeleton"></div>`;

    if (activeCatalog === "") {
        const res = await fetch(`/api/shop/products?telegram_id=${currentUser.id}`);
        const data = await res.json();
        renderProducts(data.products);
        return;
    }

    const res = await fetch(`/api/shop/products?telegram_id=${currentUser.id}&catalog=${activeCatalog}`);
    const data = await res.json();

    if (activeCatalog === "seller" && !data.products.length) {
        container.innerHTML = `<div class="product-empty">🔒 Bu katalogni ko'rish uchun faol Vaucher kerak.<br><br><button class="mini-btn primary" onclick="selectCatalog('vaucher')">🎟️ Vaucher olish</button></div>`;
        return;
    }

    renderProducts(data.products);
}

function renderProducts(products) {
    const container = document.getElementById("productsList");
    if (!products.length) {
        container.innerHTML = `<div class="product-empty">Bu katalogda hozircha mahsulot yo'q.</div>`;
        return;
    }
    container.innerHTML = products
        .map((p) => {
            const img = p.image_url || "https://placehold.co/300x200/2563EB/fff?text=B";
            const priceClass = p.price_type === "money" ? "money" : "";
            return `
                <div class="product-card" onclick="location.href='/shop/product?id=${p.id}'">
                    <img class="product-image" src="${img}">
                    <div class="product-body">
                        <div class="product-name">${p.name}</div>
                        <div class="product-price ${priceClass}">${priceLabel(p)}</div>
                    </div>
                </div>
            `;
        })
        .join("");
}

(async function init() {
    await ensureProfile();
    await loadProducts();
})();
