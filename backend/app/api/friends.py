from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/api/friends", tags=["friends"])


@router.get("/list/{telegram_id}", response_model=list[schemas.UserBrief])
async def friends_list(telegram_id: int, db: AsyncSession = Depends(get_db)):
    user = await crud.get_or_create_user(db, telegram_id=telegram_id)
    friends = await crud.get_friends_list(db, user)
    return [schemas.UserBrief.model_validate(f) for f in friends]


@router.get("/incoming/{telegram_id}", response_model=list[schemas.FriendRequestOut])
async def incoming_requests(telegram_id: int, db: AsyncSession = Depends(get_db)):
    user = await crud.get_or_create_user(db, telegram_id=telegram_id)
    rows = await crud.get_incoming_requests(db, user)
    return [
        schemas.FriendRequestOut(
            request_id=req.id, user=schemas.UserBrief.model_validate(u), created_at=req.created_at.isoformat()
        )
        for req, u in rows
    ]


@router.get("/outgoing/{telegram_id}", response_model=list[schemas.FriendRequestOut])
async def outgoing_requests(telegram_id: int, db: AsyncSession = Depends(get_db)):
    user = await crud.get_or_create_user(db, telegram_id=telegram_id)
    rows = await crud.get_outgoing_requests(db, user)
    return [
        schemas.FriendRequestOut(
            request_id=req.id, user=schemas.UserBrief.model_validate(u), created_at=req.created_at.isoformat()
        )
        for req, u in rows
    ]


@router.get("/search", response_model=schemas.SearchUsersResult)
async def search(telegram_id: int, q: str, db: AsyncSession = Depends(get_db)):
    user = await crud.get_or_create_user(db, telegram_id=telegram_id)
    users = await crud.search_users(db, q, exclude_telegram_id=user.telegram_id)
    return schemas.SearchUsersResult(users=[schemas.UserBrief.model_validate(u) for u in users])


@router.post("/request")
async def send_request(payload: schemas.SendFriendRequest, db: AsyncSession = Depends(get_db)):
    user = await crud.get_or_create_user(db, telegram_id=payload.telegram_id)
    ok, message = await crud.send_friend_request(db, user, payload.target)
    if not ok:
        raise HTTPException(status_code=400, detail=message)
    return {"detail": message}


@router.post("/respond")
async def respond_request(payload: schemas.RespondFriendRequest, db: AsyncSession = Depends(get_db)):
    user = await crud.get_or_create_user(db, telegram_id=payload.telegram_id)
    ok, message = await crud.respond_friend_request(db, user, payload.request_id, payload.action)
    if not ok:
        raise HTTPException(status_code=400, detail=message)
    return {"detail": message}


@router.post("/gift")
async def gift(payload: schemas.GiftCoinRequest, db: AsyncSession = Depends(get_db)):
    user = await crud.get_or_create_user(db, telegram_id=payload.telegram_id)
    friend = await crud.get_user_by_telegram_id(db, payload.friend_telegram_id)
    if friend is None:
        raise HTTPException(status_code=404, detail="Do'st topilmadi")
    friends = await crud.get_friends_list(db, user)
    if friend.id not in {f.id for f in friends}:
        raise HTTPException(status_code=400, detail="Faqat do'stlaringizga sovg'a yubora olasiz")
    ok, message = await crud.gift_coin(db, user, friend, payload.amount)
    if not ok:
        raise HTTPException(status_code=400, detail=message)
    return {"detail": message, "new_b_coin": float(user.b_coin)}
