from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.database import get_db

router = APIRouter(prefix="/api/payment", tags=["payment"])


@router.get("/status/{order_id}", response_model=schemas.PaymentStatusOut)
async def get_status(order_id: int, telegram_id: int, db: AsyncSession = Depends(get_db)):
    order = await db.get(models.PaymentOrder, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")
    user = await crud.get_user_by_telegram_id(db, telegram_id)
    if user is None or order.user_id != user.id:
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")
    product = await crud.get_product(db, order.product_id)
    return schemas.PaymentStatusOut(
        order_id=order.id,
        status=order.status,
        product_name=product.name if product else "—",
        amount=float(order.amount),
        expires_at=order.expires_at.isoformat(),
    )
