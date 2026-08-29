"""
Bilim Jangi — 3-bosqich: Premium tariflar va Vaucher rejalari uchun
boshlang'ich mahsulotlar (Product jadvaliga birinchi ishga tushishda yoziladi).
Narx va bonuslarni admin panel orqali keyinchalik o'zgartirish mumkin.
"""

PREMIUM_TIERS: list[dict] = [
    {
        "catalog": "premium", "name": "Premium 1", "description": "Barcha mukofotlarga +10% bonus",
        "price_type": "money", "price_amount": 15000, "premium_tier": 1, "bonus_percent": 10,
    },
    {
        "catalog": "premium", "name": "Premium 2", "description": "Barcha mukofotlarga +30% bonus",
        "price_type": "money", "price_amount": 35000, "premium_tier": 2, "bonus_percent": 30,
    },
    {
        "catalog": "premium", "name": "Premium 3", "description": "Barcha mukofotlarga +50% bonus",
        "price_type": "money", "price_amount": 60000, "premium_tier": 3, "bonus_percent": 50,
    },
    {
        "catalog": "premium", "name": "Premium 4", "description": "Barcha mukofotlarga +80% bonus",
        "price_type": "money", "price_amount": 100000, "premium_tier": 4, "bonus_percent": 80,
    },
]

VOUCHER_PLANS: list[dict] = [
    {
        "catalog": "vaucher", "name": "Vaucher — 3 kun", "description": "3 kun davomida 15 ta mahsulotni ko'rish imkoniyati",
        "price_type": "coin", "price_amount": 5, "voucher_days": 3, "voucher_product_count": 15, "is_vip_plus": False,
    },
    {
        "catalog": "vaucher", "name": "Vaucher — 7 kun", "description": "7 kun davomida 60 ta mahsulotni ko'rish imkoniyati",
        "price_type": "coin", "price_amount": 15, "voucher_days": 7, "voucher_product_count": 60, "is_vip_plus": False,
    },
    {
        "catalog": "vaucher", "name": "Vaucher — 30 kun", "description": "30 kun davomida 200 ta mahsulotni ko'rish imkoniyati",
        "price_type": "coin", "price_amount": 40, "voucher_days": 30, "voucher_product_count": 200, "is_vip_plus": False,
    },
    {
        "catalog": "vaucher", "name": "VIP Plus — 30 kun",
        "description": "30 kun: 200 ta oddiy + 15 ta pullik mahsulotni ko'rish imkoniyati",
        "price_type": "money", "price_amount": 45000, "voucher_days": 30,
        "voucher_product_count": 200, "voucher_paid_count": 15, "is_vip_plus": True,
    },
]
