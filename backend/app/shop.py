from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.config import settings
from app.database import get_db

router = APIRouter(prefix="/api/shop", tags=["shop"])


@router.get("/products", response_model=schemas.ProductListOut)
async def list_products(telegram_id: int, catalog: str | None = None, db: AsyncSession = Depends(get_db)):
    user = await crud.get_or_create_user(db, telegram_id=telegram_id)
    products = await crud.list_products(db, catalog, user)
    return schemas.ProductListOut(products=[schemas.ProductOut.model_validate(p) for p in products])


@router.get("/product/{product_id}", response_model=schemas.ProductOut)
async def get_single_product(product_id: int, db: AsyncSession = Depends(get_db)):
    product = await crud.get_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")
    return schemas.ProductOut.model_validate(product)


@router.post("/products/submit", response_model=schemas.ProductOut)
async def submit_product(payload: schemas.ProductSubmitRequest, db: AsyncSession = Depends(get_db)):
    user = await crud.get_or_create_user(db, telegram_id=payload.telegram_id)
    product, message = await crud.submit_seller_product(
        db, user, payload.catalog, payload.name, payload.description, payload.image_url, payload.price_amount
    )
    if product is None:
        raise HTTPException(status_code=400, detail=message)
    return schemas.ProductOut.model_validate(product)


@router.post("/purchase")
async def purchase(payload: schemas.PurchaseRequest, db: AsyncSession = Depends(get_db)):
    user = await crud.get_or_create_user(db, telegram_id=payload.telegram_id)
    product = await crud.get_product(db, payload.product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")

    if product.price_type == "coin":
        ok, message = await crud.purchase_with_coin(db, user, product)
        if not ok:
            raise HTTPException(status_code=400, detail=message)
        return schemas.PurchaseCoinResult(detail=message, new_b_coin=float(user.b_coin))
    else:
        order, message = await crud.create_payment_order(db, user, product)
        if order is None:
            raise HTTPException(status_code=400, detail=message)
        return schemas.PurchaseMoneyResult(
            order_id=order.id,
            card_number=settings.PAYMENT_CARD_NUMBER,
            card_holder=settings.PAYMENT_CARD_HOLDER,
            amount=float(order.amount),
            expires_at=order.expires_at.isoformat(),
            instructions=(
                f"Ko'rsatilgan kartaga {order.amount} so'm o'tkazing, so'ng to'lov skrinshotini "
                f"to'g'ridan-to'g'ri Bilim Jangi botiga (shu Telegram chatga) yuboring. "
                f"Tasdiqlash uchun {settings.PAYMENT_TIMEOUT_MINUTES} daqiqa vaqtingiz bor."
            ),
        )


@router.get("/inventory/{telegram_id}", response_model=schemas.InventoryListOut)
async def get_inventory(telegram_id: int, db: AsyncSession = Depends(get_db)):
    user = await crud.get_or_create_user(db, telegram_id=telegram_id)
    rows = await crud.get_user_inventory(db, user)
    items = [
        schemas.InventoryItemOut(
            id=item.id, product=schemas.ProductOut.model_validate(product),
            status=item.status, acquired_at=item.acquired_at.isoformat(),
        )
        for item, product in rows
    ]
    return schemas.InventoryListOut(items=items)


@router.post("/inventory/apply")
async def apply_item(payload: schemas.ApplyOrRefundRequest, db: AsyncSession = Depends(get_db)):
    user = await crud.get_or_create_user(db, telegram_id=payload.telegram_id)
    ok, message = await crud.apply_inventory_item(db, user, payload.inventory_item_id)
    if not ok:
        raise HTTPException(status_code=400, detail=message)
    return {"detail": message}


@router.post("/inventory/refund")
async def refund_item(payload: schemas.ApplyOrRefundRequest, db: AsyncSession = Depends(get_db)):
    user = await crud.get_or_create_user(db, telegram_id=payload.telegram_id)
    ok, message = await crud.refund_inventory_item(db, user, payload.inventory_item_id)
    if not ok:
        raise HTTPException(status_code=400, detail=message)
    return {"detail": message, "new_b_coin": float(user.b_coin)}
