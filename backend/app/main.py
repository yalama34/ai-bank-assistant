from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import analytics, approval, generation, letters, validation

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(letters.router)
app.include_router(generation.router)
app.include_router(validation.router)
app.include_router(approval.router)
app.include_router(analytics.router)


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "status": "running"
    }


@app.get("/health")
async def health():
    """Проверка здоровья сервиса"""
    return {
        "status": "healthy",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)