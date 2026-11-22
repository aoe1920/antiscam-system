import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.api.v1.endpoints.verification import router as verification_router
from backend.app.api.v1.endpoints.auth import router as auth_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = (time.perf_counter() - start_time) * 1000.0
    response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"
    return response

app.include_router(verification_router, prefix=settings.API_V1_STR)
app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "antiscam-backend",
        "version": "1.0.0"
    }

@app.get("/api/v1/mock/verify-demo", tags=["Mock"])
async def mock_verify_demo(account_number: str = "1029384756"):
    return {
        "success": True,
        "data": {
            "entity_value": account_number,
            "entity_type": "bank_account",
            "credit_score": 18.5,
            "risk_level": "CRITICAL",
            "penalty_breakdown": {
                "graph_penalty": 40.0,
                "payment_penalty": 25.0,
                "psychology_penalty": 16.5,
                "image_penalty": 0.0
            },
            "what_if_scenarios": [
                "Bước 1: Đối tượng tạo áp lực khan hiếm phòng trọ, yêu cầu chuyển cọc 1 triệu trong 15 phút.",
                "Bước 2: Sau khi nạn nhân chuyển khoản, đối tượng cắt liên lạc hoặc yêu cầu nạp thêm tiền làm hợp đồng.",
                "Bước 3: Chặn số điện thoại, khóa tài khoản Facebook/Zalo và xóa toàn bộ tin nhắn."
            ]
        }
    }
