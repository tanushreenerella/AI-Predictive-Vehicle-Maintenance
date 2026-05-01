from fastapi import FastAPI, Request
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

ALLOWED_ORIGINS = ["http://localhost:3000", "https://ai-predictive-vehicle-maintenance.vercel.app"]

app = FastAPI(title="Predictive Maintenance API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    origin = request.headers.get("origin", "")
    headers = {}
    if origin in ALLOWED_ORIGINS:
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
        headers=headers,
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

