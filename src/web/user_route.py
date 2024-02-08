from fastapi import APIRouter

router = APIRouter(prefix="/users")


@router.get("")
async def hi():
    return "Hello there"
