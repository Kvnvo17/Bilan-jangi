// Bilim Jangi — Mahsulot joylash (sotuvchi)

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

async function submitProduct() {
    const catalog = document.getElementById("pCatalog").value;
    const name = document.getElementById("pName").value.trim();
    const description = document.getElementById("pDesc").value.trim();
    const image_url = document.getElementById("pImage").value.trim() || null;
    const price_amount = Number(document.getElementById("pPrice").value);

    if (!name || !price_amount) {
        showToast("Nomi va narxini kiriting");
        return;
    }

    const res = await fetch("/api/shop/products/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ telegram_id: currentUser.id, catalog, name, description, image_url, price_amount }),
    });
    const data = await res.json();
    if (!res.ok) {
        showToast(data.detail || "Xatolik");
        return;
    }
    showToast("✅ Yuborildi — admin tasdig'ini kutmoqda");
    ["pName", "pDesc", "pImage", "pPrice"].forEach((id) => (document.getElementById(id).value = ""));
}
