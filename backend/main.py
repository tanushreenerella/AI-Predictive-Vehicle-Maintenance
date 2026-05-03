import re
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.routes.vehicles import router as vehicle_router
from backend.routes.analysis import router as analysis_router
from backend.base import Base
from backend.session import engine
from backend.routes.dashboard import router as dashboard_router
from backend.routes.vehicle_health import router as vehicle_health_router
from backend.routes.alerts import router as alerts_router
from backend.routes.auth import router as auth_router
from backend.routes.scheduling import router as scheduling_router
from backend.routes.agent_chat import router as agent_chat_router
from backend.routes.predict import router as predict_router
from backend.routes.analyze_route import router as analyze_router
Base.metadata.create_all(bind=engine)

_ORIGIN_RE = re.compile(r"https?://(localhost(:\d+)?|[a-zA-Z0-9-]+\.vercel\.app)")

app = FastAPI(title="Predictive Maintenance API")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=_ORIGIN_RE.pattern,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _cors_headers(request: Request) -> dict:
    origin = request.headers.get("origin", "")
    if _ORIGIN_RE.fullmatch(origin):
        return {"Access-Control-Allow-Origin": origin, "Access-Control-Allow-Credentials": "true"}
    return {}

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=_cors_headers(request),
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
        headers=_cors_headers(request),
    )

@app.get("/")
def root():
    return {"status": "Backend running"}

app.include_router(vehicle_router)
app.include_router(analysis_router)
app.include_router(dashboard_router)
app.include_router(vehicle_health_router)
app.include_router(alerts_router)
app.include_router(auth_router)
app.include_router(scheduling_router)
app.include_router(agent_chat_router)
app.include_router(predict_router)
app.include_router(analyze_router)

