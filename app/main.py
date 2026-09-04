from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.orders import router as order_router
from app.api.products import router as product_router
from app.api.users import router as user_router

app = FastAPI(title="Multi-Tier Pyramid Marketplace Engine", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(product_router)
app.include_router(order_router)


@app.get("/health", tags=["System"])
async def health():
    return {"status": "ok"}
