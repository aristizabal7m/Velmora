from fastapi import APIRouter

from velmora.api.v1.routers import auth, content, investments, lessons

router = APIRouter()
router.include_router(investments.router)
router.include_router(content.router)
router.include_router(lessons.router)
router.include_router(auth.router)
