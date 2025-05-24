from fastapi import APIRouter
from app.api import api_user, api_message

router = APIRouter()
router.include_router(api_user.router)
router.include_router(api_message.router)
